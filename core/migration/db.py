# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Migration db property
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db as south_db
from django.db.models import AutoField


class DB(object):
    """
    PostgreSQL database migration operations
    """
    def create_table(self, name, fields):
        south_db.create_table(name, fields)

    def delete_table(self, name):
        south_db.delete_table(name)

    def add_column(self, table_name, field_name, field_def):
        south_db.add_column(table_name, field_name, field_def)

    def alter_column(self, table_name, field_name, field_def):
        south_db.alter_column(table_name, field_name, field_def)

    def delete_column(self, table_name, field_name):
        south_db.delete_column(table_name, field_name)

    def rename_column(self, table_name, from_name, to_name):
        south_db.rename_column(table_name, from_name, to_name)

    def execute(self, query, *args):
        return south_db.execute(query, *args)

    def create_index(self, table_name, fields, unique=False, db_tablespace=""):
        south_db.create_index(table_name, fields, unique=unique, db_tablespace=db_tablespace)

    def mock_model(self, model_name, db_table, db_tablespace='',
                   pk_field_name='id', pk_field_type=AutoField,
                   pk_field_args=None, pk_field_kwargs=None):
        return south_db.mock_model(
            model_name=model_name,
            db_table=db_table,
            db_tablespace=db_tablespace,
            pk_field_name=pk_field_name,
            pk_field_type=pk_field_type,
            pk_field_args=pk_field_args or [],
            pk_field_kwargs=pk_field_kwargs or {}
        )


# Singleton
db = DB()
