# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from . import models

# --------------------------- INSTALLATION HOOKS ------------------------------

from logging import getLogger
_logger = getLogger(__name__)


def uninstall_hook(cr, registry):
    """ Clear uneccesary SQL procedures and triggers """

    _logger.debug('Proccessing uninstallation hook')

    cr.execute("""
        DROP TRIGGER IF EXISTS
            CRM_LEAD_ENSURE_VALID_REASON_BEFORE_INSERT ON crm_lead CASCADE;

        DROP TRIGGER IF EXISTS
            CRM_LEAD_ENSURE_VALID_REASON_BEFORE_UPDATE ON crm_lead CASCADE;

        DROP FUNCTION IF EXISTS ENSURE_VALID_REASON() CASCADE;
    """)

