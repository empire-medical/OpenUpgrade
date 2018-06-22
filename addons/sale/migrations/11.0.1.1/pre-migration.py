# -*- coding: utf-8 -*-
# Copyright 2018 - Nicolas JEUDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xmlid_renames = [
    ('account.group_proforma_invoices', 'sale.group_proforma_sales'),
]

# It comes from the renaming of website_portal_sale > sale_payment
_portal_xmlid_renames = [
    ('sale_payment.portal_my_home_menu_sale', 'sale.portal_my_home_menu_sale'),
    ('sale_payment.portal_my_home_sale', 'sale.portal_my_home_sale'),
    ('sale_payment.portal_my_quotations', 'sale.portal_my_quotations'),
    ('sale_payment.portal_my_orders', 'sale.portal_my_orders'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.rename_xmlids(env.cr, _portal_xmlid_renames)
    try:
        with env.cr.savepoint():
            env.ref('sale_payment.orders_followup').unlink()
    except Exception:
        pass
