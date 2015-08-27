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


class CrmLeadChangelogUpdate(models.Model):
    """ User id change log for all leads/opportunities ``
    """

    _name = 'crm.lead.changelog.update'
    _description = u'Crm lead changelog update'

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
        help=('Stage of case assigned to the lead in the previous change')
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
        help=('Stage of case who has been assigned to the lead in the next '
              'change')
    )

    prev_reason_id = fields.Many2one(
        string='Previous salesperson',
        required=False,
        readonly=True,
        index=False,
        default=None,
        comodel_name='crm.stage.reason',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help=('Salesperson assigned to the lead in the previous change')
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

    next_reason_id = fields.Many2one(
        string='Next salesperson',
        required=False,
        readonly=True,
        index=False,
        default=None,
        comodel_name='crm.stage.reason',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        help=('Salesperson who has been assigned to the lead in the next '
              'change')
    )

    item_id = fields.Reference(
        string='Item changed',
        required=False,
        readonly=True,
        index=False,
        default=0,
        help='Item has been changed',
        selection=[
            ('res.users', 'Salesperson'),
            ('crm.case.stage', 'Stage of case'),
            ('crm.stage.reason', 'Reason')
        ]
    )

    ctype = fields.Selection(
        string='Type',
        required=False,
        readonly=True,
        index=False,
        default=False,
        help=False,
        selection=[
            ('user_id', 'Salesperson'),
            ('stage_id', 'Stage of case'),
            ('reason_id', 'Reason')
        ]
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
    @api.depends('lead_id', 'item_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = ' - '.join(
                filter(None, (record.lead_id.name, record.item_id.name)))

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
    @api.onchange('item_id')
    def _onchange_user_id(self):
        self._compute_display_name()

    def init(self, cr):
        """ Build database view which will be used as module origin

            :param cr: database cursor
        """

        self._sql_query = """
         WITH updates AS (
             WITH user_updates AS (
                 SELECT t1.create_uid,
                    t1.create_date,
                    t1.write_uid,
                    t1.write_date,
                    t1.lead_id,
                    lag(t1.user_id, 1, NULL::integer)
                        OVER user_w AS prev_user_id,
                    t1.user_id,
                    lead(t1.user_id, 1, NULL::integer)
                        OVER user_w AS next_user_id,
                    NULL::integer AS prev_stage_id,
                    NULL::integer AS stage_id,
                    NULL::integer AS next_stage_id,
                    NULL::integer AS prev_reason_id,
                    NULL::integer AS reason_id,
                    NULL::integer AS next_reason_id,
                    concat('res.users,', t1.user_id) AS item_id,
                    'user_id'::text AS ctype,
                    (NOT (lag(t1.user_id, 1, 0)
                        OVER user_w)::boolean) AS is_initial,
                    (NOT (lead(t1.user_id, 1, 0)
                        OVER user_w)::boolean) AS is_current,
                    rank() OVER user_w AS sequence,
                    t1.date,
                    lead(t1.date, 1, '9999-12-31 00:00:00'::timestamp
                        without time zone) OVER user_w AS up_to
                   FROM ( SELECT crm_lead_changelog.id,
                            crm_lead_changelog.create_uid,
                            crm_lead_changelog.stage_id,
                            crm_lead_changelog.user_id,
                            crm_lead_changelog.lead_id,
                            crm_lead_changelog.reason_id,
                            crm_lead_changelog.write_uid,
                            crm_lead_changelog.write_date,
                            crm_lead_changelog.date,
                            crm_lead_changelog.create_date
                           FROM crm_lead_changelog
                          WHERE (crm_lead_changelog.user_id IS NOT NULL)) t1
                  WINDOW user_w AS (PARTITION BY t1.lead_id ORDER BY t1.date)
                  ORDER BY t1.lead_id, t1.date DESC
                ), stage_updates AS (
                 SELECT t1.create_uid,
                    t1.create_date,
                    t1.write_uid,
                    t1.write_date,
                    t1.lead_id,
                    NULL::integer AS prev_user_id,
                    NULL::integer AS user_id,
                    NULL::integer AS next_user_id,
                    lag(t1.stage_id, 1, NULL::integer)
                        OVER stage_w AS prev_stage_id,
                    t1.stage_id,
                    lead(t1.stage_id, 1, NULL::integer)
                        OVER stage_w AS next_stage_id,
                    NULL::integer AS prev_reason_id,
                    NULL::integer AS reason_id,
                    NULL::integer AS next_reason_id,
                    concat('crm.case.stage,', t1.stage_id) AS item_id,
                    'stage_id'::text AS ctype,
                    (NOT (lag(t1.stage_id, 1, 0)
                        OVER stage_w)::boolean) AS is_initial,
                    (NOT (lead(t1.stage_id, 1, 0)
                        OVER stage_w)::boolean) AS is_current,
                    rank() OVER stage_w AS sequence,
                    t1.date,
                    lead(t1.date, 1, '9999-12-31 00:00:00'::timestamp
                            without time zone) OVER stage_w AS up_to
                   FROM ( SELECT crm_lead_changelog.id,
                            crm_lead_changelog.create_uid,
                            crm_lead_changelog.stage_id,
                            crm_lead_changelog.user_id,
                            crm_lead_changelog.lead_id,
                            crm_lead_changelog.reason_id,
                            crm_lead_changelog.write_uid,
                            crm_lead_changelog.write_date,
                            crm_lead_changelog.date,
                            crm_lead_changelog.create_date
                           FROM crm_lead_changelog
                          WHERE (crm_lead_changelog.stage_id IS NOT NULL)) t1
                  WINDOW stage_w AS (PARTITION BY t1.lead_id ORDER BY t1.date)
                  ORDER BY t1.lead_id, t1.date DESC
                ), reason_updates AS (
                 SELECT t1.create_uid,
                    t1.create_date,
                    t1.write_uid,
                    t1.write_date,
                    t1.lead_id,
                    NULL::integer AS prev_user_id,
                    NULL::integer AS user_id,
                    NULL::integer AS next_user_id,
                    NULL::integer AS prev_stage_id,
                    NULL::integer AS stage_id,
                    NULL::integer AS next_stage_id,
                    lag(t1.reason_id, 1, NULL::integer)
                        OVER reason_w AS prev_reason_id,
                    t1.reason_id,
                    lead(t1.reason_id, 1, NULL::integer)
                        OVER reason_w AS next_reason_id,
                    concat('crm.stage.reason,', t1.reason_id) AS item_id,
                    'reason_id'::text AS ctype,
                    (NOT (lag(t1.reason_id, 1, 0)
                        OVER reason_w)::boolean) AS is_initial,
                    (NOT (lead(t1.reason_id, 1, 0)
                        OVER reason_w)::boolean) AS is_current,
                    rank() OVER reason_w AS sequence,
                    t1.date,
                    lead(t1.date, 1, '9999-12-31 00:00:00'::timestamp
                        without time zone) OVER reason_w AS up_to
                   FROM ( SELECT crm_lead_changelog.id,
                            crm_lead_changelog.create_uid,
                            crm_lead_changelog.stage_id,
                            crm_lead_changelog.user_id,
                            crm_lead_changelog.lead_id,
                            crm_lead_changelog.reason_id,
                            crm_lead_changelog.write_uid,
                            crm_lead_changelog.write_date,
                            crm_lead_changelog.date,
                            crm_lead_changelog.create_date
                           FROM crm_lead_changelog
                          WHERE (crm_lead_changelog.reason_id IS NOT NULL)) t1
                  WINDOW reason_w AS (PARTITION BY t1.lead_id ORDER BY t1.date)
                  ORDER BY t1.lead_id, t1.date DESC
                )
                 SELECT user_updates.create_uid,
                    user_updates.create_date,
                    user_updates.write_uid,
                    user_updates.write_date,
                    user_updates.lead_id,
                    user_updates.prev_user_id,
                    user_updates.user_id,
                    user_updates.next_user_id,
                    user_updates.prev_stage_id,
                    user_updates.stage_id,
                    user_updates.next_stage_id,
                    user_updates.prev_reason_id,
                    user_updates.reason_id,
                    user_updates.next_reason_id,
                    user_updates.item_id,
                    user_updates.ctype,
                    user_updates.is_initial,
                    user_updates.is_current,
                    user_updates.sequence,
                    user_updates.date,
                    user_updates.up_to
                   FROM user_updates
                UNION
                 SELECT stage_updates.create_uid,
                    stage_updates.create_date,
                    stage_updates.write_uid,
                    stage_updates.write_date,
                    stage_updates.lead_id,
                    stage_updates.prev_user_id,
                    stage_updates.user_id,
                    stage_updates.next_user_id,
                    stage_updates.prev_stage_id,
                    stage_updates.stage_id,
                    stage_updates.next_stage_id,
                    stage_updates.prev_reason_id,
                    stage_updates.reason_id,
                    stage_updates.next_reason_id,
                    stage_updates.item_id,
                    stage_updates.ctype,
                    stage_updates.is_initial,
                    stage_updates.is_current,
                    stage_updates.sequence,
                    stage_updates.date,
                    stage_updates.up_to
                   FROM stage_updates
                UNION
                 SELECT reason_updates.create_uid,
                    reason_updates.create_date,
                    reason_updates.write_uid,
                    reason_updates.write_date,
                    reason_updates.lead_id,
                    reason_updates.prev_user_id,
                    reason_updates.user_id,
                    reason_updates.next_user_id,
                    reason_updates.prev_stage_id,
                    reason_updates.stage_id,
                    reason_updates.next_stage_id,
                    reason_updates.prev_reason_id,
                    reason_updates.reason_id,
                    reason_updates.next_reason_id,
                    reason_updates.item_id,
                    reason_updates.ctype,
                    reason_updates.is_initial,
                    reason_updates.is_current,
                    reason_updates.sequence,
                    reason_updates.date,
                    reason_updates.up_to
                   FROM reason_updates
                )
         SELECT row_number() OVER () AS id,
            updates.create_uid,
            updates.create_date,
            updates.write_uid,
            updates.write_date,
            updates.lead_id,
            updates.prev_user_id,
            updates.user_id,
            updates.next_user_id,
            updates.prev_stage_id,
            updates.stage_id,
            updates.next_stage_id,
            updates.prev_reason_id,
            updates.reason_id,
            updates.next_reason_id,
            updates.item_id,
            updates.ctype,
            updates.is_initial,
            updates.is_current,
            updates.sequence,
            updates.date,
            updates.up_to
           FROM updates
        """

        drop_view_if_exists(cr, self._table)

        cr.execute(
            'create or replace view {} as ({})'.format(
                self._table,
                self._sql_query
            )
        )
