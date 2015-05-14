# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2014      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Jorge Soto García <sotogarcia@gmail.com>
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
    'name': "Anubia Support",
    'version': '0.1',

    'summary': """Anubia, technical support module""",

    'description': """
        Anubia Soluciones en la Nube SL, technical support module.

        - Anubia Contact Data
        - Anubia Technical Support User
    """,

    'author': 'Anubia, Soluciones en la Nube, SL',
    'website': "http://www.anubia.es",
    'maintainer': 'Anubia, soluciones en la nube, SL',

    'contributors': [
        'Jorge Soto García <sotogarcia@gmail.com>',
    ],

    'category': 'Technical Settings',
    'version': '0.1',

    'depends': ['base'],

    'data': [
        'data/res_partner.xml',
        'data/res_users.xml',

        'security/res_groups.xml',

        'views/ir_module_module.xml'
    ],

    'demo': [
    ],
}
