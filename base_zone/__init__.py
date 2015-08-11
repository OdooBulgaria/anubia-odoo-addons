# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from . import models
from . import tests

# --------------------------- INSTALLATION HOOKS ------------------------------

from logging import getLogger
_logger = getLogger(__name__)


def uninstall_hook(cr, registry):
    """ Clear uneccesary SQL procedures and triggers """

    _logger.debug('Proccessing uninstallation hook')

    cr.execute("""
        DROP FUNCTION IF EXISTS GET_CHILD_ZONES(INT) CASCADE;
        DROP FUNCTION IF EXISTS ENSURE_ADDED_DEFAULT_USER_ID() CASCADE;
        DROP FUNCTION IF EXISTS ENSURE_DELETED_DEFAULT_USER_ID() CASCADE;
    """)

