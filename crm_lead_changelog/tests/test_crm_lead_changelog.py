# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp.tests.common import TransactionCase, SingleTransactionCase
from psycopg2 import IntegrityError

from logging import getLogger

#pylint: disable=I0011,C0103
_logger = getLogger(__name__)


class TestCrmLeadChangelog(TransactionCase):
    """ This class contains the unit tests for 'CrmLeadChangelog'.
    """

    def setUp(self):
        """ Calls the base class setUp and initialices the attributes
        """

        super(TestCrmLeadChangelog, self).setUp()

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

    def test_ensure_changelog(self):
        """ Test is the first changelog record of all the leads has the three
        boolean fields set to True. This ensures that all preexisting leads in
        the database have a changelog recors as they have been created after
        this module had been installed.
        """

        lead_ids = self._lead_obj.search_read([], ['id'])

        for lead_item in lead_ids:
            lead_id = lead_item['id']

            domain = [('lead_id', '=', lead_id)]
            result = self._changelog_obj.search( \
                domain, order="date ASC", limit=1)

            self.assertTrue(
                result.user_id_changed and \
                result.stage_id_changed and \
                result.reason_id_changed,
                msg='First changelog for %d with some False field' % lead_id
            )

    def test_write(self):
        """ Not important """
        pass

    def test_create(self):
        """ Test if create method:
            1.- saves new record in database

            More tests will be in single transactions
        """
        stage_id = self.stage_id.id
        lead_id = self.lead_id.id
        result = None

        values = {'stage_id': stage_id, 'lead_id': lead_id}
        result = self._changelog_obj.create(values)

        self.assertIsInstance(
            result,
            type(self._changelog_obj),
            msg='The expected new crm_lead_changelog has not been created'
        )

    def test__update_changelog_values(self):
        """ Test if _update_changelog values:
        1.- Returns the same value in result and _in_out values argument
        2.- Updates boolean values in accordance with given arguments
        3.- Prevents user can force invalid boolean value

        This test will be performed with each one of the valid arguments and
        with a cumulative dictionary.
        """

        error1_msg = 'result is different than updated (_in_out) dictionary'
        error2_msg = '_update_changelog unexpected result'
        doing_msg = '_update_changelog({}) = {}'

        values = dict(
            user_id=self.user_id,
            stage_id=self.stage_id,
            reason_id=self.reason_id
        )

        no_changed = {
            'user_id_changed': False,
            'stage_id_changed': False,
            'reason_id_changed': False,
        }

        # Deliberated access to a private  method
        update_changelog_values = \
            getattr(self._changelog_obj, '_update_changelog_values')

        cumulative_values = {}
        cumulative_expected = no_changed.copy()

        for key, value in values.iteritems():
            expected = no_changed.copy()
            expected_to_add = {u'{}_changed'.format(key): True}

            values = {key:value}
            cumulative_values.update({key:value})

            expected.update(values.items()+expected_to_add.items())
            cumulative_expected.update(values.items()+expected_to_add.items())

            # TEST 1: Each one of the parameters without any boolean field
            _in_out = values.copy()  # Preserve values to display in log
            result = update_changelog_values(_in_out)

            self._log(0, doing_msg, values, result)
            self.assertDictEqual(_in_out, result, error1_msg)
            self.assertDictEqual(expected, result, error2_msg)

            # TEST 2: Each one of the parameteres with wrong boolean values
            _in_out = values.copy()
            _in_out.update(self._inverted_dictionary(no_changed))
            result = update_changelog_values(_in_out)

            self._log(0, doing_msg, values, result)
            self.assertDictEqual(_in_out, result, error1_msg)
            self.assertDictEqual(expected, result, error2_msg)

            # TEST 3: Cumulative parameters dictionary without boolean values
            _in_out = cumulative_values.copy()  # Preserve to display in log
            result = update_changelog_values(_in_out)

            self._log(0, doing_msg, cumulative_values, result)
            self.assertDictEqual(_in_out, result, error1_msg)
            self.assertDictEqual(cumulative_expected, result, error2_msg)

            # TEST 4: Cumulative parameters dictionary with wrong bool values
            _in_out = cumulative_values.copy()
            _in_out.update(self._inverted_dictionary(no_changed))
            result = update_changelog_values(_in_out)

            self._log(0, doing_msg, cumulative_values, result)
            self.assertDictEqual(_in_out, result, error1_msg)
            self.assertDictEqual(cumulative_expected, result, error2_msg)

    @classmethod
    def _inverted_dictionary(cls, _in_dict):
        """ Returns a dictionary with all boolean items inverted
        :param _in_dict: (in) dictionary to get values
        :return: copy of the dictionary with inverted boolean items
        """
        _out_dict = _in_dict.copy()
        btype = type(False)

        for key, value in _out_dict.iteritems():
            if isinstance(value, btype):
                _out_dict[key] = not value

        return _out_dict

    @classmethod
    def _log(cls, level, msg_format, *args, **kwargs):
        """ Outputs an formated string in log

            :param level (int): 0=> debug, 1=> info, 2=> warning, 3=> error
            :param message (basestring): name of the message
        """

        methods = ['debug', 'info', 'warning', 'error']
        log = getattr(_logger, methods[level])

        msg = msg_format.format(*args, **kwargs)
        log(msg)


class TestCrmLeadChangelogCreateWithEmptyLead(SingleTransactionCase):
    """ Test if crm.lead.changelog,create method fails when no lead will be
    passed as argument (Expected behavior). Test will be executed in a
    ``SingleTransactionCase`` because the SQL transactions should break.
    """

    def setUp(self):
        """ Calls the base class setUp and initialices the attributes """

        super(TestCrmLeadChangelogCreateWithEmptyLead, self).setUp()

        self.changelog_obj = self.env['crm.lead.changelog']
        self.stage_xid = 'crm.stage_lead1'
        self.stage_id = self.env.ref(self.stage_xid)


    def test_create_with_empty_lead(self):
        """ Checks if the create_with_empty_lead works properly
        """

        self.assertRaises(
            IntegrityError,
            self.changelog_obj.create,
            {'stage_id': self.stage_id.id}
        )


class TestCrmLeadChangelogCreateWithNoChanges(SingleTransactionCase):
    """ Test if crm.lead.changelog,create method fails when no changes will
    be registered (Expected behavior). Test will be executed in a
    ``SingleTransactionCase`` because the SQL transactions should break.
    """

    def setUp(self):
        """ Calls the base class setUp and initialices the attributes """

        super(TestCrmLeadChangelogCreateWithNoChanges, self).setUp()

        self.changelog_obj = self.env['crm.lead.changelog']
        self.lead_xid = 'crm.crm_case_1'
        self.lead_id = self.env.ref(self.lead_xid)


    def test_create_with_no_changes(self):
        """ Checks if the create_with_empty_lead works properly
        """

        self.assertRaises(
            IntegrityError,
            self.changelog_obj.create,
            {'lead_id': self.lead_id.id}
        )
