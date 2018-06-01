# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
import time,datetime
import sys
sys.path.append('myaddons/purchase_track/fttx')
from ImportFttx import ImportFttx

from odoo import api, fields, models

from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource


_logger = logging.getLogger(__name__)

class PurchaseTrack(models.Model):
    # 此处odoo建表是:purchase_track
    _name = 'purchase.track'
    _rec_name= 'purcharse_no'

    purchase_id = fields.Char(string= "采购ID")
    purcharse_no= fields.Char(string="采购单号")
    cust_no = fields.Char(string="客户编号")
    salesman = fields.Char(string="业务员")
    contract_op_name = fields.Char(string='外销操作员')
    user_id = fields.Many2one('res.users', '跟单员')
    buyer = fields.Char(string="采购员")
    supply_name= fields.Char(string="供应商")
    product_type= fields.Char(string= "产品类别")
    purchase_date= fields.Date(string="下单日期", compute ='_compute_purchase', store=True)
    purchase_year= fields.Integer(string="年", compute= '_compute_purchase', store= True)
    purchase_month= fields.Integer(string="月", compute= '_compute_purchase', store= True)
    purchase_delivery_date = fields.Date(string="要求交期")
    total_num= fields.Char(string="总数量")
    total_amount= fields.Char(string="总金额")
    category= fields.Selection([('0','光源'),('1','杂货'),('2','商照'),('3','功能'),('4','户外')], string='大类')
    category_detail= fields.Char(string="品名")
    # have_invoice= fields.Boolean(string="开票")
    have_invoice= fields.Selection([('0','开票'),('1','不开票')], string="开票否")
    have_deliver= fields.Selection([('0','含'),('1','否')], string='含运')
    price_type= fields.Char(string= "价格类型")
    payment_method= fields.Char(string="付款方式")
    # payment_method= fields.Selection([('0','现金'),('1','月结'),('2','月结现金')], string= "结算方式")
    purchase_back_date = fields.Date(string="合同回传", compute= '_compute_purchase', store=True)
    actually_delivery_date = fields.Date(string= "实际交期", compute= '_compute_purchase')
    delivery_state = fields.Selection([('0','未出货'),('1','等出货'),('2','已出货')],default=0, string='交货状态')
    purchase_track_line_ids = fields.One2many('purchase.track.line', 'purchase_track_id', 'Tracks')
    purchase_track_qc_ids= fields.One2many('purchase.track.qc', 'purchase_track_id', 'Qc')
    timeline= fields.Html(string="时间线", compute="_compute_purchase_timeline")
    is_finished = fields.Selection([('0','未完成'),('1','完成') ], default="0", string="是否完成")
    is_del = fields.Boolean(string="已删除", default= False)

    @api.multi
    # 保存时,跟单中的editable写为False
    def write(self, vals):
        result = super(PurchaseTrack, self).write(vals)
        self.purchase_track_line_ids.write({'editable': False})
        # 保存时,如果已经有填写日期，明细条目的editable写为False
        for item in self.purchase_track_line_ids:
            if item['confirm_date'] != False:
                item['editable'] = False
            else:
                item['editable'] = True
        # self.purchase_track_qc_ids.write({'editable': False})
        return result

    @api.depends()
    # 根据跟单事项填写时间线
    def _compute_purchase_timeline(self):
        for rec in self:
            # def choose(trackItems, track_id ):
            #     '''
            #     1.在所有跟单记录(trackItems)中,根据跟单项ID(track_id)找出所有对应记录id列表item_ids，
            #     2.max(item_ids)就是最近更新的跟单记录ID，找出对应的confirm_date,
            #     3.再拼接跟单项名称返回
            #     :param trackItems: 所有跟单记录
            #     :param track_id: 某一个跟单项ID
            #     :return: string 跟单项:日期
            #     '''
            #     item_ids = []
            #     info= ''
            #     # 1
            #     for rec_line in trackItems.purchase_track_line_ids:
            #         if rec_line.purchase_track_item.id == track_id:
            #             item_ids.append(rec_line.id)
            #     if len(item_ids) > 0:
            #         # 2
            #         for rec_line in  trackItems.purchase_track_line_ids:
            #             # print('-------------------------------')
            #             # print(rec_line.confirm_date)
            #             # print( (rec_line.id == max(item_ids)) &  bool(rec_line.confirm_date) )
            #             if (rec_line.id == max(item_ids)) &  bool(rec_line.confirm_date):
            #                 # 字段本身输出字符串，先转换成时间格式，再格式化输出
            #                 info= datetime.datetime.strptime(rec_line.confirm_date,'%Y-%m-%d').strftime("%m/%d")
            #                 # 3. 拼接项目名称
            #                 info= '<span style="color:red; font-weight:700">'+ rec_line.purchase_track_item.name + ':</span>' + info + '→ '
            #                 if bool(info):
            #                     return info
            #                 else:
            #                     return ''
            #
            #         return ''
            #     else:
            #         return ''
            def _choose(trackItems, track_id):
                # 格式化返回日期，合并跟单项名称
                final_date= self.choose(trackItems, track_id)
                if final_date != '':
                    # 字段本身输出字符串，先转换成时间格式，再格式化输出
                    final_date= datetime.datetime.strptime(final_date, '%Y-%m-%d').strftime("%m/%d")
                    # 从 跟单项目表 中找到 对应 项目名称
                    final_date= '<span style="color:red; font-weight:700">'\
                                + self.env['purchase.track.items'].search([('id','=',track_id)]).name \
                                + ':</span>' + final_date + '→ '
                    return final_date
                else:
                    return ''

            rec.timeline = ''
            # rec.timeline = self.choose(rec, 1)
            for item in self.env['purchase.track.items'].search([('id','>',0)]):
                rec.timeline +=  _choose(rec, item.id)
    # 根据明细填写表头某些字段
    @api.depends('purchase_track_line_ids.confirm_date')
    def _compute_purchase(self):
        for rec in self:
            # 根据明细填写 下单日期
            _purchase_date= self.choose(rec, 1 )
            rec.purchase_date= _purchase_date
            if _purchase_date:
                # 如果跟单日期不为空，计算合同下单年, 月
                rec.purchase_year = datetime.datetime.strptime(_purchase_date, '%Y-%m-%d').year
                rec.purchase_month = datetime.datetime.strptime(_purchase_date, '%Y-%m-%d').month
            # 根据明细填写 实际交期
            rec.actually_delivery_date = self.choose(rec, 10 )
            # 根据明细填写 合同回传
            rec.purchase_back_date = self.choose(rec, 5)

    # (跟单明细，跟单项id) => 此跟单项发生日期
    def choose(self, trackItems, track_id):
        # 跟单明细长度
        num_of_track_item = len(trackItems.purchase_track_line_ids)
        n= -1
        # 从最后一项开始检查，匹配跟单项目ID,并且日期不为空，返回日期
        while n >= -num_of_track_item:
            last_item= trackItems.purchase_track_line_ids[n]
            if last_item.purchase_track_item.id == track_id and last_item.confirm_date:
                return last_item.confirm_date
            n= n-1



    @api.model
    # 从富通导入采购单
    def cron_get_purchase_from_fttx(self):
        reslist = ImportFttx('runwin_odoo_purchase', "SignDate>'2018-05-15'").ExecQuery()
        # for k in reslist:
        #     print(k)
        #     print(reslist[k])
        # 将查询结果导入到PurchaseTrack模型
        for id in reslist['id']:
            # 根據id查詢結果，如果長度小於，判斷ci ID是否存在
            if len(self.search([('purchase_id','=',id)]))< 1:
                _create_date= {
                    'purchase_id': id,
                    'purcharse_no': reslist[id]['purchase_no'],
                    'buyer': reslist[id]['purchase_op_name'],
                    'contract_op_name' : reslist[id]['contract_op_name'],
                    'salesman' : reslist[id]['cust_op_name'],
                    'cust_no': reslist[id]['cust_no'],
                    'total_amount': reslist[id]['total_amount'],
                    'total_num': reslist[id]['total_num'],
                    'supply_name': reslist[id]['supply_name'],
                    'purchase_delivery_date': reslist[id]['purchase_deliver_date'],
                    'editable': True
                }
                print(_create_date)
                # 向purchase.track中写入新的采购数据
                val= self.create(_create_date)
                # 得到刚插入数据的id
                print(val)
                new_id= val['id']
                print(new_id)
                # 写入明细purchase.track.line
                all_track_items= self.env['purchase.track.items'].search([('id','>',0)])
                for item in all_track_items:
                    self.env['purchase.track.line'].create({
                        'purchase_track_id': new_id,
                        'purchase_track_item' : item['id']
                    })


        print('写入跟单明细........')
        list= self.env['purchase.track.items'].search([('id','>',0)])
        print(list)
        for li in list:
            print(li['id'])

    @api.onchange('purchase_track_line_ids')
    def onchange_line(self):
        print('change----- ------------')

    # @api.multi
    def btn_unlink(self):
        if self.is_del == False:
            return self.write({
                'is_del': True
            })
        else:
            return self.write({
                'is_del': False
            })