# ---------------------------------------------------------------------
# DatabaseStorage
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party models
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.db import models
import psycopg2

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.fields import BinaryField


class _DatabaseStorage(Storage):
    """
    Database File Storage (PostgreSQL)
    Stores files in database table.
    Table must have at least following columns:
      File Name (Character Type) - contains full virtual path
      Binary Data (BYTEA) - File content
      Size (Integer Type) - File size (in octets)
      Modification Time (Timestamp) - Last modification time
    Table name and field names must be set up via
    "option" variable. "option" is a hash with following keys:
      db_table
      name_field
      data_field
      size field
      mtime_field
    """

    def __init__(self, option):
        self.db_table = option["db_table"]
        self.name_field = option["name_field"]
        self.data_field = option["data_field"]
        self.size_field = option["size_field"]
        self.mtime_field = option["mtime_field"]

    def get_cursor(self):
        from django.db import connection

        return connection.cursor()

    def _open(self, name, mode="rb"):
        """
        Internal implementation of the open()

        :param name: Full path
        :param mode: File mode (ignored)
        :return: File object or None
        """
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT %s FROM %s WHERE %s=%%s" % (self.data_field, self.db_table, self.name_field),
            [name],
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return ContentFile(row[0])

    def _save(self, name, content):
        """
        :param name: Full path
        :param content: File object
        :return: File name
        """
        cursor = self.get_cursor()
        binary = content.read()
        size = len(binary)
        binary = psycopg2.Binary(binary)
        if self.exists(name):
            cursor.execute(
                "UPDATE %s SET %s=%%s,%s='now',%s=%%s WHERE %s=%%s"
                % (
                    self.db_table,
                    self.data_field,
                    self.mtime_field,
                    self.size_field,
                    self.name_field,
                ),
                [binary, size, name],
            )
        else:
            cursor.execute(
                "INSERT INTO %s(%s,%s,%s,%s) VALUES(%%s,'now',%%s,%%s)"
                % (
                    self.db_table,
                    self.name_field,
                    self.mtime_field,
                    self.size_field,
                    self.data_field,
                ),
                [name, size, binary],
            )
        return name

    def exists(self, name):
        """
        Check file exists
        :param name: Full path
        :return: True if file exists
        """
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM %s WHERE %s=%%s" % (self.db_table, self.name_field), [name]
        )
        return cursor.fetchone()[0] > 0

    def path(self, name):
        """
        Returns full filesystem path as specified in Storage API.
        Raises NotImplementedError because Storage is not related to filesystem

        :param name:
        :return:
        """
        raise NotImplementedError

    def size(self, name):
        """
        Get file size
        :param name: Full name
        :return: File size
        """
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT %s FROM %s WHERE %s=%%s" % (self.size_field, self.db_table, self.name_field),
            [name],
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            return 0

    def url(self, name):
        pass

    def delete(self, name):
        """
        Deletes file
        :param name: Full path
        :return:
        """
        cursor = self.get_cursor()
        cursor.execute("DELETE FROM %s WHERE %s=%%s" % (self.db_table, self.name_field), [name])

    def get_available_name(self, name):
        """
        Returns converted file name (Required by Storage API)
        :param name:
        :return:
        """
        return name

    def listdir(self, name):
        """
        Returns a directory listing

        :param name: Full path of directory
        :return: List of file names
        """
        cursor = self.get_cursor()
        if not name.endswith("/"):
            name += "/"
        ln = len(name)
        cursor.execute(
            "SELECT %s FROM %s WHERE %s ~ '^%s[^/]+/?$'"
            % (self.name_field, self.db_table, self.name_field, name.replace("'", "\\'"))
        )
        return [x[0][ln:] for x in cursor.fetchall()]

    def stat(self, name):
        """
        Get file stats. Stats is a hash of:
        * name - full path
        * size - file size
        * mtime - last modification time
        :param name:
        :return:
        """
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT %s,%s FROM %s WHERE %s=%%s"
            % (self.size_field, self.mtime_field, self.db_table, self.name_field),
            [name],
        )
        row = cursor.fetchone()
        if row:
            return {"name": "name", "size": row[0], "mtime": row[1]}
        else:
            return None

    def set_mtime(self, name, mtime):
        """
        Set file's mtime
        :param name:
        :param mtime:
        :return:
        """
        cursor = self.get_cursor()
        cursor.execute(
            "UPDATE %s SET %s=%%s WHERE %s=%%s"
            % (self.db_table, self.mtime_field, self.name_field),
            [mtime, name],
        )


class DatabaseStorage(NOCModel):
    """
    Database Storage
    """

    class Meta(object):
        app_label = "main"
        db_table = "main_databasestorage"
        verbose_name = "Database Storage"
        verbose_name_plural = "Database Storage"

    name = models.CharField("Name", max_length=256, unique=True)
    data = BinaryField("Data")
    size = models.IntegerField("Size")
    mtime = models.DateTimeField("MTime")

    # Options for DatabaseStorage

    @classmethod
    def dbs_options(cls):
        return {
            "db_table": DatabaseStorage._meta.db_table,
            "name_field": "name",
            "data_field": "data",
            "mtime_field": "mtime",
            "size_field": "size",
        }

    @classmethod
    def get_dbs(cls):
        """
        Get DatabaseStorage instance
        """
        return _DatabaseStorage(cls.dbs_options())


# Default database storage
database_storage = DatabaseStorage.get_dbs()
