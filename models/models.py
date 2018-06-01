# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
import time,datetime
import sys
# sys.path.append('myaddons/purchase_track/fttx')
# from ImportFttx import ImportFttx

from odoo import api, fields, models

from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource


_logger = logging.getLogger(__name__)



class PurchaseTrackItems(models.Model):
    _name = 'purchase.track.items'
    _description = 'Track items'
    _rec_name = "name"

    name = fields.Char(string= "item")
    purchase_track_item_ids= fields.One2many('purchase.track.line', 'purchase_track_item', 'TrackItem')
    need_date= fields.Boolean(string="需要日期", default= True)

class PurchaseTrackLine(models.Model):
    _name = 'purchase.track.line'
    _description = 'Purchase Track Line'

    purchase_track_id = fields.Many2one('purchase.track', 'Purchase Track Id', ondelete='cascade', required=True)
    purchase_track_item = fields.Many2one('purchase.track.items','跟单事项' )
    confirm_date= fields.Date(string="发生日期")
    # date = fields.Date(string='Date', related='order_id.date', readonly=True, store=True)
    remarks = fields.Char(string="备注")
    editable = fields.Boolean(string="Editable", default=True, readonly= True)

    @api.one
    def write(self, vals):
        return super(PurchaseTrackLine,self).write(vals)

    # @api.multi
    def create(self, vals):
        # vals['editable'] = False
        if vals['purchase_track_item']:
            print('create！！')
            return super(PurchaseTrackLine,self).create(vals)
        else:
            print('create abort！！')
            return



class PurchaseTrackQc(models.Model):
    _name = 'purchase.track.qc'
    _description = '验货记录'

    purchase_track_id = fields.Many2one('purchase.track', 'Purchase Track Id', ondelete='cascade', required=True)
    qc_method = fields.Selection([('0', '现场'),('1','电子')], string= "验货方式")
    qc_clerk = fields.Char(string= "验货员")
    qc_date = fields.Date(string= "验货日期")
    qc_pass = fields.Selection([('0','PASS'), ('1', 'NG')],string= "验货结果")
    qc_remark = fields.Text(string= "备注")
    editable = fields.Boolean(string="Editable", default=True, readonly=True)

    @api.multi
    def create(self, vals):
        print('将要插入验货记录。。。')
        if bool(vals['qc_method']) & bool(vals['qc_clerk'].strip()) & bool(vals['qc_date']) & bool(vals['qc_pass']):

            return super(PurchaseTrackQc, self).create(vals)
        else:
            print('放弃插入验货记录')
            return


