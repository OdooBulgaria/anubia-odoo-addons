# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.tests.common import TransactionCase

from logging import getLogger


_logger = getLogger(__name__)


class TestCrmLead(TransactionCase):
    """ This class contains the unit tests for 'CrmLead'.
    """

    def setUp(self):
        """ Calls the base class setUp and initialices the attributes
        """

        super(TestCrmLead, self).setUp()

        self.user_xid = 'base.user_root'
        self.stage_xid = 'crm.stage_lead1'
        self.reason_xid = 'crm_case_stage_reason.crm_stage_reason_demo_1'
        self.lead_xid = 'crm.crm_case_1'

        self.user_id = self.env.ref(self.user_xid)
        self.stage_id = self.env.ref(self.stage_xid)
        self.reason_id = self.env.ref(self.reason_xid)
        self.lead_id = self.env.ref(self.lead_xid)

        self._lead_obj = self.env['crm.lead']
        self._changelog_obj = self.env['crm.lead.changelog']

    # def _compute_user_changelog_ids(self):
    # def _compute_stage_changelog_ids(self):
    # def _compute_reason_changelog_ids(self):
    # def _search_changelog_ids(self, operator, value):
    # def _search_user_changelog_ids(self, operator, value):
    # def _search_stage_changelog_ids(self, operator, value):
    # def _search_reason_changelog_ids(self, operator, value):
    # def _onchange_changelog_ids(self):
    # def _onchange_user_id(self):
    # def _onchange_stage_id(self):
    # def _onchange_crm_reason_id(self):

    def test_create(self):
        pass

    def test_write(self):
        pass

    def test__get_fields_to_track(self):
        _in_values = {
            'user_id': self.user_id.id,
            'stage_id': self.stage_id.id,
            'crm_reason_id': self.reason_id.id
        }

        expected_filled = _in_values.copy()
        expected_filled['reason_id'] = expected_filled.pop('crm_reason_id')

        expected_empty = {'user_id': None, 'stage_id': None, 'reason_id': None}

        # Deliberated access to a private  method
        get_fields_to_track = getattr(self._lead_obj, '_get_fields_to_track')

        result = get_fields_to_track(_in_values)
        self.assertDictEqual(
            expected_filled,
            result,
            msg='test__get_fields_to_track fails'
        )

        result = get_fields_to_track({}, force_all=True)
        self.assertDictEqual(
            expected_empty,
            result,
            msg='test__get_fields_to_track fails'
        )

    def test__update_changelog(self):

        lead_id = self.lead_id

        _in_values = {
            'user_id': self.user_id.id,
            'stage_id': self.stage_id.id,
            'crm_reason_id': self.reason_id.id
        }
        update_changelog_values = \
            getattr(self.lead_id, '_update_changelog')

        result = update_changelog_values(_in_values)
        self.assertTrue(
            result.user_id.id == _in_values['user_id'] and
            result.stage_id.id == _in_values['stage_id'] and
            result.reason_id.id == _in_values['crm_reason_id'],
            msg='_update_changelog fails')

    def test__log(self):
        pass

