# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

def move_fields_from_invoice_to_moves(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET empire_invoice_number = ai.empire_invoice_number
        FROM account_invoice ai
        WHERE am.old_invoice_id = ai.id AND
            ai.empire_invoice_number IS NOT NULL"""
    )

    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET empire_cc_identifier = ai.empire_cc_identifier
        FROM account_invoice ai
        WHERE am.old_invoice_id = ai.id AND
            ai.empire_cc_identifier IS NOT NULL"""
    )

    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET empire_date_invoice = ai.invoice_date
        FROM account_invoice ai
        WHERE am.old_invoice_id = ai.id AND
            ai.empire_date_invoice IS NOT NULL"""
    )

def move_fields_from_invoice_lines_to_move_lines(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET empire_salesperson_id = ail.empire_salesperson_id
        FROM account_invoice_line ail
        WHERE aml.old_invoice_line_id = ail.id AND
            ail.empire_salesperson_id IS NOT NULL"""
    )

    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET customer_id = ail.customer_id
        FROM account_invoice_line ail
        WHERE aml.old_invoice_line_id = ail.id AND
            ail.customer_id IS NOT NULL"""
    )

    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET is_shipping_line = ail.is_shipping_line
        FROM account_invoice_line ail
        WHERE aml.old_invoice_line_id = ail.id AND
            ail.is_shipping_line IS NOT NULL"""
    )

    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET is_empires_shipping_account = ail.is_empires_shipping_account
        FROM account_invoice_line ail
        WHERE aml.old_invoice_line_id = ail.id AND
            ail.is_empires_shipping_account IS NOT NULL"""
    )

    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET empire_category_id = ail.empire_category_id
        FROM account_invoice_line ail
        WHERE aml.old_invoice_line_id = ail.id AND
            ail.empire_category_id IS NOT NULL"""
    )

    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET empire_parent_category_id = ail.empire_parent_category_id
        FROM account_invoice_line ail
        WHERE aml.old_invoice_line_id = ail.id AND
            ail.empire_parent_category_id IS NOT NULL"""
    )


@openupgrade.migrate()
def migrate(env, version):
    move_fields_from_invoice_to_moves(env)
    move_fields_from_invoice_lines_to_move_lines(env)
