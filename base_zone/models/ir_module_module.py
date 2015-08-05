# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models, api
from logging import getLogger


_logger = getLogger(__name__)


###############################################################################
#             ___ __  __ ____   ___  ____ _____  _    _   _ _____             #
#            |_ _|  \/  |  _ \ / _ \|  _ \_   _|/ \  | \ | |_   _|            #
#             | || |\/| | |_) | | | | |_) || | / _ \ |  \| | | |              #
#             | || |  | |  __/| |_| |  _ < | |/ ___ \| |\  | | |              #
#            |___|_|  |_|_|    \___/|_| \_\|_/_/   \_\_| \_| |_|              #
#                                                                             #
# This model has been overwritten with the sole purpose of clear some SQL was #
# added over the Odoo ORM. Code below searches for all models in module which #
# have a method named ``auto_remove`` and call this during the uninstallation #
# proccess.                                                                   #
###############################################################################


class IrModuleModule(models.Model):
    """ Extended model to add needed behavior to remove SQL procedures and
    otherswhen module is removed.
    """

    _inherit = ['ir.module.module']

    _this_module = 'base_zone'

    # ------------------------- OVERWRITTEN METHODS ---------------------------

    @api.multi
    def module_uninstall(self):
        """ Overwritten method to remove SQL procedures and others """

        # STEP 1: Check if base_zone is being uninstalled
        if self._is_being_uninstalled(self._this_module):

            # STEP 2: Call auto_remove method in all models with this method
            for model in self._get_models_with_auto_remove(self._this_module):
                self._log(0, u'Call {}, auto_remove', model.model)
                self.env[model.model].auto_remove()

        # STEP 3: Call parent method
        return super(IrModuleModule, self).module_uninstall()

    # -------------------------- AUXILIARY METHODS ----------------------------

    @api.multi
    def _is_being_uninstalled(self, mod_name):
        """ This method is called from module_uninstall to determine is a
        module is in the recordset of modules to be uninstalled.

        :param mod_name: name of the module to be checked
        :return: returns TRUE if module is in recordset of FALSE otherwise
        """

        return bool(self.filtered(lambda x: x.name == self._this_module))

    @api.model
    def _get_models_with_auto_remove(self, mod_name):
        """ This method is called from module_uninstall method get all models
        in the module which contains a method named auto_remove. This method
        will be used to remove SQL procedures and others.

        :param mod_name: name of the module which contains the models
        :return: ir.module recordset of all the models which have auto_remove
        method
        """

        ir_data_domain = [
            '&',
            ('model', '=', 'ir.model'),
            ('module', '=', mod_name)
        ]
        ir_data_obj = self.env['ir.model.data']
        ir_data_set = ir_data_obj.search(ir_data_domain)

        model_obj = self.env['ir.model']
        model_set = model_obj.browse(ir_data_set.mapped('res_id'))

        return model_set.filtered(
            lambda x: 'auto_remove' in dir(x.env[x.model]))

    def _log(self, level, msg_format, *args, **kwargs):
        """ Outputs an formated string in log

            :param level (int): 0=> debug, 1=> info, 2=> warning, 3=> error
            :param message (basestring): name of the message
        """

        methods = ['debug', 'info', 'warning', 'error']
        log = getattr(_logger, methods[level])

        msg = msg_format.format(*args, **kwargs)
        log(msg)
