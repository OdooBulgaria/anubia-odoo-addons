# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp import models

from logging import getLogger


_logger = getLogger(__name__)


class BaseZoneMiddleRelationship(models.AbstractModel):
    """ It provides methods for replace intermediate tables with views.
        To automatically replace middle relation with view, just add a model
        attribute named as `prefix_relationname`, where prefix is the value of
        self._prefix.
    """

    _name = 'base.zone.middle.relationship'
    _description = u'Base zone middle relationship'

    _prefix = '_sql_view_select_'  # Prefix to search select queries

    # ------------------------- OVERWRITTEN METHODS ---------------------------

    def _auto_end(self, cr, context=None):
        """ Overwritten method which replaces middle tables with views
        """

        _super = super(BaseZoneMiddleRelationship, self)
        result = _super._auto_end(cr, context)

        arguments = self._get_middle_views_sql_queries()
        for m2m_tbl, sql_select in arguments.iteritems():
            self._sql_create_middle_view(cr, m2m_tbl, sql_select)

        return result

    # -------------------------- AUXILIARY METHODS ----------------------------

    def _sql_create_middle_view(self, cr, m2m_tbl, sql_select):
        """ Create middle view relations as views instead tables

            :param cr: database cursor
            :m2m_tbl: name of the middle relation
            :sql_select: sql select query to be set inside view

            :return: true if the relation had been created
        """

        # STEP 1: Initialice variables
        had_been_created = False

        # STEP 2: Gets the type of existing relation (it can not exist)
        type_sql = self._sql_relkind.format(m2m_tbl)
        cr.execute(type_sql)
        relkind = (cr.fetchone() or (False,))[0]

        # STEP 3: Removes existing relation (TABLE of VIEW)
        if relkind:
            had_been_created = True
            ttype = 'TABLE' if relkind == 'r' else 'VIEW'
            drop_sql = self._sql_drop_relation.format(ttype, m2m_tbl)
            cr.execute(drop_sql)

        # STEP 4: Creates new relation (VIEW)
        create_sql = self._sql_create_view.format(m2m_tbl, sql_select)
        cr.execute(create_sql)

        # STEP 5: Add Rules to prevent INSERT, UPDATE AND DELETE are added
        sql_no_crud = self._sql_no_crud.format(m2m_tbl)
        cr.execute(sql_no_crud)

        # STEP 6: Returns true if the relation had been created
        # @see: _m2m_raise_or_create_relation method in openerp.models
        if had_been_created:
            return True

    def _get_middle_views_sql_queries(self):
        """ Builds a dictionary with all the view names and sql select queries
            which will be used to create the views

            :return: dictionary {view_name: sql_select_query}
        """

        sql_queries = {}

        # STEP 2: filter model attributes searching sql queries with prefix
        prefix = self._prefix
        prefix_len = len(prefix)
        middle_views = filter(lambda x: x[:prefix_len] == prefix, dir(self))

        # STEP 3: build a dictionary with all the {view_name: sql_select_query}
        # removing prefix form model attribute
        for middle_view in middle_views:
            m2m_tbl = middle_view[prefix_len:]
            sql_select = getattr(self, middle_view)
            if sql_select:
                # STEP 4: prevent creation from multiple models
                # This is an optional behavior, if sql select is False in one
                # model this do not performs the creation of the middle view
                sql_queries.update({m2m_tbl: sql_select})

        return sql_queries

    def _is_middle_view(self, m2m_tbl):
        """ Check if exists an attribute with the sql select query for relation
            This attribute must be like `prefix_relationname`

            :param: name of the relation which will be checked
        """

        sql_select_attribute_name = '{}{}'.format(self._prefix, m2m_tbl)
        return hasattr(self, sql_select_attribute_name)

    # ---------------------------- SQL QUERTIES -------------------------------

    _sql_relkind = """
        SELECT
            relkind
        FROM
            pg_class
        WHERE
            relkind IN ('r', 'v')
        AND relname = '{}';
    """

    _sql_drop_relation = """
        DROP {} IF EXISTS {} CASCADE
    """

    _sql_create_view = """
        CREATE OR REPLACE VIEW {} AS ({})
    """

    _sql_no_crud = """
        CREATE OR REPLACE
            RULE {0}_no_update
            AS ON UPDATE TO {0}
            DO INSTEAD NOTHING;

        CREATE OR REPLACE
            RULE {0}_no_insert
            AS ON INSERT TO {0}
            DO INSTEAD NOTHING;

        CREATE OR REPLACE
            RULE {0}_no_delete
            AS ON DELETE TO {0}
            DO INSTEAD NOTHING;
    """
