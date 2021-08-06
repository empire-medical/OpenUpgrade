# -*- coding: utf-8 -*-

from odoo import models, fields, api
from ..constants import categories as empire_categories

class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"

    empire_category_id = fields.Integer(string="Empire Category ID", help="Empire Medicals Category ID")
    empire_parent_category_id = fields.Integer(string="Empire Parent Category ID", help="Empire Medicals Parent Category ID")

    """
        A map of Empire Medical category id's to Odoo product.category record ids.
    """
    _category_map = {
        empire_categories.BREAST_CARE: 49,
        empire_categories.DME: 50,
        empire_categories.LAB_SUPPLIES: 51,
        empire_categories.CASTING_SUPPLIES: 72,
        empire_categories.PLASTICS: 81,
        empire_categories.OTHER_SHEET_GOODS: 82,
        empire_categories.MISCELLANEOUS: 52,
        empire_categories.ORTHOTICS: 53,
        empire_categories.AFO: 71,
        empire_categories.COMPRESSION: 74,
        empire_categories.FOOT_ANKLE: 76,
        empire_categories.HIP: 77,
        empire_categories.KNEE: 78,
        empire_categories.SHOES: 83,
        empire_categories.SPINAL_CERVICAL: 84,
        empire_categories.ORTHOTICS_UPPER_EXTREMITY: 85,
        empire_categories.PROSTHETICS: 54,
        empire_categories.COMPONENTS: 73,
        empire_categories.FEET: 75,
        empire_categories.KNEES: 79,
        empire_categories.LINERS_SUSPENSION: 80,
        empire_categories.UPPER_EXTREMITY: 86
    }

    def action_convert_empire_category_id_to_odoo_id(self):
        self.ensure_one()
        odoo_category_id = self._category_map.get(self.empire_category_id, False)
        
        if (odoo_category_id == False):
            raise Exception("Category id not mapped. " + str(self.empire_category_id))
        
        self.write({'categ_id': odoo_category_id})