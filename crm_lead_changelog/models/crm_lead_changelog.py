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
    """

    _name = 'crm.lead.changelog'
    _description = 'Lead change log'

    _rec_name = 'date'

    _order = 'date ASC'

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
        default=lambda self: fields.Datetime.now(),
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

    reason_id = fields.Many2one(
        string='Reason',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Reason before the change',
        comodel_name='crm.stage.reason',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    # --------------------------- SQL CONSTRAINTS -----------------------------

    _sql_constraints = [
        (
            'non_empty',
            '''CHECK(stage_id IS NOT NULL OR user_id IS NOT NULL OR reason_id
                IS NOT NULL)''',
            _(u'Empty change in lead could not be registered')
        )
    ]

    # --------------------------- PUBLIC METHODS ------------------------------

    @api.model
    def ensure_changelog(self):
        """ Build a changelog of each one of the existing leads/opportunities
            which have not changelog.

            Values in fields `write_date`,  `create_date` and ``write_uid``
            will be the same as in the related Lead/Opportunity.
        """

        if self.env['crm.lead'].search_count([]):
            self.sudo().env.cr.execute(self._sql_ensure_changelog)

    # ----------------------------- SQL STRINGS -------------------------------

    _sql_ensure_changelog = """
       INSERT INTO crm_lead_changelog (
            lead_id,
            stage_id,
            user_id,
            reason_id,
            "date",
            create_uid,
            create_date,
            write_uid,
            write_date

        ) SELECT
            "id",
            stage_id,
            user_id,
            crm_reason_id,
            create_date,-- first changelog always match with the lead creation
            NULL,       -- allow to recognize preexisting leads in changelog
            NULL,       -- allow to recognize preexisting leads in changelog
            create_uid, -- first changelog always match with the lead creation
            create_date -- first changelog always match with the lead creation
        FROM
            crm_lead
        WHERE
            crm_lead. ID NOT IN (
                SELECT
                    lead_id
                FROM
                    crm_lead_changelog
            )
    """

