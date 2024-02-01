# ----------------------------------------------------------------------
# Migration db property
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime

# Third-party modules
from django.db.models import AutoField
from django.db import connection
from django.db.backends.utils import names_digest, truncate_name

logger = logging.getLogger("migration")


class DB(object):
    """
    PostgreSQL database migration operations
    """

    MAX_NAME_LENGTH = 63

    def __init__(self):
        self.deferred_sql = []

    @staticmethod
    def quote_name(name):
        return connection.ops.quote_name(name)

    def has_table(self, table_name):
        return bool(
            self.execute("SELECT COUNT(*) FROM pg_class WHERE relname=%s", [table_name])[0][0]
        )

    def create_table(self, table_name, fields):
        assert len(table_name) <= self.MAX_NAME_LENGTH, "Too long table name"
        columns = [self.column_sql(table_name, field_name, field) for field_name, field in fields]
        self.execute(
            "CREATE TABLE %s (%s)"
            % (self.quote_name(table_name), ", ".join(col for col in columns if col))
        )
        self.execute_deferred_sql()

    def delete_table(self, table_name, cascade=True):
        tn = self.quote_name(table_name)
        if cascade:
            self.execute("DROP TABLE %s CASCADE;" % tn)
        else:
            self.execute("DROP TABLE %s;" % tn)

    def has_column(self, table_name, name):
        """
        Check if table has column
        :param table_name: Table name
        :param name: Column name
        :return: True, if table has column, False otherwise
        """
        return self.execute(
            """
            SELECT EXISTS(
              SELECT 1
              FROM information_schema.columns
              WHERE table_name=%s AND column_name=%s
            )""",
            [table_name, name],
        )[0][0]

    def add_column(self, table_name, name, field):
        sql = "ALTER TABLE %s ADD COLUMN %s;" % (
            self.quote_name(table_name),
            self.column_sql(table_name, name, field),
        )
        self.execute(sql)
        self.execute_deferred_sql()

    def delete_column(self, table_name, field_name):
        sql = "ALTER TABLE %s DROP COLUMN %s CASCADE;" % (
            self.quote_name(table_name),
            self.quote_name(field_name),
        )
        self.execute(sql)

    def rename_column(self, table_name, old, new):
        if old == new:
            return
        sql = "ALTER TABLE %s RENAME COLUMN %s TO %s;" % (
            self.quote_name(table_name),
            self.quote_name(old),
            self.quote_name(new),
        )
        self.execute(sql)

    def execute(self, sql, params=None):
        """
        Executes the given SQL statement, with optional parameters
        :param sql: SQL statement
        :param params: List of positional parameters
        :return:
        """
        params = params or []
        logger.debug("[SQL] %s (%s)", sql, params)
        cursor = connection.cursor()
        cursor.execute(sql, params)
        try:
            return cursor.fetchall()
        except Exception:
            return []

    def create_index(self, table_name, column_names, unique=False):
        if not column_names:
            return
        # Generate index name
        idx_table_name = table_name.replace('"', "").replace(".", "_")
        index_unique_name = ""

        if len(column_names) > 1:
            index_unique_name = "_%x" % abs(hash((table_name, ",".join(column_names))))

        # If the index name is too long, truncate it
        index_name = (
            ("%s_%s%s" % (idx_table_name, column_names[0], index_unique_name))
            .replace('"', "")
            .replace(".", "_")
        )
        if len(index_name) > 63:
            part = "_%s%s" % (column_names[0], index_unique_name)
            index_name = "%s%s" % (idx_table_name[: self.MAX_NAME_LENGTH - len(part)], part)
        #
        sql = "CREATE %sINDEX %s ON %s (%s);" % (
            "UNIQUE " if unique else "",
            self.quote_name(index_name),
            self.quote_name(table_name),
            ",".join(self.quote_name(field) for field in column_names),
        )
        self.execute(sql)

    def mock_model(
        self,
        model_name,
        db_table,
        pk_field_name="id",
        pk_field_type=AutoField,
        pk_field_args=None,
        pk_field_kwargs=None,
    ):
        pk_field_args = pk_field_args or []
        pk_field_kwargs = pk_field_kwargs or {}

        class MockOptions(object):
            def __init__(self, model):
                self.db_table = db_table
                self.db_tablespace = ""
                self.object_name = model_name
                self.model_name = model_name
                self.module_name = model_name.lower()
                self.auto_field = None
                self.model = model
                self.concrete_model = model
                if pk_field_type == AutoField:
                    pk_field_kwargs["primary_key"] = True
                self.pk = pk_field_type(*pk_field_args, **pk_field_kwargs)
                self.pk.set_attributes_from_name(pk_field_name)
                self.pk.model = model
                self.abstract = False

            def get_field_by_name(self, field_name):
                # we only care about the pk field
                return self.pk, self.model, True, False

            def get_field(self, name):
                # we only care about the pk field
                return self.pk

        class MockModel(object):
            _meta = None

        # We need to return an actual class object here, not an instance
        MockModel._meta = MockOptions(MockModel)
        return MockModel

    def column_sql(self, table_name, field_name, field, with_name=True, field_prepared=False):
        """
        Create the SQL snippet for a column.
        """
        # If the field hasn't already been told its attribute name, do so.
        if not field_prepared:
            field.set_attributes_from_name(field_name)

        sql = []
        params = []
        if with_name:
            sql += [self.quote_name(field.column)]
        sql += [field.db_type(connection)]
        type_suffix = field.db_type_suffix(connection)
        if type_suffix:
            sql += [type_suffix]
        # NULL/NOT NULL
        sql += ["NULL" if field.null else "NOT NULL"]
        # PRIMARY KEY/UNIQUE
        if field.primary_key:
            sql += ["PRIMARY KEY"]
        elif field.unique:
            sql += ["UNIQUE"]
        # DEFAULT
        if field.has_default():
            default = field.get_default()
            if default is not None:
                if callable(default):
                    default = default()
                if isinstance(default, str):
                    default = "'%s'" % default.replace("'", "''")
                elif isinstance(default, (datetime.date, datetime.time, datetime.datetime)):
                    default = "'%s'" % default
                if isinstance(default, str):
                    default = default.replace("%", "%%")
                sql += ["DEFAULT %s" % default]
                params += [default]
            elif (not field.null and field.blank) or (field.get_default() == ""):
                if (
                    field.empty_strings_allowed
                    and connection.features.interprets_empty_strings_as_nulls
                ):
                    sql += [" DEFAULT ''"]
        # FOREIGN KEY
        if field.remote_field:
            self.deferred_sql += [
                self._foreign_key_sql(
                    table_name,
                    field.column,
                    field.remote_field.model._meta.db_table,
                    field.remote_field.model._meta.get_field(field.remote_field.field_name).column,
                )
            ]
        # Indexes
        model = self.mock_model("FakeModelForGISCreation", table_name)
        self.deferred_sql += self._sql_indexes_for_field(model, field)
        sql = " ".join(sql)
        return sql % params

    def _foreign_key_sql(self, from_table_name, from_column_name, to_table_name, to_column_name):
        """
        Generates a full SQL statement to add a foreign key constraint
        """
        constraint_name = "%s_refs_%s_%x" % (
            from_column_name,
            to_column_name,
            abs(hash((from_table_name, to_table_name))),
        )
        return "ALTER TABLE %s ADD CONSTRAINT %s FOREIGN KEY (%s) REFERENCES %s (%s)%s;" % (
            self.quote_name(from_table_name),
            self.quote_name(truncate_name(constraint_name, connection.ops.max_name_length())),
            self.quote_name(from_column_name),
            self.quote_name(to_table_name),
            self.quote_name(to_column_name),
            connection.ops.deferrable_sql(),  # Django knows this
        )

    def execute_deferred_sql(self):
        for sql in self.deferred_sql:
            self.execute(sql)
        self.deferred_sql = []

    def _sql_indexes_for_field(self, model, field):
        """
        Return the CREATE INDEX SQL statements for a single model field

        :param model:
        :param field:
        :return:
        """

        def qn(name):
            if name.startswith('"') and name.endswith('"'):
                return name  # Quoting once is enough.
            return '"%s"' % name

        max_name_length = 63

        if field.db_index and not field.unique:
            i_name = names_digest(model._meta.db_table, field.column, length=8)
            return [
                "CREATE INDEX %s ON %s(%s)"
                % (
                    qn(truncate_name(i_name, max_name_length)),
                    qn(model._meta.db_table),
                    qn(field.column),
                )
            ]
        return []


# Singletone
db = DB()
