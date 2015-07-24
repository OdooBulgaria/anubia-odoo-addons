# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api
from openerp.tools.translate import _

import logging


_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    """ Extended model to add a change log behavior to register changes in
    ``user_id`` and ``stage_id`` fields.
    """

    _inherit = 'crm.lead'

    # --------------------------- ENTITY FIELDS -------------------------------

    changelog_ids = fields.One2many(
        string='Changelog',
        comodel_name='crm.lead.changelog',
        inverse_name='lead_id',
        track_visibility='onchange',
        help='Changes was made in lead',
        search=lambda self, op, vl: self._search_stage_changelog_ids(op, vl)
    )

    # --------------------------- COMPUTED FIELDS -----------------------------

    stage_changelog_ids = fields.One2many(
        string='Stage of case changelog',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Changes was made in stage of case',
        comodel_name='crm.lead.changelog',
        inverse_name='lead_id',
        domain=[('stage_id', '<>', False)],
        context={},
        auto_join=False,
        limit=None,
        compute=lambda self: self._compute_stage_changelog_ids(),
        search=lambda self, op, vl: self._search_stage_changelog_ids(op, vl)
    )

    user_changelog_ids = fields.One2many(
        string='Salesperson changelog',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Changes was made in salesperson',
        comodel_name='crm.lead.changelog',
        inverse_name='lead_id',
        domain=[('user_id', '<>', False)],
        context={},
        auto_join=False,
        limit=None,
        compute=lambda self: self._compute_user_changelog_ids(),
        search=lambda self, op, vl: self._search_user_changelog_ids(op, vl)
    )

    # --------------------------- COMPUTE METHODS -----------------------------

    @api.multi
    @api.depends('changelog_ids')
    def _compute_stage_changelog_ids(self):
        """ Fills ``stage_changelog_ids`` with related changelogs filtering
        those which have ``stage_id``
        """

        for record in self:
            record.stage_changelog_ids = record.changelog_ids.filtered(
                lambda x: x.stage_id)

    @api.multi
    @api.depends('changelog_ids')
    def _compute_user_changelog_ids(self):
        """ Fills ``user_changelog_ids`` with related changelogs filtering
        those to which have assigned ``user_id``
        """

        for record in self:
            record.user_changelog_ids = record.changelog_ids.filtered(
                lambda x: x.user_id)

    # --------------------------- SEARCH METHODS ------------------------------

    @api.model
    def _search_changelog_ids(self, operator, value):
        """ Search method for computed field ``changelog_ids``
        Searches ``value`` in all related changelogs
        """

        changelog_obj = self.env['crm.lead.changelog']
        changelog_obj.check_access_rights('read')

        changelog_domain = [('date', operator, value)]
        changelog_set = changelog_obj.search(changelog_domain)

        _ids = [x.lead_id and x.lead_id.id or 0 for x in changelog_set]

        return [('id', 'in', [_ids])]

    @api.model
    def _search_stage_changelog_ids(self, operator, value):
        """ Search method for computed field ``user_changelog_ids``
        Searches ``value`` in all related changelogs in which the ``stage_id``
        has changed
        """

        changelog_obj = self.env['crm.lead.changelog']
        changelog_obj.check_access_rights('read')

        changelog_domain = [('stage_id', operator, value)]
        changelog_set = changelog_obj.search(changelog_domain)

        _ids = [x.lead_id and x.lead_id.id or 0 for x in changelog_set]

        return [('id', 'in', [_ids])]

    @api.model
    def _search_user_changelog_ids(self, operator, value):
        """ Search method for ``user_changelog_ids`` computed field.

        Searches ``value`` in all related changelogs in which the ``user_id``
        has changed.
        """

        changelog_obj = self.env['crm.lead.changelog']
        changelog_obj.check_access_rights('read')

        changelog_domain = [('user_id', operator, value)]
        changelog_set = changelog_obj.search(changelog_domain)

        _ids = [x.lead_id and x.lead_id.id or 0 for x in changelog_set]

        return [('id', 'in', [_ids])]

    # -------------------------- ONCHANGE ENVENTS -----------------------------

    @api.onchange('changelog_ids')
    def _onchange_changelog_ids(self):
        """ Recomputes those fields which depend from ``changelog_ids``
        """

        self._compute_stage_changelog_ids()
        self._compute_user_changelog_ids()

    # ------------------------ METHODS OVERWRITTEN ----------------------------

    @api.model
    def create(self, values):
        """ Adds a new changelog record to register the assigned ``stage_id``
        and ``user_id``.
        """

        # STEP 1: Calling parent method to perform the changes in the leads
        result = super(CrmLead, self).create(values)

        # STEP 1: Update the changelog before the leads are changed
        stage_id, user_id = self._changes_to_register(values)
        if stage_id or user_id:  # needless, stage_id always appears on create
            result._update_changelog(stage_id, user_id)

        return result

    @api.multi
    def write(self, values):
        """ Adds a new changelog record to register the assigned ``stage_id``
        and ``user_id``.
        """

        # STEP 1: Update the changelog before the leads are changed
        stage_id, user_id = self._changes_to_register(values)
        if stage_id or user_id:
            self._update_changelog(stage_id, user_id)

        # STEP 2: Calling parent method to perform the changes in the leads
        return super(CrmLead, self).write(values)

    # -------------------------- AUXILIARY METHODS ----------------------------

    @api.model
    def _changes_to_register(self, values):
        """ Return a tuple with ``stage_id`` and ``user_id`` values (Integers)

        :param values: dictionary from create or write methods.
        :return: tuple (stage_id, user_id); each one of the item could be False
        """

        return values.get('stage_id', False), values.get('user_id', False)

    @api.multi
    def _update_changelog(self, stage_id, user_id):
        """ Create a changelog record for each one of the leads in recordset

        :param stage_id (integer): id of the stage or False
        :param user_id (integer): id of the user (salesperson) or False
        """

        log_obj = self.env['crm.lead.changelog']

        values = {'stage_id': stage_id, 'user_id': user_id}
        values.update({'create_uid': self.env.uid, 'write_uid': self.env.uid})

        for record in self:
            values.update({'lead_id': record.id})
            log_obj.create(values)
