# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2015
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
###############################################################################
{
    'name': 'Base Zone',
    'summary': 'Zip-based geographical zones for users',
    'version': '1.0',
    'description': 'Allows to define zip-based geographical zones for users',

    'author': 'Anubia, Soluciones en la Nube, SL',
    'maintainer': 'Anubía, Soluciones en la Nube, SL',
    'contributors': ['Jorge Soto García <sotogarcia@gmail.com>'],

    'website': 'http://www.anubia.es',

    'license': 'AGPL-3',
    'category': 'Customer Relationship Management',

    'depends': [
        'base',
        'mail',
        'base_location'
    ],
    'external_dependencies': {
        'python': [
        ],
    },
    'data': [
        'security/ir_model_access.xml',

        'views/base_zone_assets_backend.xml',
        'views/base_zone_view.xml',
        'views/res_users_view.xml',
        'views/res_better_zip_view.xml'
    ],
    'demo': [
        'demo/base_zone.xml',
        'demo/base_location_res_better_zip.xml'
    ],
    'js': [
    ],
    'css': [
        'static/src/css/base_zone.css'
    ],
    'qweb': [
    ],
    'images': [
    ],
    'test': [
    ],

    'installable': True
}
