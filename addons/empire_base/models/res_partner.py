# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    is_flagship = fields.Boolean(string='Is Flagship', default=False, help='Indicates whether or not the Customer is a Flagship customer in Imperium')
    empire_payment_term_id = fields.Integer(string="Empire Payment Term ID", readonly=True, states={'draft': [('readonly', False)]}, help='The payment term id in Empire Medicals system')

    def action_associate_flagship_status(self):
        self.ensure_one()

        if (self.customer == False):
            return

        command = False
        if (self.is_flagship):
            partner_tag_id = self._get_partner_tag("Flagship")
            command = [(4, partner_tag_id, False)]
        else:
            partner_tag_id = self._get_partner_tag("Non-Flagship")
            command = [(4, partner_tag_id, False)]

        if (command != False):
            self.write({
                'category_id': command
            })

    def _get_partner_tag(self, name):
        return self.env['res.partner.category'].search([("name", "=", name)], limit=1).id
