# ---------------------------------------------------------------------
# Database File Storage (PostgreSQL only)
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
import psycopg2


class DatabaseStorage(Storage):
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
            f"SELECT {self.data_field} FROM {self.db_table} WHERE {self.name_field}=%s", [name]
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
                f"UPDATE {self.db_table} "
                f"SET {self.data_field}=%s, {self.mtime_field}='now', {self.size_field}=%s "
                f"WHERE {self.name_field}=%s",
                [binary, size, name],
            )
        else:
            cursor.execute(
                f"INSERT INTO {self.db_table} "
                f"({self.name_field}, {self.mtime_field}, {self.size_field}, {self.data_field}) "
                f"VALUES (%s, 'now', %s, %s)",
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
        cursor.execute(f"SELECT COUNT(*) FROM {self.db_table} WHERE {self.name_field}=%s", [name])
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
            f"SELECT {self.size_field} FROM {self.db_table} WHERE {self.name_field}=%s", [name]
        )
        row = cursor.fetchone()
        if row:
            return row[0]
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
        cursor.execute(f"DELETE FROM {self.db_table} WHERE {self.name_field}=%s", [name])

    def get_available_name(self, name, max_length=None):
        """
        Returns converted file name (Required by Storage API)
        :param name:
        :param max_length:
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
        name = name.replace("'", "\\'")
        regexp = f"^{name}[^/]+/?$"
        cursor.execute(
            f"SELECT {self.name_field} FROM {self.db_table} WHERE {self.name_field} ~ %s",
            [regexp],
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
            f"SELECT {self.size_field}, {self.mtime_field} FROM {self.db_table} "
            f"WHERE {self.name_field}=%s",
            [name],
        )
        row = cursor.fetchone()
        if row:
            return {"name": "name", "size": row[0], "mtime": row[1]}
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
            f"UPDATE {self.db_table} SET {self.mtime_field}=%s WHERE {self.name_field}=%s",
            [mtime, name],
        )
