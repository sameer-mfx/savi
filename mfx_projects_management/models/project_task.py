from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import io
import base64
import xlsxwriter

class ProjectTask(models.Model):
    _inherit = 'project.task'

    audio_task_items_ids = fields.One2many(comodel_name='audio.task.items', inverse_name='task_id', string='Audio Task Items')
    video_task_items_ids = fields.One2many(comodel_name='video.task.items', inverse_name='task_id', string='Video Task Items')
    video_conferencing_task_items_ids = fields.One2many(comodel_name='video.conferencing.task.items', inverse_name='task_id', string='Video Conferencing Task Items')
    controller_task_items_ids = fields.One2many(comodel_name='controller.task.items', inverse_name='task_id', string='Controller Task Items')
    switching_task_items_ids = fields.One2many(comodel_name='switching.task.items', inverse_name='task_id', string='Switching Task Items')
    accessories_task_items_ids = fields.One2many(comodel_name='accessories.task.items', inverse_name='task_id', string='Accessories Task Items')
    task_items_summary_ids = fields.One2many(comodel_name='task.items.summary', inverse_name='task_id', string='Task Items Summary')
    can_add_products = fields.Boolean(string='Can Add Products', compute='_compute_can_add_products')
    control_page_visibility = fields.Boolean(string='Control Page Visibility', compute='_compute_control_page_visibility')

    @api.depends('stage_id.can_add_products_to_so')
    def _compute_can_add_products(self):
        for task in self:
            task.can_add_products = bool(task.stage_id and task.stage_id.can_add_products_to_so)

    @api.depends('stage_id', 'stage_id.sequence')
    def _compute_control_page_visibility(self):
        for task in self:
            add_products_stage = task.project_id.type_ids.filtered('can_add_products_to_so')
            if add_products_stage and task.stage_id:
                task.control_page_visibility = task.stage_id.sequence < add_products_stage.sequence
            elif task.stage_id:
                task.control_page_visibility = True
            else:
                task.control_page_visibility = False

    def action_export_items_summary_excel(self):
        """Export task items summary to Excel"""
        if len(self) == 1:
            return self.env['task.items.summary'].action_export_excel(task_id=self.id)
        else:
            # Handle multiple tasks - export all items from selected tasks
            # Check if all tasks are from the same project
            project_ids = self.mapped('project_id.id')
            if len(set(project_ids)) == 1:  # All tasks from same project
                project_name = self[0].project_id.name
                return self.env['task.items.summary'].action_export_excel_with_project_header(
                    task_ids=self.ids, 
                    project_name=project_name
                )
            else:
                return self.env['task.items.summary'].action_export_excel_multiple_tasks(task_ids=self.ids)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def action_export_project_items_summary_excel(self):
        """Export all task items summary for a project to Excel"""
        # Get all tasks in this project
        project_tasks = self.env['project.task'].search([('project_id', '=', self.id)])
        if not project_tasks:
            raise ValidationError(_("No tasks found in this project."))
        
        return self.env['task.items.summary'].action_export_excel_with_project_header(
            task_ids=project_tasks.ids, 
            project_name=self.name
        )

class AudioTaskItems(models.Model):
    _name = 'audio.task.items'

    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    is_added_in_so = fields.Boolean(string='Is Added In SO', default=False)
    task_id = fields.Many2one(comodel_name='project.task', string='Task', ondelete='cascade')
    is_tracked = fields.Boolean(string='Tracked', compute='_compute_is_tracked', store=True, default=False)
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers', copy=False)
    sale_line_id = fields.Many2one(comodel_name='sale.order.line', string='Sale Line')
    summary_item_id = fields.Many2one(comodel_name='task.items.summary', string='Summary Item')

    @api.constrains('quantity', 'unit_price')
    def _update_qty_price(self):
        for rec in self:
            if rec.sale_line_id:
                order = rec.task_id.sale_order_id.sudo()
                was_locked = order.locked
                if was_locked:
                    order.action_unlock()
                rec.sale_line_id.product_uom_qty = rec.quantity
                rec.sale_line_id.price_unit = rec.unit_price
                if was_locked:
                    order.action_lock()

    @api.depends('product_id')
    def _compute_is_tracked(self):
        for record in self:
            record.is_tracked = record.product_id.tracking != 'none'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.unit_price = record.product_id.list_price
                record.product_identification_ids = False

    @api.constrains('product_id', 'task_id')
    def _check_duplicate_products(self):
        for record in self:
            if record.task_id and record.product_id:
                duplicates = record.task_id.audio_task_items_ids.filtered(lambda r: r.product_id == record.product_id and r.id != record.id)
                if duplicates:
                    raise ValidationError(_("You cannot add the same product (%s) more than once in the same task.")% record.product_id.display_name)

    @api.constrains('quantity', 'product_identification_ids', 'is_tracked')
    def _check_quantity_vs_identifications(self):
        """If product is tracked then product_identification_ids must be filled and match quantity."""
        for record in self:
            if record.is_tracked:
                # Must have at least one identification if tracked
                if not record.product_identification_ids:
                    raise ValidationError(_("You must select identification numbers for the tracked product %s.")% record.product_id.display_name)
                # Optional strict rule: quantity = number of identifications
                if len(record.product_identification_ids) != int(record.quantity):
                    raise ValidationError(_("Quantity (%s) must equal the number of identification numbers (%s) for the tracked product %s.")% (record.quantity,len(record.product_identification_ids),record.product_id.display_name))

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AudioTaskItems, self).create(vals_list)
        for vals in res:
            summary_id = self.env['task.items.summary'].create({
                'task_id': vals.task_id.id,
                'product_id': vals.product_id.id,
                'quantity': vals.quantity,
                'unit_price': vals.unit_price,
                'product_identification_ids': vals.product_identification_ids.ids,
                'category': 'audio'
            })
            vals['summary_item_id'] = summary_id.id
        return res

    def write(self, vals):
        res = super(AudioTaskItems, self).write(vals)
        if not vals.get('summary_item_id'):
            for rec in self:
                if rec.summary_item_id:
                    rec.summary_item_id.write({
                        'product_id': rec.product_id.id,
                        'quantity': rec.quantity,
                        'unit_price': rec.unit_price,
                        'product_identification_ids': rec.product_identification_ids.ids,
                    })
        return res

    def unlink(self):
        for rec in self:
            if rec.is_added_in_so:
                raise ValidationError(_("You cannot delete this item as it is already added in the sale order."))
            if rec.summary_item_id:
                rec.summary_item_id.unlink()
        return super(AudioTaskItems, self).unlink()

class VideoTaskItems(models.Model):
    _name = 'video.task.items'

    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    is_added_in_so = fields.Boolean(string='Is Added In SO', default=False)
    task_id = fields.Many2one(comodel_name='project.task', string='Task', ondelete='cascade')
    is_tracked = fields.Boolean(string='Tracked', compute='_compute_is_tracked', store=True, default=False)
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers', copy=False)
    sale_line_id = fields.Many2one(comodel_name='sale.order.line', string='Sale Line')
    summary_item_id = fields.Many2one(comodel_name='task.items.summary', string='Summary Item')

    @api.constrains('quantity', 'unit_price')
    def _update_qty_price(self):
        for rec in self:
            if rec.sale_line_id:
                order = rec.task_id.sale_order_id.sudo()
                was_locked = order.locked
                if was_locked:
                    order.action_unlock()
                rec.sale_line_id.product_uom_qty = rec.quantity
                rec.sale_line_id.price_unit = rec.unit_price
                if was_locked:
                    order.action_lock()

    @api.depends('product_id')
    def _compute_is_tracked(self):
        for record in self:
            record.is_tracked = record.product_id.tracking != 'none'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.unit_price = record.product_id.list_price
                record.product_identification_ids = False

    @api.constrains('product_id', 'task_id')
    def _check_duplicate_products(self):
        for record in self:
            if record.task_id and record.product_id:
                duplicates = record.task_id.video_task_items_ids.filtered(lambda r: r.product_id == record.product_id and r.id != record.id)
                if duplicates:
                    raise ValidationError(_("You cannot add the same product (%s) more than once in the same task.")% record.product_id.display_name)

    @api.constrains('quantity', 'product_identification_ids', 'is_tracked')
    def _check_quantity_vs_identifications(self):
        """If product is tracked then product_identification_ids must be filled and match quantity."""
        for record in self:
            if record.is_tracked:
                # Must have at least one identification if tracked
                if not record.product_identification_ids:
                    raise ValidationError(_("You must select identification numbers for the tracked product %s.") % record.product_id.display_name)
                # Optional strict rule: quantity = number of identifications
                if len(record.product_identification_ids) != int(record.quantity):
                    raise ValidationError(_("Quantity (%s) must equal the number of identification numbers (%s) for the tracked product %s.") % (record.quantity, len(record.product_identification_ids), record.product_id.display_name))

    @api.model_create_multi
    def create(self, vals_list):
        res = super(VideoTaskItems, self).create(vals_list)
        for vals in res:
            summary_id = self.env['task.items.summary'].create({
                'task_id': vals.task_id.id,
                'product_id': vals.product_id.id,
                'quantity': vals.quantity,
                'unit_price': vals.unit_price,
                'product_identification_ids': vals.product_identification_ids.ids,
                'category': 'video'
            })
            vals['summary_item_id'] = summary_id.id
        return res

    def write(self, vals):
        res = super(VideoTaskItems, self).write(vals)
        if not vals.get('summary_item_id'):
            for rec in self:
                if rec.summary_item_id:
                    rec.summary_item_id.write({
                        'product_id': rec.product_id.id,
                        'quantity': rec.quantity,
                        'unit_price': rec.unit_price,
                        'product_identification_ids': rec.product_identification_ids.ids,
                    })
        return res

    def unlink(self):
        for rec in self:
            if rec.is_added_in_so:
                raise ValidationError(_("You cannot delete this item as it is already added in the sale order."))
            if rec.summary_item_id:
                rec.summary_item_id.unlink()
        return super(VideoTaskItems, self).unlink()

class VideoConferencingTaskItems(models.Model):
    _name = 'video.conferencing.task.items'

    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    is_added_in_so = fields.Boolean(string='Is Added In SO', default=False)
    task_id = fields.Many2one(comodel_name='project.task', string='Task', ondelete='cascade')
    is_tracked = fields.Boolean(string='Tracked', compute='_compute_is_tracked', store=True, default=False)
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers', copy=False)
    sale_line_id = fields.Many2one(comodel_name='sale.order.line', string='Sale Line')
    summary_item_id = fields.Many2one(comodel_name='task.items.summary', string='Summary Item')

    @api.constrains('quantity', 'unit_price')
    def _update_qty_price(self):
        for rec in self:
            if rec.sale_line_id:
                order = rec.task_id.sale_order_id.sudo()
                was_locked = order.locked
                if was_locked:
                    order.action_unlock()
                rec.sale_line_id.product_uom_qty = rec.quantity
                rec.sale_line_id.price_unit = rec.unit_price
                if was_locked:
                    order.action_lock()

    @api.depends('product_id')
    def _compute_is_tracked(self):
        for record in self:
            record.is_tracked = record.product_id.tracking != 'none'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.unit_price = record.product_id.list_price
                record.product_identification_ids = False

    @api.constrains('product_id', 'task_id')
    def _check_duplicate_products(self):
        for record in self:
            if record.task_id and record.product_id:
                duplicates = record.task_id.video_conferencing_task_items_ids.filtered(lambda r: r.product_id == record.product_id and r.id != record.id)
                if duplicates:
                    raise ValidationError(_("You cannot add the same product (%s) more than once in the same task.")% record.product_id.display_name)

    @api.constrains('quantity', 'product_identification_ids', 'is_tracked')
    def _check_quantity_vs_identifications(self):
        """If product is tracked then product_identification_ids must be filled and match quantity."""
        for record in self:
            if record.is_tracked:
                # Must have at least one identification if tracked
                if not record.product_identification_ids:
                    raise ValidationError(_("You must select identification numbers for the tracked product %s.") % record.product_id.display_name)
                # Optional strict rule: quantity = number of identifications
                if len(record.product_identification_ids) != int(record.quantity):
                    raise ValidationError(_("Quantity (%s) must equal the number of identification numbers (%s) for the tracked product %s.") % (record.quantity, len(record.product_identification_ids), record.product_id.display_name))

    @api.model_create_multi
    def create(self, vals_list):
        res = super(VideoConferencingTaskItems, self).create(vals_list)
        for vals in res:
            summary_id = self.env['task.items.summary'].create({
                'task_id': vals.task_id.id,
                'product_id': vals.product_id.id,
                'quantity': vals.quantity,
                'unit_price': vals.unit_price,
                'product_identification_ids': vals.product_identification_ids.ids,
                'category': 'video_conferencing'
            })
            vals['summary_item_id'] = summary_id.id
        return res

    def write(self, vals):
        res = super(VideoConferencingTaskItems, self).write(vals)
        if not vals.get('summary_item_id'):
            for rec in self:
                if rec.summary_item_id:
                    rec.summary_item_id.write({
                        'product_id': rec.product_id.id,
                        'quantity': rec.quantity,
                        'unit_price': rec.unit_price,
                        'product_identification_ids': rec.product_identification_ids.ids,
                    })
        return res

    def unlink(self):
        for rec in self:
            if rec.is_added_in_so:
                raise ValidationError(_("You cannot delete this item as it is already added in the sale order."))
            if rec.summary_item_id:
                rec.summary_item_id.unlink()
        return super(VideoConferencingTaskItems, self).unlink()

class ControllerTaskItems(models.Model):
    _name = 'controller.task.items'

    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    is_added_in_so = fields.Boolean(string='Is Added In SO', default=False)
    task_id = fields.Many2one(comodel_name='project.task', string='Task', ondelete='cascade')
    is_tracked = fields.Boolean(string='Tracked', compute='_compute_is_tracked', store=True, default=False)
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers', copy=False)
    sale_line_id = fields.Many2one(comodel_name='sale.order.line', string='Sale Line')
    summary_item_id = fields.Many2one(comodel_name='task.items.summary', string='Summary Item')

    @api.constrains('quantity', 'unit_price')
    def _update_qty_price(self):
        for rec in self:
            if rec.sale_line_id:
                order = rec.task_id.sale_order_id.sudo()
                was_locked = order.locked
                if was_locked:
                    order.action_unlock()
                rec.sale_line_id.product_uom_qty = rec.quantity
                rec.sale_line_id.price_unit = rec.unit_price
                if was_locked:
                    order.action_lock()

    @api.depends('product_id')
    def _compute_is_tracked(self):
        for record in self:
            record.is_tracked = record.product_id.tracking != 'none'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.unit_price = record.product_id.list_price
                record.product_identification_ids = False

    @api.constrains('product_id', 'task_id')
    def _check_duplicate_products(self):
        for record in self:
            if record.task_id and record.product_id:
                duplicates = record.task_id.controller_task_items_ids.filtered(lambda r: r.product_id == record.product_id and r.id != record.id)
                if duplicates:
                    raise ValidationError(_("You cannot add the same product (%s) more than once in the same task.")% record.product_id.display_name)

    @api.constrains('quantity', 'product_identification_ids', 'is_tracked')
    def _check_quantity_vs_identifications(self):
        """If product is tracked then product_identification_ids must be filled and match quantity."""
        for record in self:
            if record.is_tracked:
                # Must have at least one identification if tracked
                if not record.product_identification_ids:
                    raise ValidationError(_("You must select identification numbers for the tracked product %s.") % record.product_id.display_name)
                # Optional strict rule: quantity = number of identifications
                if len(record.product_identification_ids) != int(record.quantity):
                    raise ValidationError(_("Quantity (%s) must equal the number of identification numbers (%s) for the tracked product %s.") % (record.quantity, len(record.product_identification_ids), record.product_id.display_name))

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ControllerTaskItems, self).create(vals_list)
        for vals in res:
            summary_id = self.env['task.items.summary'].create({
                'task_id': vals.task_id.id,
                'product_id': vals.product_id.id,
                'quantity': vals.quantity,
                'unit_price': vals.unit_price,
                'product_identification_ids': vals.product_identification_ids.ids,
                'category': 'controller'
            })
            vals['summary_item_id'] = summary_id.id
        return res

    def write(self, vals):
        res = super(ControllerTaskItems, self).write(vals)
        if not vals.get('summary_item_id'):
            for rec in self:
                if rec.summary_item_id:
                    rec.summary_item_id.write({
                        'product_id': rec.product_id.id,
                        'quantity': rec.quantity,
                        'unit_price': rec.unit_price,
                        'product_identification_ids': rec.product_identification_ids.ids,
                    })
        return res

    def unlink(self):
        for rec in self:
            if rec.is_added_in_so:
                raise ValidationError(_("You cannot delete this item as it is already added in the sale order."))
            if rec.summary_item_id:
                rec.summary_item_id.unlink()
        return super(ControllerTaskItems, self).unlink()

class SwitchingTaskItems(models.Model):
    _name = 'switching.task.items'

    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    is_added_in_so = fields.Boolean(string='Is Added In SO', default=False)
    task_id = fields.Many2one(comodel_name='project.task', string='Task', ondelete='cascade')
    is_tracked = fields.Boolean(string='Tracked', compute='_compute_is_tracked', store=True, default=False)
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers', copy=False)
    sale_line_id = fields.Many2one(comodel_name='sale.order.line', string='Sale Line')
    summary_item_id = fields.Many2one(comodel_name='task.items.summary', string='Summary Item')

    @api.constrains('quantity', 'unit_price')
    def _update_qty_price(self):
        for rec in self:
            if rec.sale_line_id:
                order = rec.task_id.sale_order_id.sudo()
                was_locked = order.locked
                if was_locked:
                    order.action_unlock()
                rec.sale_line_id.product_uom_qty = rec.quantity
                rec.sale_line_id.price_unit = rec.unit_price
                if was_locked:
                    order.action_lock()

    @api.depends('product_id')
    def _compute_is_tracked(self):
        for record in self:
            record.is_tracked = record.product_id.tracking != 'none'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.unit_price = record.product_id.list_price
                record.product_identification_ids = False

    @api.constrains('product_id', 'task_id')
    def _check_duplicate_products(self):
        for record in self:
            if record.task_id and record.product_id:
                duplicates = record.task_id.switching_task_items_ids.filtered(lambda r: r.product_id == record.product_id and r.id != record.id)
                if duplicates:
                    raise ValidationError(_("You cannot add the same product (%s) more than once in the same task.")% record.product_id.display_name)

    @api.constrains('quantity', 'product_identification_ids', 'is_tracked')
    def _check_quantity_vs_identifications(self):
        """If product is tracked then product_identification_ids must be filled and match quantity."""
        for record in self:
            if record.is_tracked:
                # Must have at least one identification if tracked
                if not record.product_identification_ids:
                    raise ValidationError(_("You must select identification numbers for the tracked product %s.") % record.product_id.display_name)
                # Optional strict rule: quantity = number of identifications
                if len(record.product_identification_ids) != int(record.quantity):
                    raise ValidationError(_("Quantity (%s) must equal the number of identification numbers (%s) for the tracked product %s.") % (record.quantity, len(record.product_identification_ids), record.product_id.display_name))

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SwitchingTaskItems, self).create(vals_list)
        for vals in res:
            summary_id = self.env['task.items.summary'].create({
                'task_id': vals.task_id.id,
                'product_id': vals.product_id.id,
                'quantity': vals.quantity,
                'unit_price': vals.unit_price,
                'product_identification_ids': vals.product_identification_ids.ids,
                'category': 'switching'
            })
            vals['summary_item_id'] = summary_id.id
        return res

    def write(self, vals):
        res = super(SwitchingTaskItems, self).write(vals)
        if not vals.get('summary_item_id'):
            for rec in self:
                if rec.summary_item_id:
                    rec.summary_item_id.write({
                        'product_id': rec.product_id.id,
                        'quantity': rec.quantity,
                        'unit_price': rec.unit_price,
                        'product_identification_ids': rec.product_identification_ids.ids,
                    })
        return res

    def unlink(self):
        for rec in self:
            if rec.is_added_in_so:
                raise ValidationError(_("You cannot delete this item as it is already added in the sale order."))
            if rec.summary_item_id:
                rec.summary_item_id.unlink()
        return super(SwitchingTaskItems, self).unlink()

class AccessoriesTaskItems(models.Model):
    _name = 'accessories.task.items'

    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    is_added_in_so = fields.Boolean(string='Is Added In SO', default=False)
    task_id = fields.Many2one(comodel_name='project.task', string='Task', ondelete='cascade')
    is_tracked = fields.Boolean(string='Tracked', compute='_compute_is_tracked', store=True, default=False)
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers', copy=False)
    sale_line_id = fields.Many2one(comodel_name='sale.order.line', string='Sale Line')
    summary_item_id = fields.Many2one(comodel_name='task.items.summary', string='Summary Item')

    @api.constrains('quantity', 'unit_price')
    def _update_qty_price(self):
        for rec in self:
            if rec.sale_line_id:
                order = rec.task_id.sale_order_id.sudo()
                was_locked = order.locked
                if was_locked:
                    order.action_unlock()
                rec.sale_line_id.product_uom_qty = rec.quantity
                rec.sale_line_id.price_unit = rec.unit_price
                if was_locked:
                    order.action_lock()

    @api.depends('product_id')
    def _compute_is_tracked(self):
        for record in self:
            record.is_tracked = record.product_id.tracking != 'none'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.unit_price = record.product_id.list_price
                record.product_identification_ids = False

    @api.constrains('product_id', 'task_id')
    def _check_duplicate_products(self):
        for record in self:
            if record.task_id and record.product_id:
                duplicates = record.task_id.accessories_task_items_ids.filtered(lambda r: r.product_id == record.product_id and r.id != record.id)
                if duplicates:
                    raise ValidationError(_("You cannot add the same product (%s) more than once in the same task.")% record.product_id.display_name)

    @api.constrains('quantity', 'product_identification_ids', 'is_tracked')
    def _check_quantity_vs_identifications(self):
        """If product is tracked then product_identification_ids must be filled and match quantity."""
        for record in self:
            if record.is_tracked:
                # Must have at least one identification if tracked
                if not record.product_identification_ids:
                    raise ValidationError(_("You must select identification numbers for the tracked product %s.") % record.product_id.display_name)
                # Optional strict rule: quantity = number of identifications
                if len(record.product_identification_ids) != int(record.quantity):
                    raise ValidationError(_("Quantity (%s) must equal the number of identification numbers (%s) for the tracked product %s.") % (record.quantity, len(record.product_identification_ids), record.product_id.display_name))

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccessoriesTaskItems, self).create(vals_list)
        for vals in res:
            summary_id = self.env['task.items.summary'].create({
                'task_id': vals.task_id.id,
                'product_id': vals.product_id.id,
                'quantity': vals.quantity,
                'unit_price': vals.unit_price,
                'product_identification_ids': vals.product_identification_ids.ids,
                'category': 'accessories'
            })
            vals['summary_item_id'] = summary_id.id
        return res

    def write(self, vals):
        res = super(AccessoriesTaskItems, self).write(vals)
        if not vals.get('summary_item_id'):
            for rec in self:
                if rec.summary_item_id:
                    rec.summary_item_id.write({
                        'product_id': rec.product_id.id,
                        'quantity': rec.quantity,
                        'unit_price': rec.unit_price,
                        'product_identification_ids': rec.product_identification_ids.ids,
                    })
        return res

    def unlink(self):
        for rec in self:
            if rec.is_added_in_so:
                raise ValidationError(_("You cannot delete this item as it is already added in the sale order."))
            if rec.summary_item_id:
                rec.summary_item_id.unlink()
        return super(AccessoriesTaskItems, self).unlink()

class TaskItemsSummary(models.Model):
    _name = 'task.items.summary'
    _description = 'Task Items Summary'
    _order = 'sequence, id'

    task_id = fields.Many2one(comodel_name='project.task', string='Task', required=True, ondelete='cascade')
    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    unit_price = fields.Float(string='Unit Price')
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers')
    category = fields.Selection(selection=[('video_conferencing', 'Video Conferencing Products'), ('video', 'Video Products'), ('audio', 'Audio Products'), ('controller', 'Controller Products'), ('switching', 'Switching Products'), ('accessories', 'Accessories')], string='Category')
    sequence = fields.Integer(string='Sequence', compute='_compute_sequence', store=True)

    @api.depends('category')
    def _compute_sequence(self):
        """Compute sequence based on category order"""
        category_sequence = {
            'video_conferencing': 1,
            'video': 2,
            'audio': 3,
            'controller': 4,
            'switching': 5,
            'accessories': 6,
        }
        for record in self:
            record.sequence = category_sequence.get(record.category, 99)

    @api.model
    def action_export_excel(self, task_id=None, project_name=None):
        """Export task items summary to Excel format"""
        # Get the records to export
        if task_id:
            records = self.search([('task_id', '=', task_id)])
            task = self.env['project.task'].browse(task_id)
            if project_name:
                filename = f"Project_{project_name.replace(' ', '_')}_Task_Items_Summary.xlsx"
            else:
                filename = f"Task_Items_Summary_{task.name.replace(' ', '_')}.xlsx"
        else:
            records = self
            if project_name:
                filename = f"Project_{project_name.replace(' ', '_')}_Task_Items_Summary.xlsx"
            else:
                filename = "Task_Items_Summary.xlsx"

        if not records:
            raise ValidationError(_("No records found to export."))

        # ✅ Sort by project, task, and category
        records = records.sorted(key=lambda r: (
            (r.task_id.project_id.name or '').lower(),
            (r.task_id.name or '').lower(),
            (r.category or '').lower()
        ))

        # Create Excel file in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        company_currency = self.env.company.currency_id
        currency_symbol = company_currency.symbol

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        data_format = workbook.add_format({'border': 1, 'align': 'left'})
        number_format = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '0.00'})
        currency_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'num_format': f'"{currency_symbol}"#,##0.00'
        })

        worksheet = workbook.add_worksheet('Task Items Summary')
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 12)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)

        headers = ['Project Name', 'Task Name', 'Product Name', 'Category', 'Quantity', 'Unit Price', 'Total Price']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        row = 1
        total_amount = 0
        for record in records:
            total_price = record.quantity * record.unit_price
            total_amount += total_price
            worksheet.write(row, 0, record.task_id.project_id.name or '', data_format)
            worksheet.write(row, 1, record.task_id.name or '', data_format)
            worksheet.write(row, 2, record.product_id.display_name or '', data_format)
            worksheet.write(row, 3, dict(record._fields['category'].selection).get(record.category, ''), data_format)
            worksheet.write(row, 4, record.quantity, number_format)
            worksheet.write(row, 5, record.unit_price, currency_format)
            worksheet.write(row, 6, total_price, currency_format)
            row += 1

        if row > 1:
            worksheet.write(row, 0, 'TOTAL:', header_format)
            worksheet.write(row, 5, 'TOTAL:', header_format)
            worksheet.write(row, 6, total_amount, header_format)

        workbook.close()
        excel_data = output.getvalue()
        output.close()
        excel_base64 = base64.b64encode(excel_data)

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': excel_base64,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': 'project.task',
            'res_id': task_id or False,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    @api.model
    def action_export_excel_with_project_header(self, task_ids=None, project_name=None):
        """Export task items summary with project header to Excel format"""
        if not task_ids:
            raise ValidationError(_("No task IDs provided."))

        records = self.search([('task_id', 'in', task_ids)])
        # ✅ Sort by project, task, and category
        records = records.sorted(key=lambda r: (
            (r.task_id.project_id.name or '').lower(),
            (r.task_id.name or '').lower(),
            (r.category or '').lower()
        ))

        tasks = self.env['project.task'].browse(task_ids)
        if not records:
            raise ValidationError(_("No records found to export."))

        filename = f"Project_{project_name.replace(' ', '_')}_Task_Items_Summary.xlsx" if project_name else "Task_Items_Summary.xlsx"
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        currency_symbol = self.env.company.currency_id.symbol

        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#4472C4', 'font_color': 'white', 'border': 1, 'align': 'center'
        })
        data_format = workbook.add_format({'border': 1, 'align': 'left'})
        number_format = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '0.00'})
        currency_format = workbook.add_format({
            'border': 1, 'align': 'right', 'num_format': f'"{currency_symbol}"#,##0.00'
        })

        worksheet = workbook.add_worksheet('Task Items Summary')
        worksheet.set_column('A:G', 20)

        row = 0
        if project_name:
            project_header_format = workbook.add_format({
                'bold': True, 'font_size': 16, 'bg_color': '#2F5597',
                'font_color': 'white', 'align': 'center', 'border': 1
            })
            worksheet.merge_range(0, 0, 0, 6, f"Project: {project_name}", project_header_format)
            row = 2

        headers = ['Project Name', 'Task Name', 'Product Name', 'Category', 'Quantity', 'Unit Price', 'Total Price']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)

        row += 1
        total_amount = 0
        for record in records:
            total_price = record.quantity * record.unit_price
            total_amount += total_price
            worksheet.write(row, 0, record.task_id.project_id.name or '', data_format)
            worksheet.write(row, 1, record.task_id.name or '', data_format)
            worksheet.write(row, 2, record.product_id.display_name or '', data_format)
            worksheet.write(row, 3, dict(record._fields['category'].selection).get(record.category, ''), data_format)
            worksheet.write(row, 4, record.quantity, number_format)
            worksheet.write(row, 5, record.unit_price, currency_format)
            worksheet.write(row, 6, total_price, currency_format)
            row += 1

        if row > (2 if project_name else 1):
            worksheet.write(row, 0, 'TOTAL:', header_format)
            worksheet.write(row, 5, 'TOTAL:', header_format)
            worksheet.write(row, 6, total_amount, header_format)

        workbook.close()
        excel_data = output.getvalue()
        output.close()
        excel_base64 = base64.b64encode(excel_data)

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': excel_base64,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': 'project.project' if project_name else 'project.task',
            'res_id': False,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    @api.model
    def action_export_excel_multiple_tasks(self, task_ids=None, project_name=None):
        """Export task items summary for multiple tasks to Excel format"""
        if not task_ids:
            raise ValidationError(_("No task IDs provided."))

        records = self.search([('task_id', 'in', task_ids)])
        # ✅ Sort by project, task, and category
        records = records.sorted(key=lambda r: (
            (r.task_id.project_id.name or '').lower(),
            (r.task_id.name or '').lower(),
            (r.category or '').lower()
        ))

        tasks = self.env['project.task'].browse(task_ids)
        if not records:
            raise ValidationError(_("No records found to export."))

        if project_name:
            filename = f"Project_{project_name.replace(' ', '_')}_Task_Items_Summary.xlsx"
        else:
            task_names = [task.name.replace(' ', '_') for task in tasks[:3]]
            if len(tasks) > 3:
                task_names.append(f"and_{len(tasks) - 3}_more")
            filename = f"Task_Items_Summary_{'_'.join(task_names)}.xlsx"

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        currency_symbol = self.env.company.currency_id.symbol

        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#4472C4', 'font_color': 'white', 'border': 1, 'align': 'center'
        })
        data_format = workbook.add_format({'border': 1, 'align': 'left'})
        number_format = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '0.00'})
        currency_format = workbook.add_format({
            'border': 1, 'align': 'right', 'num_format': f'"{currency_symbol}"#,##0.00'
        })

        worksheet = workbook.add_worksheet('Task Items Summary')
        worksheet.set_column('A:G', 20)

        headers = ['Project Name', 'Task Name', 'Product Name', 'Category', 'Quantity', 'Unit Price', 'Total Price']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        row = 1
        total_amount = 0
        for record in records:
            total_price = record.quantity * record.unit_price
            total_amount += total_price
            worksheet.write(row, 0, record.task_id.project_id.name or '', data_format)
            worksheet.write(row, 1, record.task_id.name or '', data_format)
            worksheet.write(row, 2, record.product_id.display_name or '', data_format)
            worksheet.write(row, 3, dict(record._fields['category'].selection).get(record.category, ''), data_format)
            worksheet.write(row, 4, record.quantity, number_format)
            worksheet.write(row, 5, record.unit_price, currency_format)
            worksheet.write(row, 6, total_price, currency_format)
            row += 1

        if row > 1:
            worksheet.write(row, 0, 'TOTAL:', header_format)
            worksheet.write(row, 5, 'TOTAL:', header_format)
            worksheet.write(row, 6, total_amount, header_format)

        workbook.close()
        excel_data = output.getvalue()
        output.close()
        excel_base64 = base64.b64encode(excel_data)

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': excel_base64,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': 'project.task',
            'res_id': False,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }