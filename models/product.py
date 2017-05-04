# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from odoo import fields, models, api
from odoo.addons import decimal_precision as dp
import math

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _compute_quantities(self):
        super(ProductTemplate, self)._compute_quantities()
        bom_template= self.filtered(lambda p: p.bom_ids.exists())

        for template in bom_template:
            bom = self.env['mrp.bom'].sudo()._bom_find(product_tmpl=template)
            if not bom or bom.type != 'phantom':
                continue
            factor = template.uom_id._compute_quantity(1, bom.product_uom_id) / bom.product_qty
            boms, lines = bom.sudo().explode(template.product_variant_id, factor, picking_type=bom.picking_type_id)

            pack_qty_available = []
            pack_virtual_available = []
            for bom_line, line_data in lines:
                subproduct_stock = bom_line.product_id._product_available()[bom_line.product_id.id]
                sub_qty = line_data['qty']
                if sub_qty:
                    pack_qty_available.append(math.floor(
                        subproduct_stock['qty_available'] / sub_qty))
                    pack_virtual_available.append(math.floor(
                        subproduct_stock['virtual_available'] / sub_qty))

            template.qty_available += min(pack_qty_available)
            template.virtual_available += min(pack_virtual_available)



class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('stock_quant_ids', 'stock_move_ids')
    def _compute_quantities(self):
        super(ProductProduct, self)._compute_quantities()

        bom_product = self.filtered(lambda p: p.bom_ids.exists())

        for product in bom_product:
            bom = self.env['mrp.bom'].sudo()._bom_find(product=product)
            if not bom or bom.type != 'phantom':
                continue
            factor = product.uom_id._compute_quantity(1, bom.product_uom_id) / bom.product_qty
            boms, lines = bom.sudo().explode(product, factor, picking_type=bom.picking_type_id)

            pack_qty_available = []
            pack_virtual_available = []
            for bom_line, line_data in lines:
                subproduct_stock = bom_line.product_id._product_available()[bom_line.product_id.id]
                sub_qty = line_data['qty']
                if sub_qty:
                    pack_qty_available.append(math.floor(
                        subproduct_stock['qty_available'] / sub_qty))
                    pack_virtual_available.append(math.floor(
                        subproduct_stock['virtual_available'] / sub_qty))

            product.qty_available += min(pack_qty_available)
            product.virtual_available += min(pack_virtual_available)
