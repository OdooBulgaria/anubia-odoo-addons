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

    def _auto_end(self, cr, context=None):
        """ This method has been overwritten to register the model procedures
        and triggers
        """

        super(CrmLead, self)._auto_end(cr, context=context)

        cr.execute(self._sql_add_procedures_and_triggers)

    # -------------------------- SQL QUERY STRINGS ----------------------------

    _sql_add_procedures_and_triggers = """
        CREATE OR REPLACE FUNCTION ENSURE_VALID_REASON()
        RETURNS TRIGGER AS $$
        DECLARE
            available_reasons INTEGER ARRAY;
            default_reason INTEGER;
        BEGIN
            IF NEW.stage_id IS NULL THEN
                NEW.crm_reason_id = NULL;
            ELSE
                available_reasons = (SELECT
                    ARRAY (
                        SELECT
                            rel.crm_stage_reason_id
                        FROM
                            crm_stage_to_reason_rel as rel
                        WHERE rel.crm_case_stage_id = NEW.crm_reason_id
                    )):: INTEGER ARRAY;

                IF NEW.crm_reason_id != ALL(available_reasons) THEN
                    NEW.crm_reason_id = (
                        SELECT default_crm_reason_id
                        FROM crm_case_stage
                        WHERE "id" = 2 LIMIT 1
                    )::INTEGER;
                END IF;
            END IF;

            RETURN NULL;
        END;
        $$ LANGUAGE 'plpgsql';

        DROP TRIGGER IF EXISTS
            CRM_LEAD_ENSURE_VALID_REASON_BEFORE_INSERT ON crm_lead CASCADE;

        CREATE TRIGGER CRM_LEAD_ENSURE_VALID_REASON_BEFORE_INSERT
            BEFORE INSERT ON crm_lead FOR EACH ROW
            EXECUTE PROCEDURE ENSURE_VALID_REASON ();

        DROP TRIGGER IF EXISTS
            CRM_LEAD_ENSURE_VALID_REASON_BEFORE_UPDATE ON crm_lead CASCADE;

        CREATE TRIGGER CRM_LEAD_ENSURE_VALID_REASON_BEFORE_UPDATE
            BEFORE UPDATE ON crm_lead FOR EACH ROW
            EXECUTE PROCEDURE ENSURE_VALID_REASON ();
    """
