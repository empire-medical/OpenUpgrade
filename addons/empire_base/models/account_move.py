# -*- coding: utf-8 -*-

from odoo import models, fields, api
from ..constants import categories as empire_categories
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _name = "account.move"
    _inherit = "account.move"

    empire_invoice_number = fields.Char(string='Empire Invoice Number', index=True, readonly=True, states={'draft': [('readonly', False)]}, help='The invoice number in Empire Medicals system')
    empire_cc_identifier = fields.Char(string='Empire CC Identifier', index=True, help="For script usage. Easy identifier to know which CC journal to create payments for")
    empire_date_invoice = fields.Date(string='Empire Bill Date', index=True, readonly=True, help="The date this item was billed/credited in Imperium")

class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = "account.move.line"

    empire_salesperson_id = fields.Many2one('res.users', string="Salesperson", ondelete="set null")
    customer_id = fields.Many2one('res.partner', string="Customer (CC)", ondelete="restrict")
    is_shipping_line = fields.Boolean(string="Is Shipping", readonly=True, states={'draft': [('readonly', False)]}, help='Indicates that this Invoice Line is a shipping line.')
    is_empires_shipping_account = fields.Boolean(string="Is Empires Shipping Account", readonly=True, states={'draft': [('readonly', False)]}, help="Indicates which analytic tag this shipping line uses")
    empire_category_id = fields.Integer(string="Empire Category ID", help="Empire Medicals Category ID")
    empire_parent_category_id = fields.Integer(string="Empire Parent Category ID", help="Empire Medicals Parent Category ID")

    _analytic_tag_map = {
        empire_categories.AFO: "AFO",
        empire_categories.CASTING_SUPPLIES: "Casting Supplies",
        empire_categories.COMPONENTS: "Components",
        empire_categories.COMPRESSION: "Compression",
        empire_categories.FEET: "Feet (P)",
        empire_categories.UPPER_EXTREMITY: "Upper Extremity (P)",
        empire_categories.FOOT_ANKLE: "Foot & Ankle (O)",
        empire_categories.KNEES: "Knees (P)",
        empire_categories.HIP: "Hip",
        empire_categories.KNEE: "Knee (O)",
        empire_categories.PLASTICS: "Plastics",
        empire_categories.OTHER_SHEET_GOODS: "Sheet Goods (non-plastic)",
        empire_categories.LINERS_SUSPENSION: "Liners",
        empire_categories.SHOES: "Shoes",
        empire_categories.SPINAL_CERVICAL: "Spinal/Cervical",
        empire_categories.ORTHOTICS_UPPER_EXTREMITY: "Upper Extremity (O)",
        empire_categories.SHIPPING_HANDLING: "Empire's Shipper Account",
        empire_categories.SHIPPING_HANDLING_VENDOR: "Vendor's Shipper Account"
    }

    _analytic_account_map = {
        empire_categories.LAB_SUPPLIES: "Lab Supplies",
        empire_categories.ORTHOTICS: "Orthotics",
        empire_categories.SHOES: "Orthotics",
        empire_categories.PROSTHETICS: "Prosthetics",
        empire_categories.BREAST_CARE: "Breast Care",
        empire_categories.DME: "DME",
        empire_categories.MISCELLANEOUS: "Miscellaneous",
        empire_categories.FINANCE_CHARGES: "Finance Charges",
        empire_categories.HANDLING_CHARGE: "Handling",
        empire_categories.HANDLING_CHARGE_ST: "Handling - ST",
        empire_categories.HAZMAT_FEES: "Hazmat Fees",
        empire_categories.MINFEE: "Minimum Order Fees",
        empire_categories.VENDOR_REBATES: "Vendor Rebates",
        empire_categories.RESTOCKING_FEES: "Restocking Fees",
        empire_categories.SHIPPING_HANDLING: "Shipping",
        empire_categories.SHIPPING_HANDLING_VENDOR: "Shipping"
    }

    def action_apply_tags(self):
        """
            Apply appropriate tags to the Move Line.

            For Move Lines that are representative of Products then the
            Move Line should have an Analytic Account and several Analytic Tags applied.

            For Move Lines that are representative of Shipping costs then the
            Move Line should have an Analytic Account of Shipping and an Analytic Tag
            of either Vendor's Shipping Account or Empire's Shipping Account depending on
            specified criteria.
        """
        self.ensure_one()
        properties = {}
        if (self.is_shipping_line):
            _logger.info("Move Line is Shipping Line")
            properties = self._get_shipping_line_write_properties()
        else:
            _logger.info("Move Line is not Shipping Line")
            properties = self._get_product_line_write_properties()
        
        if (properties.keys()):
            self.write(properties)
            _logger.info("Tags written to Move Line")
            _logger.info("Properties written ".join(map(str, properties.keys())))

    def action_apply_salesperson_tag(self, salesperson_name):
        """
            Apply appropriate Salesperson tag to the Invocie Line
        """
        self.ensure_one()
        tag = self._get_analytic_tag("Salesperson: %s" % (salesperson_name))

        if (tag):
            self.write({ "analytic_tag_ids": [(4, tag, False)]})

    def _get_shipping_line_write_properties(self):
        #
        # When the move type is in_invoice or in_refund then the Analytic Tag should always be "Vendor's Shipping Account"
        # When the move type is out_invoice or out_refund then the Analytic Tag should be determined by empire_category_id of the Invoice Line
        # The Analytic Account should always be "Shipping"
        #
        properties = {}
        if (self.move_id.type in ["in_invoice", "in_refund"] or self.is_empires_shipping_account == False):
            _logger.info("Shipping Line: Parent move is in_invoice or in_refund")
            analytic_tag_id = self._get_analytic_tag("Vendor's Shipper Account")
            if (analytic_tag_id is not None):
                properties = self._add_analytic_command(properties, (4, analytic_tag_id, False))
            else:
                _logger.info("Shipping Line: Could not find Vendor's Shipper Account analytic tag")
        elif (self.is_empires_shipping_account):
            analytic_tag_id = self._get_analytic_tag("Empire's Shipper Account")
            if (analytic_tag_id is not None):
                properties = self._add_analytic_command(
                    properties, (4, analytic_tag_id, False))
            else:
                _logger.info(
                    "Shipping Line: Could not find Empire's Shipper Account analytic tag")
        
        analytic_account_id = self._get_analytic_account_id("Shipping")
        if (analytic_account_id is not None):
            properties['account_analytic_id'] = analytic_account_id
        else:
            _logger.info("Shipping Line: Could not find shipping analytic account")

        # Shipping lines should only have flagship tags on Invoices and Credit Memos
        if (self.move_id.type in ["out_invoice", "out_refund"]):
            flagship_analytic_tag_id = self._get_flagship_analytic_tag_id()
            if (flagship_analytic_tag_id is not None):
                properties = self._add_analytic_command(properties, (4, flagship_analytic_tag_id, False))

        return properties

    def _add_analytic_command(self, properties, command):
        if ("analytic_tag_ids" not in properties):
            properties["analytic_tag_ids"] = []
        properties["analytic_tag_ids"].append(command)
        return properties

    def _get_product_line_write_properties(self):
        properties = {}
        account_analytic_id = self._get_analytic_account_id(self._get_analytic_account_name())
        update_analytic_tags_command = self._get_update_analytic_tags_command()
        if (not update_analytic_tags_command):
            _logger.info(
                "Received empty update_analytic_tags_command ID: {0}".format(self.id))
        else:
            properties['analytic_tag_ids'] = update_analytic_tags_command
        if (not account_analytic_id):
            message = "Received empty account_analytic_id ID: {0} Category ID: {1} Parent Category ID: {2}"
            _logger.info(message.format(
                self.id, self.empire_category_id, self.empire_parent_category_id))
        else:
            properties['account_analytic_id'] = account_analytic_id
        return properties

    def _get_update_analytic_tags_command(self):
        command = []
        category_analytic_tag_id = self._get_analytic_tag(self._get_category_analytic_tag_name())
        flagship_analytic_tag_id = self._get_flagship_analytic_tag_id()
        if (category_analytic_tag_id is not None):
            command.append((4, category_analytic_tag_id, False))
        else:
            _logger.info("Move Line category analytic tag id was not found!")
        if (flagship_analytic_tag_id is not None):
            command.append((4, flagship_analytic_tag_id, False))
        else:
            _logger.info("Move Line flagship analytic tag id was not found!")

        return command

    def _get_category_analytic_tag_name(self):
        category_name = None
        category_id = self.empire_category_id
        if (not category_id):
            message = "Move Line's does not have an empire category assigned!"
            _logger.info(message)
        
        if (category_id not in self._analytic_tag_map):
            message = "Move Line category id not in analytic tag map. ID: {0}, Category ID: {1}".format(self.id, category_id)
            _logger.info(message)
        else:
            category_name = self._analytic_tag_map.get(category_id)

        return category_name

    def _get_flagship_analytic_tag_id(self):
        if (self.customer_id.is_flagship):
            _logger.info("Move Line's parent is a flagship")
            return self._get_analytic_tag("Flagship")
        else:
            _logger.info("Move Line's parent is not a flagship")
            return self._get_analytic_tag("Non-Flagship")
        return None

    def _get_analytic_tag(self, name):        
        if (name):
            analytic_tag = self.env['account.analytic.tag'].search([("name", "=", name)], limit=1)
            return getattr(analytic_tag, 'id', None)

        return None

    def _get_analytic_account_id(self, name):
        if (name):
            analytic_account = self.env['account.analytic.account'].search([("name", "=", name)], limit=1)
            return getattr(analytic_account, 'id', None)
        
        return None

    def _get_analytic_account_name(self):
        # 
        # If the parent category id is empty then
        # we want to fall back to the category id
        # in order to handle the SHOES category
        #
        parent_category_id = self.empire_parent_category_id

        if (not parent_category_id):
            _logger.info("Move Line does not have a parent category id.")

        if (parent_category_id):
            return self._analytic_account_map.get(parent_category_id)

        product_category_id = self.empire_category_id

        if (not product_category_id):
            _logger.info("Move Line's product does not have a category id")

        return self._analytic_account_map.get(product_category_id)
