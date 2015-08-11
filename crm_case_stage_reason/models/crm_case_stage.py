# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields, api
from openerp.exceptions import ValidationError
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
    _description = _('Stage of case')

    _rec_name = 'name'
    _order = 'sequence'

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

    # ------------------------ POSTGRES CONSTRAINTS ---------------------------

    @api.one
    @api.constrains('default_crm_reason_id', 'crm_reason_ids')
    def _check_default_user_id(self):
        def_reason_id = self.default_crm_reason_id
        if def_reason_id and def_reason_id not in self.crm_reason_ids:
            msg = _(u'Default reason not available for this stage of case')
            raise ValidationError(msg)
