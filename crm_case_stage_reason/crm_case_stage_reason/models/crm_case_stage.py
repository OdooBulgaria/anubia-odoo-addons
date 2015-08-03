# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from logging import getLogger


_logger = getLogger(__name__)


class CrmCaseStage(models.Model):
    """ Extends crm.case.stage model adding it reasons

    Fields:
      available_reason_ids: available reasons for each stage of case
      default_reason_id: default reason for each stage of case
    """

    _inherit = 'crm.case.stage'
    _description = u'Crm case stage'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Name',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help=False,
        size=50,
        translate=True
    )
