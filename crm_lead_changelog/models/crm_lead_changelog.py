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
        required=True,
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

    user_id_changed = fields.Boolean(
        string='User was changed',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help='Checked if the user was changed'
    )

    stage_id_changed = fields.Boolean(
        string='Stage of case was changed',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help='Checked if the stage of case was changed'
    )

    reason_id_changed = fields.Boolean(
        string='Reason was changed',
        required=False,
        readonly=True,
        index=False,
        default=False,
        help='Checked if the reason of stage of case was changed'
    )

    # --------------------------- SQL CONSTRAINTS -----------------------------

    _sql_constraints = [(
        'non_empty',
        'CHECK(user_id_changed OR stage_id_changed OR reason_id_changed)',
        _(u'Empty change in lead could not be registered')
    )]

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

    # -------------------------------- CRUD -----------------------------------

    @api.multi
    def write(self, values):
        """ Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise

            @param values: dict of new values to be set

            @return: True on success, False otherwise
        """

        values = self._update_changelog_values(values)
        result = super(CrmLeadChangelog, self).write(values)

        return result

    @api.model
    def create(self, values):
        """ Create a new record for a model CrmLeadChangelog
            @param values: provides a data for new record

            @return: returns a id of new record
        """

        values = self._update_changelog_values(values)
        result = super(CrmLeadChangelog, self).create(values)

        return result

    # -------------------------- AUXILIARY METHODS ----------------------------

    @api.model
    def _update_changelog_values(self, values):
        """ Set values for the Boolean fields. These fields will have a True
        when user has been changed a value or False otherwise.

        This method prevents theses fields can be updated manually too.
        """

        values.update({
            'user_id_changed': 'user_id' in values,
            'stage_id_changed': 'stage_id' in values,
            'reason_id_changed': 'reason_id' in values
        })

        return values

    # ----------------------------- SQL STRINGS -------------------------------

    _sql_ensure_changelog = """
              INSERT INTO crm_lead_changelog (
            lead_id,
            user_id,
            stage_id,
            reason_id,
            "date",
            create_uid,
            create_date,
            write_uid,
            write_date,
            user_id_changed,
            stage_id_changed,
            reason_id_changed
        ) SELECT
            "id",
            user_id,
            stage_id,
            crm_reason_id,
            create_date, -- first changelog always match with the lead creation
            NULL,        -- allow to recognize preexisting leads in changelog
            NULL,        -- allow to recognize preexisting leads in changelog
            create_uid,  -- first changelog always match with the lead creation
            create_date, -- first changelog always match with the lead creation
            TRUE,
            TRUE,
            TRUE
        FROM
            crm_lead
        WHERE
            crm_lead."id" NOT IN (
                SELECT
                    lead_id
                FROM
                    crm_lead_changelog
            )
    """

