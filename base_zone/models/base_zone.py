# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _

from logging import getLogger


_logger = getLogger(__name__)
_atoms = {int, long, str, unicode, models.NewId}


class BaseZone(models.Model):
    """ Allows to create nicknames for a group of zip codes that can be
        associated to sales workforce.')

    Entity fields:
      name (Char) : Name of the zone
      active (Boolean): Enable or disable the zone
      parent_id (Many2one): Zone in which is included
      child_ids (One2many): Subzones in the zone
      user_ids (Many2one): Users assigned to zone
      zip_ids (One2many): Zip codes of the zone
      notes (Text): somthing about record
    Management fields:
      zip_range_ex (Char): zip code pattern to be added/removed
      holder_ids (One2many): all zones above in hierarchy
      subordinate_ids (One2many): all zones below in hierarchy
      subordinate_zip_ids (Many2many): zip codes from all zones below in hrch.
      holder_user_ids (Many2many): zip codes from all zones below in hierarchy
      trail (Char): parent zone breadcrumbs
    """

    _name = 'base.zone'
    _description = u'Zip-based geographical zone'

    _inherit = ['base.zone.middle.relationship', 'mail.thread']

    _rec_name = 'name'
    _order = 'name ASC'

    _zip_range_regex = None

    # ---------------------------- ENTITY FIELDS ------------------------------

    name = fields.Char(
        string='Name',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Enter the name of the zone",
        size=50,
        translate=False,
        track_visibility='onchange',
    )

    active = fields.Boolean(
        string='Active',
        required=False,
        readonly=False,
        index=False,
        default=True,
        help='Switch to enable or disable the zone',
        track_visibility='onchange',
    )

    parent_id = fields.Many2one(
        string='Parent zone',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Sets the zone in which this will be included',
        comodel_name='base.zone',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False,
        oldname='parent_zone_id',
        track_visibility='onchange',
    )

    child_ids = fields.One2many(
        string='Child zones',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Add or remove subzones from zone',
        comodel_name='base.zone',
        inverse_name='parent_id',
        domain=[],
        context={},
        auto_join=False,
        limit=None,
        oldname='children_zone_ids',
        track_visibility='onchange',
    )

    user_ids = fields.Many2many(
        string='Users',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Add or remove users from zone',
        comodel_name='res.users',
        relation='base_zone_res_users_rel',
        column1='base_zone_id',
        column2='res_users_id',
        domain=[],
        context={},
        limit=None,
        track_visibility='onchange',
    )

    zip_ids = fields.One2many(
        string='Own zip codes',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Add or remove zip codes from zone',
        comodel_name='res.better.zip',
        inverse_name='base_zone_id',
        domain=[],
        context={},
        auto_join=False,
        limit=None,
        ondelete='set null'
    )

    default_user_id = fields.Many2one(
        string='Default user',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='res.users',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    notes = fields.Text(
        string='Notes',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Some information about the zone',
        translate=True
    )

    # -------------------------- MANAGEMENT FIELDS ----------------------------

    zip_range_ex = fields.Char(
        string='Zip range expression',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Regular expression which defines the needed zip code range',
        size=65536,  # 64KB needed to add long lists of zip codes
        translate=False,
        store=False,
        search=lambda self, oper, val: self._search_zip_range_ex(oper, val)
    )

    holder_ids = fields.Many2many(
        string='Holder zones',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Displays all holder zones including this same',
        comodel_name='base.zone',
        relation='base_zone_implied_base_zone_rel',
        column1='base_zone_id',
        column2='parent_zone_id',
        domain=[],
        context={},
        limit=None
    )

    subordinate_ids = fields.Many2many(
        string='Subordinate zones',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Displays all subordinated zones including this same',
        comodel_name='base.zone',
        relation='base_zone_implied_base_zone_rel',
        column1='parent_zone_id',
        column2='base_zone_id',
        domain=[],
        context={},
        limit=None
    )

    subordinate_zip_ids = fields.Many2many(
        string='Subordinate zip codes',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Zip codes of all descendants zones including this same',
        comodel_name='res.better.zip',
        relation='base_zone_subordinate_res_better_zip_rel',
        column1='base_zone_id',
        column2='res_better_zip_id',
        domain=[],
        context={},
        limit=None
    )

    holder_user_ids = fields.Many2many(
        string='Holder users',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Users of all ascendants zones including this same',
        comodel_name='res.users',
        relation='base_zone_holder_res_users_rel',
        column1='base_zone_id',
        column2='res_users_id',
        domain=[],
        context={},
        limit=None
    )

    subordinate_user_ids = fields.Many2many(
        string='Subordinate users',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Users of all descendant zones including this same',
        comodel_name='res.users',
        relation='base_zone_subordinate_res_users_rel',
        column1='base_zone_id',
        column2='res_users_id',
        domain=[],
        context={},
        limit=None
    )

    trail = fields.Char(
        string='Trail',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help='Parent zone trail from top',
        size=255,
        translate=False,
        compute=lambda self: self._compute_trail(),
        oldname='zone_trail'
    )

    # --------------------------- SQL CONSTRAINTS -----------------------------

    _sql_constraints = [
        (
            'prevent_recursion',
            'CHECK ((parent_id IS NULL) OR (parent_id <> id))',
            _(u'If this parent zone was established an infinite loop would '
              u'be created.')
        ),  # This will be overwritten later
        (
            'verify_default_user_id',
            'CHECK ((user_id IS NULL) OR (user_id > 0))',
            _(u'Default user is not an allowed zone user.')
        )
    ]

    # --------------------------- ONCHANGE EVENTS -----------------------------

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        self.ensure_one()
        self.trail = self._get_trail()

    # ---------------------------- FIELD METHODS ------------------------------

    @api.multi
    @api.depends('parent_id')
    def _compute_trail(self):
        for record in self:
            record.trail = record._get_trail()

    def _get_trail(self):
        """ Builds the zone trail (parent > child)

            :return (unicode): zone trail
        """

        self.ensure_one()

        record = self
        trail = record.name

        # record.parent_id != self
        # prevents recursion while the record has not been saved
        while record.parent_id and record.parent_id != self:
            record = record.parent_id
            trail = u'{} > {}'.format(record.name, trail)

        # limit trail length (for good measure)
        return (trail or u'')[:255]

    @api.model
    def _search_zip_range_ex(self, operator, value):
        """ Disallow search by zip_range_ex
        """
        return [('id', '<', 0)]

    # --------------------------- PUBLIC METHODS ------------------------------

    @api.multi
    def add_zip_codes(self, zip_range_ex=None):
        """ Behavior for the ``add`` button shown in the model form view """

        for record in self:
            record.zip_range_ex = zip_range_ex or record.zip_range_ex or ''
            record._proccess_zip_range_ex(remove=False)

    @api.multi
    def remove_zip_codes(self, zip_range_ex=None):
        """ Behavior for the ``remove`` button shown in the model form view """

        for record in self:
            record.zip_range_ex = zip_range_ex or record.zip_range_ex or ''
            record._proccess_zip_range_ex(remove=True)

    def browse_by_zip(self, zip_names, subordinate=False):
        zip_set = self.env['res.better.zip']
        zip_names = self._normalize_zips(zip_names)

        assert not subordinate, \
            u'Browse by subordinate zip not implemented yet'

        if zip_names:
            zip_domain = [('name', 'in', zip_names)]
            zip_set = zip_set.search(zip_domain)

        return zip_set.mapped('base_zone_id')

    # ------------------------- OVERWRITTEN METHODS ---------------------------

    def _auto_end(self, cr, context=None):
        """ Overwritten method which replaces some model complex constraints
        """

        _super = super(BaseZone, self)
        result = _super._auto_end(cr, context)

        cr.execute(self._sql_alter_recursion_constraint)
        cr.execute(self._sql_verify_default_user)

        return result

    # -------------------------- AUXILIARY METHODS ----------------------------

    @api.multi
    def _proccess_zip_range_ex(self, remove=False):
        """ Proccess entered zip_range_ex adding or removing zips

        :param zip_range_ex: regular expresion to match with zip codes,
                             if it's empty object zip_range_ex will be used.
        :param remove: False => add, True => remove
        """

        self.ensure_one()

        zip_range_ex = self.zip_range_ex or ''
        zone_out = not remove
        result_obj = self.env['res.better.zip']
        result_set = result_obj.regex_search(zip_range_ex, zone_out)

        if result_set:
            if remove:
                zip_set = (self.zip_ids - result_set)
            else:
                zip_set = (self.zip_ids | result_set)

            zip_ids = zip_set.mapped('id') or [0]
            self.zip_ids = [(6, 0, zip_ids)]

        self.zip_range_ex = None

    def _normalize_zips(self, arg, atoms=_atoms):
        """ Normalizes the ids argument for ``browse_by_zip`` to a tuple.

        :rtype: tuple
        """
        if not arg:
            return ()

        if arg.__class__ in atoms:
            return arg,

        return tuple(arg)

    def _log(self, level, msg_format, *args, **kwargs):
        """ Outputs an formated string in log

            :param level (int): 0=> debug, 1=> info, 2=> warning, 3=> error
            :param message (basestring): name of the message
        """

        methods = ['debug', 'info', 'warning', 'error']
        log = getattr(_logger, methods[level])

        msg = msg_format.format(*args, **kwargs)
        log(msg)

    # ----------------------- BACKWARD COMPATIBILITY --------------------------

    def get_zone_trail(self, context=None):
        """ backward compatibility, undocumented """
        self.ensure_one()
        return self._compute_trail()

    @api.one
    @api.returns('base.zone')
    def get_top_zone(self, context=None):
        """ backward compatibility, undocumented """
        return self.holder_ids.filtered(lambda x: not x.parent_id)

    @api.one
    @api.returns('res.better.zip')
    def get_subtree_zip_ids(self, context=None):
        """ backward compatibility, undocumented """
        return self.subordinate_ids

    def get_base_zones_for_zip(self, zip_name=None):
        """ backward compatibility, undocumented """
        return self.browse_by_zip(zip_name, subordinate=False)

    @staticmethod
    def get_users_by_zip(self, zip_name=None):
        """ backward compatibility, undocumented """
        if not zip_name:
            return False
        zip_ids = self.env['res.better.zip'].search([('name', '=', zip_name)])
        user_ids = zip_ids.mapped('base_zone_ids.user_ids')
        return user_ids

    def contains_user(self, user_id=None):
        """ backward compatibility, undocumented """
        self.ensure_one()

        users_ids = [u.id for u in self.user_ids]
        return user_id and user_id in users_ids or False

    # ----------------------------- SQL QUERIES -------------------------------

    # SQL query used by base.zone.middle.relationship parent model
    _sql_view_select_base_zone_subordinate_res_better_zip_rel = """
        WITH RECURSIVE zone_tree AS (
            SELECT
                base_zone.parent_id,
                base_zone."id" AS zone_id
            FROM
                base_zone
            UNION ALL
                SELECT
                    zt.parent_id,
                    bz."id" AS zone_id
                FROM
                    base_zone as bz
                JOIN zone_tree as zt ON bz.parent_id = zt.zone_id
        ) SELECT
            CASE
                WHEN zone_tree.parent_id IS NULL THEN
                    zone_tree.zone_id
                ELSE
                    zone_tree.parent_id
            END AS base_zone_id,
            res_better_zip. ID AS res_better_zip_id
        FROM
            zone_tree
        JOIN res_better_zip ON
            zone_tree.zone_id = res_better_zip.base_zone_id
    """

    # SQL query used by base.zone.middle.relationship parent model
    _sql_view_select_base_zone_implied_base_zone_rel = """
        WITH RECURSIVE zone_tree AS (
            SELECT
                base_zone.parent_id,
                base_zone."id" AS zone_id
            FROM
                base_zone
            UNION ALL
                SELECT
                    zt.parent_id,
                    bz."id" AS zone_id
                FROM
                    base_zone AS bz
                JOIN zone_tree AS zt ON bz.parent_id = zt.zone_id
        ) SELECT
            zone_id AS base_zone_id,
            CASE
                WHEN parent_id IS NULL THEN
                    zone_id
                ELSE
                    parent_id
            END AS parent_zone_id
        FROM
            zone_tree
    """

    # SQL query used by base.zone.middle.relationship parent model
    _sql_view_select_base_zone_holder_res_users_rel = """
        WITH ascendant AS (
            WITH RECURSIVE zone_tree AS (
                SELECT
                    base_zone.parent_id,
                    base_zone."id" AS zone_id
                FROM
                    base_zone
                UNION ALL
                    SELECT
                        zt.parent_id,
                        bz."id" AS zone_id
                    FROM
                        base_zone AS bz
                    JOIN zone_tree AS zt ON bz.parent_id = zt.zone_id
            ) SELECT
                zone_id AS base_zone_id,
                CASE
            WHEN parent_id IS NULL THEN
                zone_id
            ELSE
                parent_id
            END AS base_zone_ascendant_id
            FROM
                zone_tree
        ) SELECT DISTINCT ON ("a".base_zone_id, u."id")
            "a".base_zone_id,
            u."id" AS res_users_id
        FROM
            ascendant AS "a"
        INNER JOIN base_zone_res_users_rel AS rel ON
            "a".base_zone_ascendant_id = rel.base_zone_id
        INNER JOIN res_users AS u ON
            rel.res_users_id = u."id"
    """

    # SQL query used by base.zone.middle.relationship parent model
    _sql_view_select_base_zone_subordinate_res_users_rel = False

    _sql_alter_recursion_constraint = """
        CREATE
        OR REPLACE FUNCTION GET_CHILD_ZONES (INT) RETURNS int[] AS $$
        select array(SELECT
            base_zone_id
        FROM
            base_zone_implied_base_zone_rel
        WHERE
            parent_zone_id = $1) $$ LANGUAGE SQL;

        ALTER TABLE base_zone DROP CONSTRAINT
        IF EXISTS base_zone_prevent_recursion;

        ALTER TABLE base_zone
        ADD CONSTRAINT base_zone_prevent_recursion CHECK (
            parent_id IS NULL or
            parent_id <> ALL(GET_CHILD_ZONES(id))
        );
    """

    _sql_verify_default_user = """
        CREATE
        OR REPLACE FUNCTION GET_ZONE_USERS (INT) RETURNS INT [] AS $$ SELECT
            ARRAY (
                SELECT
                    ID
                FROM
                    res_users
                INNER JOIN base_zone_res_users_rel AS rel
                    ON res_users."id" = rel.res_users_id
                WHERE
                    rel.base_zone_id = 1
            ) $$ LANGUAGE SQL;

        ALTER TABLE base_zone DROP CONSTRAINT
        IF EXISTS base_zone_verify_default_user_id;

        ALTER TABLE base_zone
            ADD CONSTRAINT base_zone_verify_default_user_id CHECK (
                default_user_id IS NULL
                OR default_user_id  = ALL (GET_ZONE_USERS(ID))
            );
    """
