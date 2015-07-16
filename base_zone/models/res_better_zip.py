# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields

from logging import getLogger


_logger = getLogger(__name__)


class ResBetterZip(models.Model):
    """ Add an inverse field for base_zone->zip_ids One2many field

    Fields:
      base_zone_id (Many2one): inverse field for base_zone->zip_ids One2many

    """

    _inherit = 'res.better.zip'

    # ---------------------------- ENTITY FIELDS ------------------------------

    base_zone_id = fields.Many2one(
        string='Base zone',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Set the zone to which zip code belongs',
        comodel_name='base.zone',
        domain=[],
        context={},
        ondelete='set null',
        auto_join=False
    )

    holder_zone_ids = fields.Many2many(
        string='Holder zones',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Zip codes of all descendants zones including this same',
        comodel_name='base.zone',
        relation='base_zone_subordinate_res_better_zip_rel',
        column1='res_better_zip_id',
        column2='base_zone_id',
        domain=[],
        context={},
        limit=None
    )

    # -------------------------- PUBLIC METHODS   -----------------------------

    def regex_search(self, regex, zone_out=False):
        """ Search zip codes whose names match a given regular expression

            :param regex: regular expression
            :param zone_out: ensure the returned zip codes are out of any zone
            :return: recordset of res.better.zip (can be empty)
        """

        # STEP 1: Initialize an empty recordset
        zip_set = self.env[self._name]

        # STEP 2: Check if `regex` could be normalized to continue
        regex = self._normalize_zip_regex(regex)
        if regex:

            # STEP 3: Build the sql query with regex and `zone_out` restriction
            _sql = self._sql_regex_zip.format(regex)
            if zone_out:
                _sql += ' AND base_zone_id IS NULL'

            # STEP 4: Execute query and fetch a dict/list with of returned IDs
            # [{'id': n}, {'id': m}, ...]
            cr = self.env.cr
            cr.execute(_sql)
            id_set = cr.dictfetchall()

            # STEP 5: Build a list with all the ID's in dictionary/list
            _ids = [item['id'] for item in id_set]
            zip_set = zip_set.browse(_ids)

        return zip_set

    # -------------------------- AUXILIARY METHODS ----------------------------

    def _normalize_zip_regex(self, regex):
        """ Decode given string and adds the following regex characters ^ $ at
            the beginning and end respectively

            :regex (basestring): regular expression to be normalized
            :return: normalized regular expression
        """

        if regex and isinstance(regex, basestring):
            regex = r'{}'.format(regex.decode(errors='ignore'))

            if regex:  # Has been decoded successfully
                if not regex[0] in r'^':
                    regex = r'^{}'.format(regex)

                if not regex[-1] in r'$':
                    regex = r'{}$'.format(regex)
        else:
            regex = r''

        return regex

    # ----------------------------- SQL QUERIES -------------------------------

    _sql_regex_zip = """
        SELECT
            "id"
        FROM
            res_better_zip
        WHERE
            "name" ~ '{}'
    """
