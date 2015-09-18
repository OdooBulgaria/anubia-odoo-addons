# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api

import logging


_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    """ Extended model to add a change log behavior to register changes in
    ``user_id`` and ``stage_id`` fields.
    """

    _inherit = 'crm.lead'

    _fnames_to_track = ('user_id', 'stage_id', 'crm_reason_id')

    # --------------------------- ENTITY FIELDS -------------------------------

    changelog_ids = fields.One2many(
        string='Changelog',
        comodel_name='crm.lead.changelog',
        inverse_name='lead_id',
        track_visibility='onchange',
        help='Changes made in lead',
        search=lambda self, op, vl: self._search_stage_changelog_ids(op, vl)
    )

    # --------------------------- COMPUTED FIELDS -----------------------------

    user_changelog_ids = fields.One2many(
        string='Salesperson changelog',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Changes made in salesperson',
        comodel_name='crm.lead.changelog',
        inverse_name='lead_id',
        domain=[('user_id', '<>', False)],
        context={},
        auto_join=False,
        limit=None,
        compute=lambda self: self._compute_user_changelog_ids(),
        search=lambda self, op, vl: self._search_user_changelog_ids(op, vl)
    )

    stage_changelog_ids = fields.One2many(
        string='Stage of case changelog',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Changes made in stage of case',
        comodel_name='crm.lead.changelog',
        inverse_name='lead_id',
        domain=[('stage_id', '<>', False)],
        context={},
        auto_join=False,
        limit=None,
        compute=lambda self: self._compute_stage_changelog_ids(),
        search=lambda self, op, vl: self._search_stage_changelog_ids(op, vl)
    )

    reason_changelog_ids = fields.One2many(
        string='Reason changelog',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Changes made in reason',
        comodel_name='crm.lead.changelog',
        inverse_name='lead_id',
        domain=[('reason_id', '<>', False)],
        context={},
        auto_join=False,
        limit=None,
        compute=lambda self: self._compute_reason_changelog_ids(),
        search=lambda self, op, vl: self._search_reason_changelog_ids(op, vl)
    )

    # --------------------------- COMPUTE METHODS -----------------------------

    @api.multi
    @api.depends('changelog_ids')
    def _compute_user_changelog_ids(self):
        """ Fills ``user_changelog_ids`` with related changelogs filtering
        those to which have assigned ``user_id``
        """

        for record in self:
            record.user_changelog_ids = record.changelog_ids.filtered(
                lambda x: x.user_id)

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
    def _compute_reason_changelog_ids(self):
        """ Fills ``reason_changelog_ids`` with related changelogs filtering
        those to which have assigned ``reason_id``
        """

        for record in self:
            record.user_changelog_ids = record.changelog_ids.filtered(
                lambda x: x.reason_id)

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
    def _search_reason_changelog_ids(self, operator, value):
        """ Search method for ``reason_changelog_ids`` computed field.

        Searches ``value`` in all related changelogs in which the ``reason_id``
        has changed.
        """

        changelog_obj = self.env['crm.lead.changelog']
        changelog_obj.check_access_rights('read')

        changelog_domain = [('reason_id', operator, value)]
        changelog_set = changelog_obj.search(changelog_domain)

        _ids = [x.lead_id and x.lead_id.id or 0 for x in changelog_set]

        return [('id', 'in', [_ids])]

    # -------------------------- ONCHANGE ENVENTS -----------------------------

    @api.onchange('changelog_ids')
    def _onchange_changelog_ids(self):
        """ Recomputes those fields which depend from ``changelog_ids``
        """

        self._compute_user_changelog_ids()
        self._compute_stage_changelog_ids()
        self._compute_reason_changelog_ids()

    @api.onchange('user_id')
    def _onchange_user_id(self):
        """ Recomputes those fields which depend from ``user_id``
        """

        self._compute_user_changelog_ids()

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        """ Recomputes those fields which depend from ``stage_id``
        """

        self._compute_stage_changelog_ids()

    @api.onchange('crm_reason_id')
    def _onchange_crm_reason_id(self):
        """ Recomputes those fields which depend from ``crm_reason_id``
        """

        self._compute_reason_changelog_ids()

    # ------------------------ METHODS OVERWRITTEN ----------------------------

    @api.model
    def create(self, values):
        """ Adds a new changelog record to register the assigned ``stage_id``,
        ``user_id`` and ``reason_id``.
        """

        # STEP 1: Calling parent method to perform the changes in the leads
        result = super(CrmLead, self).create(values)

        # STEP 2: Update the changelog after the leads are changed
        self._update_changelog(values)

        return result

    @api.multi
    def write(self, values):
        """ Adds a new changelog record to register the assigned ``stage_id``
        ``user_id`` and ``reason_id``.
        """

        # STEP 1: Calling parent method to perform the changes in the leads
        result = super(CrmLead, self).write(values)

        # STEP 2: Update the changelog after the leads are changed
        self._update_changelog(values)

        return result

    # -------------------------- AUXILIARY METHODS ----------------------------

    @api.model
    def _get_fields_to_track(self, values):
        fnames = self._fnames_to_track
        values = dict((k, v) for k, v in values.items() if k in fnames)

        # PATCH: fields should have the same name
        if 'crm_reason_id' in values:
            values['reason_id'] = values.pop('crm_reason_id')

        return values

    @api.multi
    def _update_changelog(self, values):
        """ Create a changelog record for each one of the leads in recordset
        """

        fields_to_track = self._get_fields_to_track(values)

        self._log(0, 'fields_to_track {}', fields_to_track)

        if fields_to_track:

            log_obj = self.env['crm.lead.changelog']

            # TODO: Check if lines below works
            fields_to_track.update(
                {'create_uid': self.env.uid, 'write_uid': self.env.uid}
            )

            for record in self:
                fields_to_track.update({'lead_id': record.id})
                log_obj.create(fields_to_track)

    def _log(self, level, msg_format, *args, **kwargs):
        """ Outputs an formated string in log

            :param level (int): 0=> debug, 1=> info, 2=> warning, 3=> error
            :param message (basestring): name of the message
        """

        methods = ['debug', 'info', 'warning', 'error']
        log = getattr(_logger, methods[level])

        msg = msg_format.format(*args, **kwargs)
        log(msg)
