# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from logging import getLogger


_logger = getLogger(__name__)


class CrmCaseStage(models.Model):
    """ Extends crm.case.stage model adding it reasons

    Fields:
      crm_reason_ids: available reasons for each stage of case
      default_reason_id: default reason for each stage of case
    """

    _inherit = 'crm.case.stage'
    _description = u'Crm case stage'

    _rec_name = 'name'
    _order = 'name ASC'

    # --------------------------- ENTITY  FIELDS ------------------------------

    name = fields.Char(
        string='Name',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help=False,
        size=50,
        translate=True
    )

    crm_reason_ids = fields.Many2many(
        comodel_name='crm.stage.reason',
        relation='crm_stage_to_reason_rel',
        string='Available reasons',
        select=True,
        ondelete='restrict',
        required=False,
        default=False,
    )

    default_crm_reason_id = fields.Many2one(
        comodel_name='crm.stage.reason',
        string='Default reason',
        select=True,
        ondelete='restrict',
        required=False,
        default=False,
        domain="[('id', 'in', crm_reason_ids[0][2])]",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
        store=True,
    )

    # ----------------------------- CONSTRAINTS -------------------------------

    _sql_constraints = [
        (
            'check_default_crm_reason_id',
            'CHECK ((default_crm_reason_id IS NULL) OR (default_crm_reason_id > 0))',
            u'Default reason must belong to the allow list of reasons'
        )
    ]

    # ------------------------- OVERWRITTEN METHODS ---------------------------

    def _auto_end(self, cr, context=None):
        """ Overwritten method which replaces some model complex constraints
        """

        _super = super(CrmCaseStage, self)
        result = _super._auto_end(cr, context)

        cr.execute(self._sql_default_crm_reason_id)

        return result

    @api.multi
    def write(self, values):
        """
            Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise

            @param values: dict of new values to be set
            @return: True on success, False otherwise
        """
        result = True

        if self._both_reasons_changed(values):
            crm_reason_ids = values.pop('crm_reason_ids')
            result = super(CrmCaseStage, self).write(
                {'crm_reason_ids': crm_reason_ids})

        return result and super(CrmCaseStage, self).write(values)

    @api.model
    def create(self, values):
        """
            Create a new record for a model CrmCaseStage

            @param values: provides a data for new record
            @return: returns a id of new record
        """
        default_crm_reason_id = None

        if self._both_reasons_changed(values):
            default_crm_reason_id = values.pop('default_crm_reason_id')

        result = super(CrmCaseStage, self).create(values)

        if result and default_crm_reason_id:
            result.write({'default_crm_reason_id': default_crm_reason_id})

        return result

    # -------------------------- AUXILIARY METHODS ----------------------------

    def _both_reasons_changed(self, values):
        return \
            'default_crm_reason_id' in values and \
            values['default_crm_reason_id'] and \
            'crm_reason_ids' in values and \
            values['crm_reason_ids']

    # ----------------------------- SQL QUERIES -------------------------------

    _sql_default_crm_reason_id = """
        CREATE
        OR REPLACE FUNCTION get_reasons_from_stage(int) RETURNS int[] AS $$
        SELECT
            ARRAY (
                SELECT
                    id
                FROM
                    crm_stage_reason
                INNER JOIN crm_stage_to_reason_rel AS rel
                    ON crm_stage_reason.id = rel.crm_stage_reason_id
                WHERE
                    rel.crm_case_stage_id = $1
            ) $$ LANGUAGE SQL;

        ALTER TABLE crm_case_stage DROP CONSTRAINT
        IF EXISTS crm_case_stage_check_default_crm_reason_id;

        ALTER TABLE crm_case_stage
            ADD CONSTRAINT crm_case_stage_check_default_crm_reason_id CHECK (
                (default_crm_reason_id IS NULL)
                OR (default_crm_reason_id = ANY(get_reasons_from_stage(id)))
            );
    """
