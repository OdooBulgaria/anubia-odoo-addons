# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from logging import getLogger


_logger = getLogger(__name__)


class CrmLead(models.Model):
    """ Extends crm.lead model adding it reasons

    Fields:
      crm_reason_id: reason for each stage of case selected in lead
    """

    _inherit = 'crm.lead'
    _description = u'Crm lead'

    _rec_name = 'name'
    _order = 'name ASC'

    # --------------------------- ENTITY  FIELDS ------------------------------

    crm_reason_id = fields.Many2one(
        comodel_name='crm.stage.reason',
        string='Reason',
        invisible=True,
        required=False,
        default=False,
        domain="[('crm_stages_ids', '=', stage_id)]",
    )

    crm_reason_available_ids = fields.Many2many(
        string="Historic stages",
        comodel_name='crm.stage.reason',
        relation='crm_reason_available_ids_rel',
        column1='lead_id',
        column2='reason_id',
        store=True,
        compute='_compute_crm_reason_available_ids',
    )

    # ----------------------- AUXILIARY FIELD METHODS -------------------------

    @api.depends('stage_id')
    def _compute_crm_reason_available_ids(self):
        for record in self:
            record.crm_reason_available_ids = record.stage_id and \
                record.stage_id.crm_reason_ids or False
