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


class TestBaseZone(TransactionCase):
    """ This class contains the unit tests for 'base.zone'.

        Tests:
          - item_name: Checks if the item_name works properly
    """

    def setUp(self):
        super(TestBaseZone, self).setUp()

        self.zone_obj = self.env['base.zone']
        self.zip_obj = self.env['res.better.zip']

        self.zip_arnor = self.zip_obj.create(
            dict(name='ar', city='Arnor')
        )

        self.zip_unlinked = self.zip_obj.create(
            dict(name='unlinked', city='Unlinked')
        )

    def test_create(self):
        """ Checks if the create works properly
        """

        values = dict(
            name='Arnor',
            active=False,
            zip_ids=[(4, self.zip_arnor.id)]
        )

        new = self.zone_obj.create(values)

        self.assertIsNotNone(
            new, 'Fail on test create with Arnor')

        self.assertIsNotNone(
            new.zip_ids, 'Zip code was not added for Arnor')

    def test__regex_search(self):
        """ Checks if the _regex_search works properly
        """
        zip_type = type(self.env['res.better.zip'])

        # STEP 1: Search for existing zips wich already linked
        found = self.zone_obj._regex_search('BR', zone_out=True)
        self.assertIsInstance(
            found, zip_type, 'Result is not a zone recordset')
        self.assertTrue(
            len(found) == 0, 'Found Bree but it was already linked')

        found = self.zone_obj._regex_search('BR', zone_out=False)
        self.assertIsInstance(
            found, zip_type, 'Result is not a zone recordset')
        self.assertTrue(
            len(found) == 1, 'Bree not found')

        # STEP 2: Search for existing zips which were not linked
        regex = self.zip_unlinked.name
        found = self.zone_obj._regex_search(regex, zone_out=True)
        self.assertIsInstance(
            found, zip_type, 'Result is not a zone recordset')
        self.assertTrue(
            len(found) == 1, '%s not found' % regex)

        found = self.zone_obj._regex_search(regex, zone_out=True)
        self.assertIsInstance(
            found, zip_type, 'Result is not a zone recordset')
        self.assertTrue(
            len(found) == 1, '%s not found' % regex)

        # STEP 3: Search with empty and null regex
        found = self.zone_obj._regex_search('', zone_out=False)
        self.assertIsInstance(
            found, zip_type, 'Result is not a zone recordset')
        self.assertTrue(
            len(found) == 0, 'Some records were found with an empty regex')

        found = self.zone_obj._regex_search(None, zone_out=False)
        self.assertIsInstance(
            found, zip_type, 'Result is not a zone recordset')
        self.assertTrue(
            len(found) == 0, 'Some records were found without regex')

    def test_button_add_zip_codes(self):
        """ Checks if the button_add_zip_codes works properly
        """
        eriador = self.env.ref('base_zone.base_zone_eriador')
        regex = self.zip_unlinked.name

        eriador.zip_range_ex = regex
        eriador.button_add_zip_codes()

        self.assertTrue(
            len(eriador.zip_ids) == 2, '%s was not added' % regex)

        self.assertTrue(
            self.zip_unlinked in eriador.zip_ids, 'bad zip was added')

    def test_button_remove_zip_codes(self):
        """ Checks if the button_remove_zip_codes works properly
        """

        eriador = self.env.ref('base_zone.base_zone_eriador')
        eriador.zip_range_ex = 'ERDR'

        eriador.button_remove_zip_codes()

        self.assertTrue(
            len(eriador.zip_ids) == 0, '%s was not removed' % 'ERDR')

    def test_browse_by_zip(self):
        """ Checks if the browse_by_zip works properly
        """

        eriador = self.env.ref('base_zone.base_zone_eriador')

        found = self.zone_obj.browse_by_zip('ERDR')
        self.assertTrue(
            len(found) == 1 and found.id == eriador.id,
            msg='Searching Eriador other zone was found')

        found = self.zone_obj.browse_by_zip('\*\#\~non exinting')
        self.assertTrue(len(found) == 0, msg='Non exinsting was found')

        found = self.zone_obj.browse_by_zip('\*\#\~non exinting')
        self.assertTrue(len(found) == 0, msg='Non exinsting was found')

        found = self.zone_obj.browse_by_zip('')
        self.assertTrue(len(found) == 0, msg='Empty was found')

        found = self.zone_obj.browse_by_zip('')
        self.assertTrue(len(found) == 0, msg='None was found')

    def test__compute_zip_set(self):
        """ Checks if the _compute_zip_set works properly
        """

        eriador = self.env.ref('base_zone.base_zone_eriador')
        bree = self.env.ref('base_zone.base_zone_bree')

        result = self.zone_obj._compute_zip_set(eriador, bree, remove=False)
        self.assertTrue(len(result) == 2, msg='Operation a | b fails')

        both = result  # Used below

        result = self.zone_obj._compute_zip_set(eriador, eriador, remove=False)
        self.assertTrue(len(result) == 1, msg='Operation a | a fails')

        result = self.zone_obj._compute_zip_set(
            self.zone_obj, eriador, remove=False)
        self.assertTrue(len(result) == 1, msg='Operation 0 | a fails')

        result = self.zone_obj._compute_zip_set(
            eriador, self.zone_obj, remove=False)
        self.assertTrue(len(result) == 1, msg='Operation a | 0 fails')

        result = self.zone_obj._compute_zip_set(
            self.zone_obj, self.zone_obj, remove=False)
        self.assertTrue(len(result) == 0, msg='Sum 0 | 0 fails')

        result = self.zone_obj._compute_zip_set(both, bree, remove=True)
        self.assertTrue(len(result) == 1, msg='Operation (a + b) - b fails')

        result = self.zone_obj._compute_zip_set(eriador, bree, remove=True)
        self.assertTrue(len(result) == 1, msg='Operation a - b fails')

        result = self.zone_obj._compute_zip_set(eriador, eriador, remove=True)
        self.assertTrue(len(result) == 0, msg='Operation a - a fails')

        result = self.zone_obj._compute_zip_set(
            self.zone_obj, eriador, remove=True)
        self.assertTrue(len(result) == 0, msg='Operation 0 - a fails')

        result = self.zone_obj._compute_zip_set(
            eriador, self.zone_obj, remove=True)
        self.assertTrue(len(result) == 1, msg='Operation a - 0 fails')

        result = self.zone_obj._compute_zip_set(
            self.zone_obj, self.zone_obj, remove=True)
        self.assertTrue(len(result) == 0, msg='Sum 0 - 0 fails')

    def test__normalize_zips(self):
        """ Checks if the _normalize_zips works properly

            Tested with: int, long, str, unicode and models.NewId
            Tested with list and tuple
        """

        # _atoms = {int, long, str, unicode, models.NewId}
        ret = self.zone_obj._normalize_zips(1)
        self.assertEqual(ret, (1,), 'Fail on _normalize_zips(1)')

        ret = self.zone_obj._normalize_zips(1L)
        self.assertEqual(ret, (1L,), 'Fail on _normalize_zips(1L)')

        ret = self.zone_obj._normalize_zips('1')
        self.assertEqual(ret, ('1',), 'Fail on _normalize_zips(\'1\')')

        ret = self.zone_obj._normalize_zips(u'1')
        self.assertEqual(ret, (u'1',), 'Fail on _normalize_zips(u\'1\')')

        _id = models.NewId()
        ret = self.zone_obj._normalize_zips(_id)
        self.assertEqual(ret, (), 'Fail on _normalize_zips(models.NewId')

        ret = self.zone_obj._normalize_zips((1, 2))
        self.assertEqual(
            ret, (1, 2), 'Fail on _normalize_zips((1, 2))')

        ret = self.zone_obj._normalize_zips([1, 2])
        self.assertEqual(
            ret, (1, 2), 'Fail on _normalize_zips([1, 2])')





# def _check_default_user_id
# def _onchange_parent_id
# def _compute_trail
# def _get_trail
# def _compute_zip_range_ex
# def auto_remove
# def _auto_init
# def _log
# def get_zone_trail
# def get_top_zone
# def get_subtree_zip_ids
# def get_base_zones_for_zip
# def get_users_by_zip
# def contains_user

