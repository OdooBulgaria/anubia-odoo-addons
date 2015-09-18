# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp.tests.common import TransactionCase

from logging import getLogger


_logger = getLogger(__name__)


class TestCrmLead(TransactionCase):
    """ This class contains the unit tests for 'crm.lead'.

        Tests:
          - item_name: Checks if the item_name works properly
    """

    def setUp(self):
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

    def _log(self, level, msg_format, *args, **kwargs):
        """ Outputs an formated string in log

            :param level (int): 0=> debug, 1=> info, 2=> warning, 3=> error
            :param message (basestring): name of the message
        """

        methods = ['debug', 'info', 'warning', 'error']
        log = getattr(_logger, methods[level])

        msg = msg_format.format(*args, **kwargs)
        log(msg)

    def test__values_to_update(self):
        """ Checks if the _values_to_update works properly

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
            obtained = self._lead_obj._values_to_update(values),
            expected = results[counter],
            self._log(0, 'obtainded {} / expected {}', obtained, expected)

            # STEP 3: Compare otained and expected results
            self.assertTupleEqual(
                obtained,
                expected,
                msg='_values_to_update(%s) fails!' % (values)
            )

            # STEP 4: Counter keep pointer to the expected results list
            counter += 1

    def test__reasons_from_stage(self):
        """ Checks if the _reasons_from_stage works properly
        """

        # STEP 1: Load all stages
        stage_domain = []
        stage_obj = self.env['crm.case.stage']
        stage_set = stage_obj.search(stage_domain)

        for stage in stage_set:

            # STEP 2: Get reasons and default reason from current stage
            reason_ids = stage.crm_reason_ids.mapped('id')
            default_reason_id = stage.default_crm_reason_id.id or None

            # STEP 3: Call tested method for current stage
            result = self._lead_obj._reasons_from_stage(stage.id)

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

    def test__stages_from_reason(self):
        """ Checks if the _stages_from_reason works properly
        """
        # STEP 1: Load all reasons
        reason_domain = []
        reason_obj = self.env['crm.stage.reason']
        reason_set = reason_obj.search(reason_domain)

        for reason in reason_set:

            # STEP 2: Get reasons and default reason from current reason
            stage_ids = reason.crm_stages_ids.mapped('id')

            # STEP 3: Call tested method for current reason
            result = self._lead_obj._stages_from_reason(reason.id)

            # STEP 4: compare stages earned from reason and tested method
            self._log(0, 'stages: {} / {}', result, stage_ids)
            self.assertSetEqual(
                set(result),
                set(stage_ids),
                msg='_stages_from_reasone(%s) fails!' % reason.id
            )

    def test__ensure_values(self):
        """ Checks if the _ensure_values works properly
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
        """
        msg = u'_ensure_values fails with %s'
        lead_obj = self._lead_obj
        lead_new = self.env.ref('crm.crm_case_27')
        lead_dead = self.env.ref('crm.crm_case_11')

        stage_new = self.env.ref('crm.stage_lead1')
        reason_new = self.env.ref(
            'crm_case_stage_reason.crm_stage_reason_demo_2')
        reason_venture = self.env.ref(
            'crm_case_stage_reason.crm_stage_reason_demo_3')

        # STEP 1: |               |               |
        # ----------------------------------------------------------
        values = {}
        expected = {}

        result = lead_obj._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_new._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_dead._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        # STEP 2: |               |    None       |
        # ----------------------------------------------------------
        values = {'crm_reason_id': None}
        expected = {'crm_reason_id': None}

        result = lead_obj._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_new._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_dead._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        # STEP 3: |               |    Not None   |
        # ----------------------------------------------------------
        values = {'crm_reason_id': reason_new.id}
        expected = None
        try:
            result = lead_obj._ensure_values(values)
        except:
            result = None
        self.assertIsNone(result,  msg % values)

        # try:
        #     result = lead_new._ensure_values(values)
        # except:
        #     result = None
        # self.assertDictEqual(expected, result, msg % values)

        try:
            result = lead_dead._ensure_values(values)
        except:
            result = None
        self.assertIsNone(result,  msg % values)

        # STEP 4: |    None       |               |
        # ----------------------------------------------------------
        values = {'stage_id': None}
        expected = {'stage_id': None, 'crm_reason_id': None}

        result = lead_obj._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_new._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_dead._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        # STEP 5: |    None       |    None       |
        # ----------------------------------------------------------
        values = {'stage_id': None, 'crm_reason_id': None}
        expected = {'stage_id': None, 'crm_reason_id': None}

        result = lead_obj._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_new._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_dead._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        # STEP 6: |    None       |    Not None   |
        # ----------------------------------------------------------
        values = {'stage_id': None, 'crm_reason_id': reason_new.id}
        expected = None
        try:
            result = lead_obj._ensure_values(values)
        except:
            result = None
        self.assertIsNone(result,  msg % values)

        try:
            result = lead_new._ensure_values(values)
        except:
            result = None
        self.assertIsNone(result,  msg % values)

        try:
            result = lead_dead._ensure_values(values)
        except:
            result = None
        self.assertIsNone(result,  msg % values)

        # STEP 7: |    Not None   |               |
        # ----------------------------------------------------------
        values = {'stage_id': stage_new.id}
        expected = dict(
            stage_id=stage_new.id, crm_reason_id=reason_venture.id)

        result = lead_obj._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_new._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_dead._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        # STEP 8: |    Not None   |    None       |
        # ----------------------------------------------------------
        values = {'stage_id': stage_new.id, 'crm_reason_id': None}
        expected = {'stage_id': stage_new.id, 'crm_reason_id': None}

        result = lead_obj._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_new._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        result = lead_dead._ensure_values(values)
        self.assertDictEqual(expected, result, msg % values)

        # STEP 9: |    Not None   |    Not None   |
        # ----------------------------------------------------------
        values = {'stage_id': stage_new.id, 'crm_reason_id': reason_new.id}
        expected = {'stage_id': stage_new.id, 'crm_reason_id': reason_new.id}

        try:
            result = lead_obj._ensure_values(values)
        except:
            result = None
        self.assertDictEqual(expected, result, msg % values)

        try:
            result = lead_new._ensure_values(values)
        except:
            result = None
        self.assertDictEqual(expected, result, msg % values)

        try:
            result = lead_dead._ensure_values(values)
        except:
            result = None
        self.assertDictEqual(expected, result, msg % values)

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
