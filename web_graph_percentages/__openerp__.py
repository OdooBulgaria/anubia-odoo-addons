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
    'name': 'Web Graph Percentages',
    'summary': 'Allows to calculate percentages in pivot tables',
    'version': '1.0',

    'description': 'Allows to calculate percentages in pivot tables',

    'author': 'Anubía, soluciones en la nube, SL',
    'maintainer': 'Anubía, soluciones en la nube, SL',
    'contributors': ['Jorge Soto Garcia <sotogarcia@gmail.com>'],

    'website': "http://www.anubia.es",

    'license': 'AGPL-3',
    'category': 'Technical Settings',

    'depends': [
        'base',
        'web_graph'
    ],
    'external_dependencies': {
        'python': [
        ],
    },
    'data': [
        'views/assets_backend.xml'
    ],
    'demo': [
    ],
    'js': [
        'static/src/js/graph_view.js',
        'static/src/js/graph_widget.js',
        'static/src/js/pivot_table.js'
    ],
    'css': [
    ],
    'qweb': [
    ],
    'images': [
    ],
    'test': [
    ],

    'installable': True
}
