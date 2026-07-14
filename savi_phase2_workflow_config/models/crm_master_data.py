from odoo import api, models


class UtmSource(models.Model):
    _inherit = "utm.source"

    @api.model
    def savi_ensure_sources(self, names):
        existing = {
            source.name.casefold()
            for source in self.search([])
            if source.name
        }
        for name in names:
            if name and name.casefold() not in existing:
                self.create({"name": name})
                existing.add(name.casefold())


class CrmLostReason(models.Model):
    _inherit = "crm.lost.reason"

    @api.model
    def savi_ensure_lost_reasons(self, names):
        existing = {
            reason.name.casefold()
            for reason in self.search([])
            if reason.name
        }
        for name in names:
            if name and name.casefold() not in existing:
                self.create({"name": name})
                existing.add(name.casefold())
