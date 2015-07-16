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
    'name': 'CRM Lead Changelog',
    'summary': 'History of changes in leads/opportunities',
    'version': '1.0',

    'author': "Anubia, Soluciones en la Nube, SL",
    'website': "http://www.anubia.es",
    'maintainer': 'Anubia, soluciones en la nube, SL',

    'contributors': [
        'Jorge Soto García <sotogarcia@gmail.com>',
        'Daniel Lago Suárez <dls@anubia.es>',
        'Alejandro Santana <alejandrosantana@anubia.es>',
    ],

    'website': 'http://www.gitlab.com/',

    'license': 'AGPL-3',
    'category': 'Customer Relationship Management',

    'depends': [
        'base',
        'crm',
        'web',
        'web_m2x_options',
    ],
    'external_dependencies': {
        'python': [
        ],
    },
    'data': [
        'data/ir_actions_todo.xml',

        'views/crm_lead_changelog.xml',
        'views/crm_lead_changelog_view.xml',
        'wizards/build_crm_changelog_view.xml',
    ],
    'demo': [
    ],
    'js': [
    ],
    'css': [
        'static/static/css/crm_lead_changelog.css',
        'static/static/css/crm_lead_changelog.css'
    ],
    'qweb': [
    ],
    'images': [
    ],
    'test': [
    ],

    'installable': True
}
