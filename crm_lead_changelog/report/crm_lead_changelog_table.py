# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.tools import drop_view_if_exists
from logging import getLogger


_logger = getLogger(__name__)


class CrmLeadChangelogTable(models.Model):
    """ User id change log for all leads/opportunities ``
    """

    _name = 'crm.lead.changelog.table'
    _description = u'Crm lead changelog table'

    _rec_name = 'id'
    _order = 'lead_id DESC, date DESC'

    _auto = False

    lead_id = fields.Many2one(
        string='Lead/Opportunity',
        required=True,
        readonly=True,
        index=True,
        default=None,
        comodel_name='crm.lead',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help='Lead which has been modified'
    )

    date = fields.Datetime(
        string='Date',
        required=True,
        readonly=True,
        index=False,
        default=fields.datetime.now(),
        help='Date on which the change was made'
    )

    zone_id = fields.Many2one(
        string='Zone',
        required=True,
        readonly=True,
        index=False,
        default=None,
        comodel_name='base.zone',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help=('Zone assigned to the lead in this change')
    )

    source_id = fields.Many2one(
        string='Source',
        required=True,
        readonly=True,
        index=False,
        default=None,
        comodel_name='crm.tracking.source',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help=('Source assigned to the lead in this change')
    )

    user_id = fields.Many2one(
        string='User',
        required=True,
        readonly=True,
        index=False,
        default=None,
        comodel_name='res.users',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help=('User assigned to the lead in this change')
    )

    stage_id = fields.Many2one(
        string='Stage of case',
        required=True,
        readonly=True,
        index=False,
        default=None,
        comodel_name='crm.case.stage',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help=('Stage of case assigned to the lead in this change')
    )

    reason_id = fields.Many2one(
        string='Salesperson',
        required=True,
        readonly=True,
        index=False,
        default=None,
        comodel_name='crm.stage.reason',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help=('Salesperson assigned to the lead in this change')
    )

    def init(self, cr):
        """ Build database view which will be used as module origin

            :param cr: database cursor
        """
        self._sql_query = """
            WITH
            user_updates AS (
                SELECT *
                FROM crm_lead_changelog
                WHERE user_id IS NOT NULL
                ORDER BY lead_id DESC, date DESC
            ),
            stage_updates AS (
                SELECT *
                FROM crm_lead_changelog
                WHERE stage_id IS NOT NULL
                ORDER BY lead_id DESC, date DESC
            ),
            reason_updates AS (
                SELECT *
                FROM crm_lead_changelog
                WHERE reason_id IS NOT NULL
                ORDER BY lead_id DESC, date DESC
            )
            SELECT
                row_number() OVER () AS id,
                crm_lead_changelog.lead_id AS lead_id,
                date,
                (SELECT base_zone_id
                    FROM crm_lead
                    WHERE id = crm_lead_changelog.lead_id
                    LIMIT 1) AS zone_id,
                (SELECT source_id
                    FROM crm_lead
                    WHERE id = crm_lead_changelog.lead_id
                    LIMIT 1) AS source_id,
                (SELECT user_id
                    FROM user_updates
                    WHERE user_updates.date <= crm_lead_changelog.date
                    AND user_updates.lead_id = crm_lead_changelog.lead_id
                    LIMIT 1) AS user_id,
                (SELECT stage_id
                    FROM stage_updates
                    WHERE stage_updates.date <= crm_lead_changelog.date
                    AND stage_updates.lead_id = crm_lead_changelog.lead_id
                    LIMIT 1) AS stage_id,
                (SELECT reason_id
                    FROM reason_updates
                    WHERE reason_updates.date <= crm_lead_changelog.date
                    AND reason_updates.lead_id = crm_lead_changelog.lead_id
                    LIMIT 1) AS reason_id
            FROM crm_lead_changelog
            ORDER BY lead_id ASC, date ASC
        """
        drop_view_if_exists(cr, self._table)
        cr.execute(
            'create or replace view {} as ({})'.format(
                self._table,
                self._sql_query
            )
        )