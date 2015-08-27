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


class CrmLeadChangelogUserUpdate(models.Model):
    """ User id change log for all leads/opportunities ``
    """

    _name = 'crm.lead.changelog.user.update'
    _description = u'Crm lead changelog user update'

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

    prev_user_id = fields.Many2one(
        string='Previous salesperson',
        required=False,
        readonly=True,
        index=False,
        default=None,
        comodel_name='res.users',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help=('Salesperson assigned to the lead in the previous change')
    )

    user_id = fields.Many2one(
        string='Salesperson',
        required=True,
        readonly=True,
        index=False,
        default=None,
        comodel_name='res.users',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help=('Salesperson assigned to the lead in this change')
    )

    next_user_id = fields.Many2one(
        string='Next salesperson',
        required=False,
        readonly=True,
        index=False,
        default=None,
        comodel_name='res.users',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help=('Salesperson who has been assigned to the lead in the next '
              'change')
    )

    is_initial = fields.Boolean(
        string='Is the initial salesperson?',
        required=False,
        readonly=True,
        index=False,
        default=False,
        help='Checked if it was the first change of salesperson'
    )

    is_current = fields.Boolean(
        string='Is the current salesperson?',
        required=False,
        readonly=True,
        index=False,
        default=False,
        help='Checked if it was the last change of salesperson'
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

    @api.multi
    @api.depends('lead_id', 'user_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = ' - '.join(
                filter(None, (record.lead_id.name, record.user_id.name)))

    @api.multi
    @api.depends('date')
    def _compute_display_up_to(self):
        for record in self:
            year = fields.Datetime.from_string(record.up_to).year
            record.display_up_to = year < 9999 and record.up_to or 'infinity'

    @api.one
    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        self._compute_display_name()

    @api.one
    @api.onchange('user_id')
    def _onchange_user_id(self):
        self._compute_display_name()


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
                LAG (user_id, 1, NULL) OVER user_w AS prev_user_id,
                user_id,
                LEAD (user_id, 1, NULL) OVER user_w AS next_user_id,
                NOT(LAG (user_id, 1, 0) OVER user_w)::BOOLEAN AS is_initial,
                NOT(LEAD(user_id, 1, 0) OVER user_w)::BOOLEAN AS is_current,
                RANK () OVER user_w AS "sequence",
                "date",
                LEAD ("date", 1,'9999-12-31 00:00:00' :: TIMESTAMP)
                    OVER user_w AS "up_to"
            FROM
                (
                    SELECT
                        *
                    FROM
                        crm_lead_changelog
                    WHERE
                        user_id IS NOT NULL
                ) AS T1 WINDOW user_w AS (
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
