# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from datetime import date, datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class CrmPeriod(models.Model):

    _name = 'crm.period'

    name = fields.Char(
        string='Name',
        required=True,
    )

    first_date = fields.Date(
        string='First date',
        default=date.today(),
    )

    last_date = fields.Date(
        string='Last date',
        default=date.today(),
    )
