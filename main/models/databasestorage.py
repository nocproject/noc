# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DatabaseStorage
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party models
from django.db import models
# NOC modules
from noc.core.model.fields import BinaryField
from noc.lib.database_storage import DatabaseStorage as DBS


class DatabaseStorage(models.Model):
    """
    Database Storage
    """

    class Meta:
        app_label = "main"
        db_table = "main_databasestorage"
        verbose_name = "Database Storage"
        verbose_name_plural = "Database Storage"

    name = models.CharField("Name", max_length=256, unique=True)
    data = BinaryField("Data")
    size = models.IntegerField("Size")
    mtime = models.DateTimeField("MTime")

    ##
    ## Options for DatabaseStorage
    ##
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
        return DBS(cls.dbs_options())


#
# Default database storage
#
database_storage = DatabaseStorage.get_dbs()
