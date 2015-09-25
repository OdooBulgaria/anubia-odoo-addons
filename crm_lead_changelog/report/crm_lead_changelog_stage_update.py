# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields, api
from openerp.tools import drop_view_if_exists
from logging import getLogger


_logger = getLogger(__name__)


class CrmLeadChangelogStageUpdate(models.Model):
    """ Stage id change log for all leads/opportunities ``
    """

    _name = 'crm.lead.changelog.stage.update'
    _description = u'Crm lead changelog stage update'

    _rec_name = 'id'
    _order = 'lead_id DESC, date DESC'

    _auto = False

    # ---------------------------- ENTITY FIELDS ------------------------------

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

    prev_stage_id = fields.Many2one(
        string='Previous stage of case',
        required=False,
        readonly=True,
        index=False,
        default=None,
        comodel_name='crm.case.stage',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help='Stage of case assigned to the lead in the previous change'
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
        help='Stage of case assigned to the lead in this change'
    )

    next_stage_id = fields.Many2one(
        string='Next stage of case',
        required=False,
        readonly=True,
        index=False,
        default=None,
        comodel_name='crm.case.stage',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help='Stage of case assigned to the lead in the next change'
    )

    is_initial = fields.Boolean(
        string='Is the initial stage of case?',
        required=False,
        readonly=True,
        index=False,
        default=False,
        help='Checked if it was the first change of stage of case'
    )

    is_current = fields.Boolean(
        string='Is the current stage of case?',
        required=False,
        readonly=True,
        index=False,
        default=False,
        help='Checked if it was the last change of stage of case'
    )

    sequence = fields.Integer(
        string='Sequence',
        required=True,
        readonly=True,
        index=False,
        default=0,
        help='Sequence order of this change in the lead changes'
    )

    date = fields.Datetime(
        string='Date',
        required=True,
        readonly=True,
        index=False,
        default=fields.datetime.now(),
        help='Date on which the change was made'
    )

    up_to = fields.Datetime(
        string='Date of the next change',
        required=False,
        readonly=True,
        index=False,
        default=fields.datetime.now(),
        help='Date on which the next change was made'
    )

    display_name = fields.Char(
        string='Display name',
        required=False,
        readonly=True,
        index=False,
        default=None,
        size=255,
        translate=False,
        help='Name to display',
        compute=lambda self: self._compute_display_name()
    )

    display_up_to = fields.Char(
        string='Display up to date',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False,
        compute=lambda self: self._compute_display_up_to()
    )

    # ----------------------- COMPUTED FIELD METHODS --------------------------

    @api.multi
    @api.depends('lead_id', 'stage_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = ' - '.join(
                filter(None, (record.lead_id.name, record.stage_id.name)))

    @api.multi
    @api.depends('date')
    def _compute_display_up_to(self):
        for record in self:
            year = fields.Datetime.from_string(record.up_to).year
            record.display_up_to = year < 9999 and record.up_to or 'infinity'

    # --------------------------- ONCHANGE EVENTS -----------------------------

    @api.one
    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        self._compute_display_name()

    @api.one
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        self._compute_display_name()

    # ------------------------- OVERWRITTEN METHODS ---------------------------

    def init(self, cr):
        """ Build database view which will be used as module origin

            :param cr: database cursor
        """

        self._sql_query = """
        SELECT
            ROW_NUMBER() OVER() AS "id",
            create_uid,
            create_date,
            write_uid,
            write_date,
            lead_id,
            LAG (stage_id, 1, NULL) OVER stage_w AS prev_stage_id,
            stage_id,
            LEAD (stage_id, 1, NULL) OVER stage_w AS next_stage_id,
            NOT(LAG (stage_id, 1, 0) OVER stage_w)::BOOLEAN AS is_initial,
            NOT(LEAD(stage_id, 1, 0) OVER stage_w)::BOOLEAN AS is_current,
            RANK () OVER stage_w AS "sequence",
            "date",
            LEAD ("date", 1,'9999-12-31 00:00:00' :: TIMESTAMP)
                OVER stage_w AS "up_to"
        FROM
            (
                SELECT
                    *
                FROM
                    crm_lead_changelog
                WHERE
                    stage_id_changed IS TRUE
            ) AS T1 WINDOW stage_w AS (
                PARTITION BY lead_id
                ORDER BY
                    DATE ASC
            )
        ORDER BY
            lead_id ASC,
            "date" DESC
        """

        drop_view_if_exists(cr, self._table)

        cr.execute(
            'create or replace view {} as ({})'.format(
                self._table,
                self._sql_query
            )
        )
