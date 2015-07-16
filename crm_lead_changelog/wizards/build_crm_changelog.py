# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from logging import getLogger


_logger = getLogger(__name__)


class BuildCrmChangelog(models.TransientModel):
    """ Builds a changelog for all preexisting leads in database

    Fields:
    - assign_to: to to assign
    - user_id: selected user to assign if ``assign_to`` = ``s``

    """

    _name = 'build.crm.changelog'
    _description = u'Build changelog'

    _rec_name = 'assign_to'
    _order = 'write_date DESC'

    # ------------------------------- FIELDS ----------------------------------

    assign_to = fields.Selection(
        string='Assign to',
        required=False,
        readonly=False,
        index=False,
        default='c',
        help='Assign current lead/opportunity state to',
        selection=[
            ('c', 'User who create the record'),
            ('w', 'User who made the last change'),
            ('s', 'Choose an existing user...')]
    )

    user_id = fields.Many2one(
        string='User',
        required=False,
        readonly=False,
        index=False,
        default=lambda self: self.env.uid,
        help='Choose an user to be assigned in lead changelog',
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
            'CHECK(assign_to != \'s\' OR user_id IS NOT NULL)',
            _(u'You must choose an existing user.')
        )
    ]

    # --------------------------- PUBLIC METHODS ------------------------------

    @api.multi
    def execute(self, args):
        """ Build a changelog of each one of the existing leads/opportunities
        with the selected user.
        """

        user_id = self.user_id and self.user_id.id or 1
        opts = {'c': 'lo.create_uid', 'w': 'lo.write_uid', 's': user_id}

        opt = self.assign_to
        user_param = opt and opt in opts and opts[opt] or opts['c']

        sql_query = self._sql_update_responsible.format(user_param)
        self.sudo().env.cr.execute(sql_query)

    @api.model
    def ensure_changelog(self):

        if self.env['crm.lead'].search_count([]):
            self.sudo().env.cr.execute(self._sql_ensure_changelog)

            view_id = self.env.ref(
                'crm_lead_changelog.view_build_crm_changelog_form')
            return {
                'type': 'ir.actions.act_window',
                'name': u'Build changelog',
                'res_model': self._name,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'views': [(view_id.id, 'form')],
                'domain': [],
                'context': self.env.context,
            }

    # ----------------------------- SQL STRINGS -------------------------------

    _sql_ensure_changelog = """
       INSERT INTO crm_lead_changelog (
            stage_id,
            user_id,
            lead_id,
            create_uid,
            write_uid,
            write_date,
            "date",
            create_date,
            responsible_user_id
        ) SELECT
            stage_id,
            create_uid,
            "id",
            NULL,   -- allow to recognize preexisting leads in changelog
            NULL,   -- allow to recognize preexisting leads in changelog
            write_date,
            create_date,
            create_date,
            create_uid
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

    _sql_update_responsible = """
        UPDATE crm_lead_changelog
        SET
         responsible_user_id = {0}
        FROM
            crm_lead_changelog AS cl
        INNER JOIN crm_lead AS lo ON cl.lead_id = lo."id"
        WHERE
            cl.create_uid IS NULL
            AND cl.write_uid IS NULL
    """
