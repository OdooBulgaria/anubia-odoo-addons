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


    is_invalid = fields.Boolean(
        string='Is not valid',
        required=False,
        readonly=False,
        index=False,
        default=True,
        help='Checked when lead/opportunity is not valid, unchecked otherwise'
    )


    # -------------------------------- CRUD -----------------------------------

    @api.model
    def create(self, values):
        """ Overwritten method to ensure the integrity between reason and stage
        and foce the ``is_invalid`` for certain reasons.
        """

        self._ensure_is_invalid_in_values(values)
        self._ensure_reason_for_stage(values)

        return super(CrmLead, self).create(values)

    @api.multi
    def write(self, values):
        """ Overwritten method to ensure the integrity between reason and stage
        and foce the ``is_invalid`` for certain reasons.
        """

        self._ensure_is_invalid_in_values(values)
        self._ensure_reason_for_stage(values)

        return super(CrmLead, self).write(values)

    # -------------------------- AUXILIAR METHODS -----------------------------

    @classmethod
    def _get_reason_which_has_been_set(cls, values):
        """ Determines if user has set the lead/opportunity reason to a non
        NULL value

        :param values: ``values`` given to the ``write`` or ``create`` method
        :return: True when new non null values has been set of False otherwise
        """

        return 'crm_reason_id' in values and values['crm_reason_id'] or None

    def _ensure_is_invalid_in_values(self, _in_out_values):
        """ Updates de values dictionary to ensure is_invalid
        """

        reason_id = self._get_reason_which_has_been_set(_in_out_values)

        if reason_id:
            reason_obj = self.env['crm.stage.reason']
            reason_set = reason_obj.browse(reason_id)

            if reason_set.force_invalid:
                _in_out_values.update({'is_invalid': True})

        return _in_out_values

    @classmethod
    def _get_stage_and_reason_values(cls, values):
        """ Gets the new value for these fields: stage_id and crm_reason_id
        If the field will not be updated, returned value will be ``None``

        :param values: dictionary provided by `create` or `write` method
        :return: (stage_id, crm_reason_id). Both values in the tuple can be
        None or False, this last means value has not been updated by user.
        """

        return (
            values.get('stage_id', False),
            values.get('crm_reason_id', False)
        )

    def _get_reasons_from_stage(self, stage_id):
        """ Get all valid reasons and the default reason for ``crm.case.stage``
        with the given ``id``

        :param stage_id: unique identifier of the ``crm.case.stage``
        :return: tuple with a list of unique identifiers of the valid reasons
        and the unique idenfier of the default reason. The returned list can
        be an empty list ``[]`` and default reason can be ``None``.
        """

        stage_obj = self.env['crm.case.stage']
        stage_set = stage_obj.browse(stage_id)

        valid_reason_ids = stage_set.crm_reason_ids.mapped('id')
        default_reason_id = stage_set.default_crm_reason_id and \
            stage_set.default_crm_reason_id.id or None

        return (valid_reason_ids, default_reason_id)

    def _get_stages_from_reason(self, reason_id):
        """ Get all valid stages for ``crm.stage.reason`` with the given ``id``

        :param reason_id: unique identifier of the ``crm.stage.reason``
        :return: tuple with a list of unique identifiers of the valid stages,
        this can be an empty list ``[]``.
        """

        reason_obj = self.env['crm.stage.reason']
        reason_set = reason_obj.browse(reason_id)

        return reason_set.crm_stages_ids.mapped('id')

    @api.multi
    def _ensure_reason_for_stage(self, values):
        """ Checks and tries to update ``crm_reason_id`` according ``stage_id``
        Method has several asserts, these force an error if the new reason
        can not be updated in all the ``self`` recordset entries.

        | new_stage_id  | new_reason_id | action                           |
        | ------------- | ------------- | -------------------------------- |
        |    False      |    False      |                                  |
        |    False      |    None       | 'crm_reason_id': None (*)        |
        |    False      |    Not None   | checks new reason in ``self``    |
        |    None       |    False      | 'crm_reason_id': None            |
        |    None       |    None       | 'crm_reason_id': None (*)        |
        |    None       |    Not None   | Launch an error always           |
        |    Not None   |    False      | Add default reason in values     |
        |    Not None   |    None       | 'crm_reason_id': None (*)        |
        |    Not None   |    Not None   | Check if new reason in new stage |
        (*) not absolutely necessary

        :param values: dictionary  used in ``create`` and ``write`` methods
        :return: updated values dictionary
        """

        error_message = _(
            u'The given reason is not valid for some of the stages of cases')

        # STEP 1: Get new values for stage_id or reason_id or False
        new_stage_id, new_reason_id = self._get_stage_and_reason_values(values)

        # STEP 2: If only reason has been changed, it must be valid for all
        # existing stages in ``self``.
        # Note: ``new_stage_id is False`` separately to keeps the chain
        if new_stage_id is False:
            if new_reason_id:
                valid_ids = self._get_stages_from_reason(new_reason_id)
                assert self and not self.filtered(
                    lambda x: x.stage_id and x.stage_id.id not in valid_ids), \
                    error_message

        # STEP 3: new reason will be set to ``None`` or ir raises an error
        elif new_stage_id is None:
            assert not new_reason_id, error_message
            values.update({'crm_reason_id': None})

        # STEP 4: default reason for stage, ``None`` or verify in ``self``
        elif new_reason_id is not None:
            valid_ids, default_id = self._get_reasons_from_stage(new_stage_id)
            if new_reason_id is False:
                values.update({'crm_reason_id': default_id})
            else:
                assert new_reason_id in valid_ids, error_message

        return values

    @classmethod
    def _log(cls, level, msg_format, *args, **kwargs):
        """ Outputs an formated string in log

            :param level (int): 0=> debug, 1=> info, 2=> warning, 3=> error
            :param message (basestring): name of the message
        """

        methods = ['debug', 'info', 'warning', 'error']
        log = getattr(_logger, methods[level])

        msg = msg_format.format(*args, **kwargs)
        log(msg)


