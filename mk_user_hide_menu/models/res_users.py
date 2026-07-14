# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Master Key.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class res_users(models.Model):
    _inherit = 'res.users'


    hide_menu_ids = fields.Many2many('ir.ui.menu',string="Hide Menu")
    
class ir_ui_menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        menus = super(ir_ui_menu, self).search(args, offset=0, limit=None, order=order)
        if menus:  
            for menu in self.env.user.hide_menu_ids:
                if menu in menus:
                    menus -= menu
        return menus
                                
                            
                            
                            
                        
                     
    
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
