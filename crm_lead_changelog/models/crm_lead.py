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
        string='Historics',
        comodel_name='crm.lead.changelog',
        inverse_name='lead_id',
        track_visibility='onchange',
        help='Changes was made in lead'
    )  # REVISE: this field it's not suficient

    # ------------------------ METHODS OVERWRITTEN ----------------------------

    @api.model
    def create(self, values):
        """
            Create a new record for a model CrmLead
            @param values: provides a data for new record

            @return: returns a id of new record
        """
        # STEP 1: Calling parent method to perform the changes in the leads
        result = super(CrmLead, self).create(values)

        # STEP 1: Update the changelog before the leads are changed
        stage_id, user_id = self._changes_to_register(values)
        if stage_id or user_id:
            result._update_changelog(stage_id, user_id)

        return result

    @api.multi
    def write(self, values):

        # STEP 1: Update the changelog before the leads are changed
        stage_id, user_id = self._changes_to_register(values)
        if stage_id or user_id:
            self._update_changelog(stage_id, user_id)

        # STEP 2: Calling parent method to perform the changes in the leads
        return super(CrmLead, self).write(values)

    # -------------------------- AUXILIARY METHODS ----------------------------

    @api.model
    def _changes_to_register(self, values, force=False):
        return values.get('stage_id', False), values.get('user_id', False)

    @api.multi
    def _update_changelog(self, stage_id, user_id):
        log_obj = self.env['crm.lead.changelog'].sudo()
        values = {'stage_id': stage_id, 'user_id': user_id}

        _logger.warning('_update_changelog %d %d' % (stage_id, user_id))

        for record in self:
            values.update({'lead_id': record.id})
            log_obj.create(values)

