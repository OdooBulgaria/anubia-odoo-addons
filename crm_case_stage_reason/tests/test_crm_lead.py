# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

#pylint: disable=I0011,C0103,F0401

from openerp.tests.common import TransactionCase

from logging import getLogger

_logger = getLogger(__name__)


class TestCrmLead(TransactionCase):
    """ This class contains the unit tests for 'crm.lead'.

        Below is the stage/reasons tree

        ├───New --------------------- (1)
        │   ├───Customer call·················(1)
        │   ├───Contact form··················(2)
        │   └───Business venture··············(3)
        ├───Dead -------------------- (2)
        │   ├───Invalid customer profile······(4)
        │   └───Unable to contact·············(5)
        ├───Proposition ------------- (4)
        │   ├───Specific Requirements·········(6)
        │   └───General terms not accepted····(8)
        ├───Negotiation ------------- (5)
        │   ├───Valued customer···············(7)
        │   └───General terms not accepted····(8)
        ├───Won --------------------- (6)
        │   └───Agreement·····················(9)
        └───Lost -------------------- (7)
            ├───Unable to contact·············(5)
            └───Rejected······················(10)
    """

    def setUp(self):
        """ Setting up object which will perform the tests """

        rsxid = 'crm_case_stage_reason.crm_stage_reason_demo_%s'
        stxid = 'crm.stage_lead%s'

        super(TestCrmLead, self).setUp()

        self._lead_obj = self.env['crm.lead']

        # crm.case.stage(2,7) {2: (5,3), 7: (5,4)/4}
        self.rs4 = self.env.ref(rsxid % 4)
        self.st2 = self.env.ref(stxid % 2)
        self.st7 = self.env.ref(stxid % 7)

        self._chances = [
            {},
            {'crm_reason_id': None},
            {'crm_reason_id': self.rs4.id},
            {'stage_id': None},
            {'stage_id': None, 'crm_reason_id': None},
            {'stage_id': None, 'crm_reason_id': self.rs4.id},
            {'stage_id': self.st7.id},
            {'stage_id': self.st7.id, 'crm_reason_id': None},
            {'stage_id': self.st7.id, 'crm_reason_id': self.rs4.id},
        ]

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

    def test__get_stage_and_reason_values(self):
        """ Checks if the _get_stage_and_reason_values works properly

        | stage_id      | crm_reason_id | Result         |
        | ------------- | ------------- | -------------- |
        |               |               | (False, False) |
        |               | None          | (False, None   |
        |               | 1             | (False, 1)     |
        | None          |               | (None, False)  |
        | None          | None          | (None, None)   |
        | None          | 1             | (None, 1)      |
        | 1             |               | (1, False)     |
        | 1             | None          | (1, None)      |
        | 1             | 1             | (1, 1)         |
        """

        # Deliberate access to the private methods will be tested
        get_stage_and_reason_values = getattr(
            self._lead_obj, '_get_stage_and_reason_values')

        # STEP 1: Define the expected results
        results = [
            (False, False),
            (False, None),
            (False, self.rs4.id),
            (None, False),
            (None, None),
            (None, self.rs4.id),
            (self.st7.id, False),
            (self.st7.id, None),
            (self.st7.id, self.rs4.id),
        ]

        counter = 0
        for values in self._chances:

            # STEP 2: Compute results calling method and print results
            obtained = get_stage_and_reason_values(values),
            expected = results[counter],
            self._log(0, 'obtainded {} / expected {}', obtained, expected)

            # STEP 3: Compare otained and expected results
            self.assertTupleEqual(
                obtained,
                expected,
                msg='_get_stage_and_reason_values(%s) fails!' % (values)
            )

            # STEP 4: Counter keep pointer to the expected results list
            counter += 1

    def test__get_reasons_from_stage(self):
        """ Checks if the _reasons_from_stage works properly
        """

        # Deliberate access to the private methods will be tested
        reasons_from_stage = getattr(self._lead_obj, '_get_reasons_from_stage')

        # STEP 1: Load all stages
        stage_domain = []
        stage_obj = self.env['crm.case.stage']
        stage_set = stage_obj.search(stage_domain)

        for stage in stage_set:

            # STEP 2: Get reasons and default reason from current stage
            reason_ids = stage.crm_reason_ids.mapped('id')
            default_reason_id = stage.default_crm_reason_id.id or None

            # STEP 3: Call tested method for current stage
            result = reasons_from_stage(stage.id)

            # STEP 4: compare reasons earned from stage and tested method
            self._log(0, 'obtained: {} / expected: {}', result[0], reason_ids)
            self.assertSetEqual(
                set(result[0]),
                set(reason_ids),
                msg='_reasons_from_stage(%s) fails!' % stage.id
            )

            # STEP 4: compare the default reason got from stage and method
            self._log(0, 'obtained: {} / expected: {}', result[0], reason_ids)
            self.assertEqual(
                result[1],
                default_reason_id,
                msg='_reasons_from_stage(%s) wrong default reason!' % stage.id
            )

    def test__get_stages_from_reason(self):
        """ Checks if the _stages_from_reason works properly
        """

        # Deliberate access to the private methods will be tested
        stages_from_reason = getattr(self._lead_obj, '_get_stages_from_reason')

        # STEP 1: Load all reasons
        reason_domain = []
        reason_obj = self.env['crm.stage.reason']
        reason_set = reason_obj.search(reason_domain)

        for reason in reason_set:

            # STEP 2: Get reasons and default reason from current reason
            stage_ids = reason.crm_stages_ids.mapped('id')

            # STEP 3: Call tested method for current reason
            result = stages_from_reason(reason.id)

            # STEP 4: compare stages earned from reason and tested method
            self._log(0, 'stages: {} / {}', result, stage_ids)
            self.assertSetEqual(
                set(result),
                set(stage_ids),
                msg='_stages_from_reasone(%s) fails!' % reason.id
            )

    def _expected_values(self, lead_dict, values, expected):
        """ Compares result from _ensure_reason_for_stage method with an expected
        dictionary using a dictionary of different lead records

        :param lead_dict: dictionary {name:crm.lead,...}
        :param values: dictionary with the values will be passed to the method
        :param expected: dictionary with the values will be expected as result
        """

        msg = u'%s._ensure_reason_for_stage fails with %s'

        for key, lead_obj in lead_dict.iteritems():
            self._log(0, '{}._ensure_reason_for_stage({}) (expecting...)', key, values)
            ensure_values = getattr(lead_obj, '_ensure_reason_for_stage')
            result = ensure_values(values)
            self.assertDictEqual(expected, result, msg % (key, values))

    def _expected_fail(self, lead_dict, values):
        """ Check if method fails

        :param lead_dict: dictionary {name:crm.lead,...}
        :param values: dictionary with the values will be passed to the method
        """

        msg = u'%s._ensure_reason_for_stage fails with %s'

        for key, lead_obj in lead_dict.iteritems():
            self._log(0, '{}._ensure_reason_for_stage({}) (should fail)', key, values)
            ensure_values = getattr(lead_obj, '_ensure_reason_for_stage')
            try:
                result = ensure_values(values)
            except AssertionError as ex:
                self._log(0, u'Expected AssertionError {}', ex)
                result = None
            self.assertIsNone(result, msg % (key, values))

    def test__ensure_reason_for_stage(self):
        """ Checks if the ``_ensure_reason_for_stage`` works properly

        It tests the nine cases shown in the following table:

        | new_stage_id  | new_reason_id | action                           |
        | ------------- | ------------- | -------------------------------- |
        |               |               |                                  |
        |               |    None       | 'crm_reason_id': None (*)        |
        |               |    Not None   | checks new reason in ``self``    |
        |    None       |               | 'crm_reason_id': None            |
        |    None       |    None       | 'crm_reason_id': None (*)        |
        |    None       |    Not None   | Launch an error always           |
        |    Not None   |               | Add default reason in values     |
        |    Not None   |    None       | 'crm_reason_id': None (*)        |
        |    Not None   |    Not None   | Check if new reason in new stage |

        The third and nineth cases depends of the recordset, this method tests
        both with the two possible results.
        """

        # STEP 0: Declare and initialice variables
        rxid = 'crm_case_stage_reason.crm_stage_reason_demo_%d'

        # Empty recordset, record with ``New`` as stage and with a different
        lead_obj = self._lead_obj
        lead_new = self.env.ref('crm.crm_case_27')
        lead_dead = self.env.ref('crm.crm_case_11')

        lead_all = {
            'lead_obj': lead_obj,
            'lead_new': lead_new,
            'lead_dead': lead_dead
        }

        # The ``New`` stage; valid, default and invalid reason
        stage_new = self.env.ref('crm.stage_lead1')

        reason_new = self.env.ref(rxid % 2)
        reason_venture = self.env.ref(rxid % 3)
        reason_agreement = self.env.ref(rxid % 9)

        # TEST 1: new_stage_id: empty, new_reason_id: empty
        # ----------------------------------------------------------
        values = {}
        expected = {}

        self._expected_values(lead_all, values, expected)

        # TEST 2: new_stage_id: empty, new_reason_id: none
        # ----------------------------------------------------------
        values = {'crm_reason_id': None}
        expected = {'crm_reason_id': None}

        self._expected_values(lead_all, values, expected)

        # TEST 3: new_stage_id: empty, new_reason_id: value
        # It must fail when ``stage_id`` is different than ``New``
        # ----------------------------------------------------------
        values = {'crm_reason_id': reason_new.id}
        expected = {'crm_reason_id': reason_new.id}

        self._expected_values({'lead_new': lead_new}, values, expected)

        fail_dict = {'lead_obj': lead_obj, 'lead_dead': lead_dead}
        self._expected_fail(fail_dict, values)

        # TEST 4: new_stage_id: none, new_reason_id: empty
        # ----------------------------------------------------------
        values = {'stage_id': None}
        expected = {'stage_id': None, 'crm_reason_id': None}

        self._expected_values(lead_all, values, expected)

        # TEST 5: new_stage_id: none, new_reason_id: none
        # ----------------------------------------------------------
        values = {'stage_id': None, 'crm_reason_id': None}
        expected = {'stage_id': None, 'crm_reason_id': None}

        self._expected_values(lead_all, values, expected)

        # TEST 6: new_stage_id: empty, new_reason_id: value
        # It should fail in all cases
        # ----------------------------------------------------------
        values = {'stage_id': None, 'crm_reason_id': reason_new.id}
        self._expected_fail(lead_all, values)

        # TEST 7: new_stage_id: value, new_reason_id: empty
        # ----------------------------------------------------------
        values = {'stage_id': stage_new.id}
        expected = dict(
            stage_id=stage_new.id, crm_reason_id=reason_venture.id)

        self._expected_values(lead_all, values, expected)

        # TEST 8: new_stage_id: value, new_reason_id: none
        # ----------------------------------------------------------
        values = {'stage_id': stage_new.id, 'crm_reason_id': None}
        expected = {'stage_id': stage_new.id, 'crm_reason_id': None}

        self._expected_values(lead_all, values, expected)

        # TEST 9: new_stage_id: value, new_reason_id: value
        # It success if stage_id and reason are compatible or fails otherwise
        # ----------------------------------------------------------
        values = {'stage_id': stage_new.id, 'crm_reason_id': reason_new.id}
        expected = {'stage_id': stage_new.id, 'crm_reason_id': reason_new.id}

        # 1
        self._expected_values(lead_all, values, expected)

        # 2
        values.update({'crm_reason_id': reason_agreement.id})
        self._expected_fail(lead_all, values)

    # -------------------------- SQL QUERY STRINGS ----------------------------

    _sql_reasons_from_stage = """
        SELECT
            "id",
            default_crm_reason_id,
            reason_ids
        FROM
            crm_case_stage
        LEFT JOIN (
            SELECT
                crm_case_stage_id,
                ARRAY_AGG (crm_stage_reason_id) AS reason_ids
            FROM
                crm_stage_to_reason_rel
            GROUP BY
                crm_case_stage_id

        ) AS tb ON tb.crm_case_stage_id = "id"
        ORDER BY "id"
    """
