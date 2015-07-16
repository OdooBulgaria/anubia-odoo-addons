# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields

from logging import getLogger


_logger = getLogger(__name__)


class ResUsers(models.Model):
    """ Add two fields to manage user zones

    Fields:
      name (Char): Human readable name which will identify each record.

    """

    _name = 'res.users'
    _inherit = ['base.zone.middle.relationship', 'res.users']

    # ---------------------------- ENTITY FIELDS ------------------------------

    zone_ids = fields.Many2many(
        string='Zone ids',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Add or remove the user from zone',
        comodel_name='base.zone',
        relation='base_zone_res_users_rel',
        column1='res_users_id',
        column2='base_zone_id',
        domain=[],
        context={},
        limit=None
    )

    # -------------------------- MANAGEMENT FIELDS ----------------------------

    subordinate_zone_ids = fields.Many2many(
        string='Subordinate zones',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Display all subordinate zones',
        comodel_name='base.zone',
        relation='base_zone_holder_res_users_rel',
        column1='res_users_id',
        column2='base_zone_id',
        domain=[],
        context={},
        limit=None
    )

    holder_zone_ids = fields.Many2many(
        string='Holder zones',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Display all holder zones',
        comodel_name='base.zone',
        relation='base_zone_subordinate_res_users_rel',
        column1='res_users_id',
        column2='base_zone_id',
        domain=[],
        context={},
        limit=None
    )
    # ----------------------------- SQL QUERIES -------------------------------

    # SQL query used by base.zone.middle.relationship parent model
    _sql_view_select_base_zone_holder_res_users_rel = False

    # SQL query used by base.zone.middle.relationship parent model
    _sql_view_select_base_zone_subordinate_res_users_rel = """
        WITH descendants AS (
            WITH RECURSIVE zone_tree AS (
                SELECT
                    base_zone.parent_id,
                    base_zone. ID AS zone_id
                FROM
                    base_zone
                UNION ALL
                    SELECT
                        zt.parent_id,
                        bz. ID AS zone_id
                    FROM
                        (
                            base_zone bz
                            JOIN zone_tree zt ON ((bz.parent_id = zt.zone_id))
                        )
            ) SELECT
                zone_tree.zone_id AS base_zone_descendant_id,
                CASE
                    WHEN (zone_tree.parent_id IS NULL) THEN
                        zone_tree.zone_id
                    ELSE
                        zone_tree.parent_id
                END AS base_zone_id
            FROM
                zone_tree
        ) SELECT DISTINCT ON (descendants.base_zone_id, res_users."id")
            descendants.base_zone_id AS base_zone_id,
            res_users."id" AS res_users_id
        FROM
            descendants
        INNER JOIN base_zone_res_users_rel AS rel ON
            descendants.base_zone_descendant_id = rel.base_zone_id
        INNER JOIN res_users ON res_users."id" = rel.res_users_id
    """
