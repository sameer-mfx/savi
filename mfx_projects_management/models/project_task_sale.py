from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def action_create_sale_order_lines(self):
        SaleOrderLine = self.env['sale.order.line']

        task_model_to_field = {
            'audio.task.items': 'audio_task_line_id',
            'video.task.items': 'video_task_line_id',
            'video.conferencing.task.items': 'video_conferencing_task_line_id',
            'controller.task.items': 'controller_task_line_id',
            'switching.task.items': 'switching_task_line_id',
            'accessories.task.items': 'accessories_task_line_id',
        }

        task_block = 1000
        category_block = 100
        category_offsets = {
            "Video Conferencing Products": 0,
            "Video Products": 100,
            "Audio Products": 200,
            "Controller Products": 300,
            "Switching Products": 400,
            "Accessories Products": 500,
        }

        task_categories = {
            "Video Conferencing Products": 'video_conferencing_task_items_ids',
            "Video Products": 'video_task_items_ids',
            "Audio Products": 'audio_task_items_ids',
            "Controller Products": 'controller_task_items_ids',
            "Switching Products": 'switching_task_items_ids',
            "Accessories Products": 'accessories_task_items_ids',
        }

        for task in self:
            if not task.sale_order_id:
                raise UserError(_("No Sale Order linked to task %s") % task.name)

            order = task.sale_order_id
            order_sudo = order.sudo()
            was_locked = order.locked
            if was_locked:
                order_sudo.action_unlock()

            task_base_sequence = task.id * task_block

            for category_name, field_name in task_categories.items():
                items = getattr(task, field_name)
                items_to_add = items.filtered(lambda i: not i.is_added_in_so)
                if not items_to_add:
                    continue

                category_base = task_base_sequence + category_offsets.get(category_name, 0)
                section_name = f"{category_name} - {task.name}"

                existing_section = order.order_line.filtered(
                    lambda l: l.display_type == 'line_section' and l.name == section_name
                )
                if existing_section:
                    section_line = existing_section.sorted(key=lambda r: r.sequence)[-1]
                else:
                    section_line = SaleOrderLine.create({
                        'order_id': order.id,
                        'display_type': 'line_section',
                        'name': section_name,
                        'sequence': category_base,
                    })

                existing_products = order.order_line.filtered(
                    lambda l: category_base < l.sequence < category_base + category_block and not l.display_type
                )

                next_sequence = section_line.sequence + len(existing_products) + 1

                if next_sequence + len(items_to_add) - 1 >= category_base + category_block:
                    raise UserError(_(
                        "Category '%s' for task '%s' cannot accept more items in the sale order."
                    ) % (category_name, task.name))

                for index, item in enumerate(items_to_add):
                    so_line_field = task_model_to_field.get(item._name)
                    sol_vals = {
                        'order_id': order.id,
                        'product_id': item.product_id.id,
                        'product_uom_qty': item.quantity,
                        'price_unit': item.unit_price,
                        'display_type': False,
                        'sequence': next_sequence + index,
                    }
                    if so_line_field:
                        sol_vals[so_line_field] = item.id

                    sol = SaleOrderLine.create(sol_vals)

                    item.write({
                        'sale_line_id': sol.id,
                        'is_added_in_so': True
                    })

            # Ensure service-tracking lines stay at the end
            service_line = order.order_line.filtered(lambda l: l.product_id.type == 'service' and l.product_id.service_tracking and l.product_id.service_tracking != 'no')
            highest_sequence = max(order.order_line.mapped('sequence'))
            if service_line and highest_sequence != service_line.sequence:
                service_line.sequence = highest_sequence * 1000

            if was_locked:
                order_sudo.action_lock()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    audio_task_line_id = fields.Many2one(comodel_name='audio.task.items', string='Audio Task Line')
    video_task_line_id = fields.Many2one(comodel_name='video.task.items', string='Video Task Line')
    video_conferencing_task_line_id = fields.Many2one(comodel_name='video.conferencing.task.items', string='Video Conferencing Task Line')
    accessories_task_line_id = fields.Many2one(comodel_name='accessories.task.items', string='Accessories Task Line')
    controller_task_line_id = fields.Many2one(comodel_name='controller.task.items', string='Controller Task Line')
    switching_task_line_id = fields.Many2one(comodel_name='switching.task.items', string='Switching Task Line')