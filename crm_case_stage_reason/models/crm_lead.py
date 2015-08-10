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

    # ------------------------- OVERWRITTEN METHODS ---------------------------

    @api.multi
    def write(self, values):
        """ Update reason according to new stage if this have changed.
        """
        values = self._update_lead_reason(values)
        result = super(CrmLead, self.sudo()).write(values)
        return result

    # -------------------------- AUXILIARY METHODS ----------------------------

    def _update_lead_reason(self, values):
        """ If stage have been changed ('stage_id' in values), it checks if
            current reason is valid for new stage, otherwise it changes it.

            :param self: recordset of crm.lead
            :return: updated dictionary
        """
        stage_id = values.get('stage_id', False)
        if stage_id:
            for record in self:
                current_reason = record.crm_reason_id
                new_stage = self.env['crm.case.stage'].browse(stage_id)
                if current_reason not in new_stage.crm_reason_ids:
                    values['crm_reason_id'] = \
                        new_stage.default_crm_reason_id.id
        return values
