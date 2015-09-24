# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2014      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Alejandro Santana <alejandrosantana@anubia.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#
##############################################################################

{
    'name': 'Custom reports 00',
    'version': '0.1',
    'category': 'Customization',
    # 'complexity': 'normal',
    'license': 'AGPL-3',
    'author': 'Alejandro Santana <alejandrosantana@anubia.es>',
    'maintainer': 'Anubía, soluciones en la nube, SL',
    'website': 'http://www.anubia.es',
    'depends': [
        'account',
        'crm',
        'report',
        'sale',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'data/report_paperformat.xml',
        'data/base_data.xml',
        'views/ir_qweb.xml',
        'views/layouts.xml',
        'views/report_saleorder.xml',
        'views/report_invoice.xml',
    ],
    'demo': [],
    'test': [],
    'qweb': [],
    'images': [],
    'css': [
        'static/src/css/style.css',
    ],
    'js': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    # 'bootstrap': True,
    # 'certificate': 'certificate',
}
