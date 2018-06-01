# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# 描述模块一些信息
{
    'name' : '采购跟单',
    #'version' : 0.1,
    'summary': '赢润公司采购跟单',
    'sequence': 1,
    'description': """
        用于本公司跟单部跟踪采购合同。
    """,
    # 'category': 'Accounting',
    'website': 'runwin.com',
    'images' : [],
    'depends' : ['web'],
    # 注意data中的文件顺序，ref的ID对应的record一定要在前面
    # 不理解的看views.xml中的action和menuitem的定义顺序
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/data.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    # 'installable': True,
    'application': True,
    # 'auto_install': False,
    # 'post_init_hook': '_auto_install_l10n',
}
