# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api
from openerp.tools.translate import _

import logging


_logger = logging.getLogger(__name__)


class CrmLeadChangelog(models.Model):
    """ Keep the history of changes in ``crm.lead,user_id`` and in
     ``crm.lead,stage.id`` fields.

    Fields:
    - lead_id: Lead to which this log record belongs
    - date: Date in which the change was done
    - stage_id: Stage of case before the change
    - user_id: Salesperson before the change
    - responsible_user_id: Who made the change
    """

    _name = 'crm.lead.changelog'
    _description = 'Lead change log'

    _rec_name = 'id'

    _order = 'date DESC'

    # --------------------------- ENTITY FIELDS -------------------------------

    lead_id = fields.Many2one(
        string='Lead',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Lead to which this log record belongs',
        comodel_name='crm.lead',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    date = fields.Datetime(
        string='Date',
        required=True,
        readonly=False,
        index=False,
        default=lambda self: fields.Datetime.context_today(self),
        help='Date in which the change was made'
    )

    stage_id = fields.Many2one(
        string='Stage of case',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Stage of case before the change',
        comodel_name='crm.case.stage',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    user_id = fields.Many2one(
        string='Salesperson',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Salesperson before the change',
        comodel_name='res.users',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    responsible_user_id = fields.Many2one(
        string='responsible for changing',
        required=True,
        readonly=False,
        index=False,
        default=lambda self: self.env.uid,
        help='Who made the change',
        comodel_name='res.users',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    # --------------------------- SQL CONSTRAINTS -----------------------------

    _sql_constraints = [
        (
            'non_empty',
            'CHECK(stage_id IS NOT NULL OR user_id IS NOT NULL)',
            _(u'Empty change in lead could not be registered')
        )
    ]
