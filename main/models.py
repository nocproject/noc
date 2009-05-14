# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.db import models
from noc.main.report import report_registry
from noc.main.menu import populate_reports
from noc.main.menu import Menu
from noc.lib.fields import BinaryField
from noc.lib.database_storage import DatabaseStorage as DBS
import noc.main.search # Set up signal handlers
import os

##
## Languages
##
class Language(models.Model):
    class Meta:
        verbose_name="Language"
        verbose_name_plural="Languages"
        ordering=("name",)
    name=models.CharField("Name",max_length=32,unique=True)
    native_name=models.CharField("Native Name",max_length=32)
    is_active=models.BooleanField("Is Active",default=False)
    def __unicode__(self):
        return self.name
##
##
##
class DatabaseStorage(models.Model):
    class Meta:
        verbose_name="Database Storage"
        verbose_name_plural="Database Storage"
    name=models.CharField("Name",max_length=256,unique=True)
    data=BinaryField("Data")
    size=models.IntegerField("Size")
    mtime=models.DateTimeField("MTime")
    ##
    ## Options for DatabaseStorage
    ##
    @classmethod
    def dbs_options(cls):
        return {
            "db_table"     : DatabaseStorage._meta.db_table,
            "name_field"  : "name",
            "data_field"  : "data",
            "mtime_field" : "mtime",
            "size_field"  : "size",
        }
    ##
    ## Returns DatabaseStorage instance
    ##
    @classmethod
    def get_dbs(cls):
        return DBS(cls.dbs_options())
##
## Default database storage
##
database_storage=DatabaseStorage.get_dbs()
##
## Extension to MIME-type mapping
##
class MIMEType(models.Model):
    class Meta:
        verbose_name="MIME Type"
        verbose_name_plural="MIME Types"
    extension=models.CharField("Extension",max_length=32,unique=True)
    mime_type=models.CharField("MIME Type",max_length=63)
    def __unicode__(self):
        return u"%s -> %s"%(self.extension,self.mime_type)
    ##
    ## Determine MIME type from filename
    ##
    @classmethod
    def get_mime_type(cls,filename):
        r,ext=os.path.splitext(filename)
        try:
            m=MIMEType.objects.get(extension=ext)
            return m.mime_type
        except MIMEType.DoesNotExist:
            return "application/octet-stream"

##
## Application Menu
##
class AppMenu(Menu):
    app="main"
    title="Main"
    items=[
        ("Setup", [
            ("Users",  "/admin/auth/user/",  "auth.change_user"),
            ("Groups", "/admin/auth/group/", "auth.change_group"),
            ("Languages","/admin/main/language/", "main.change_language"),
            ("MIME Types", "/admin/main/mimetype/", "main.change_mimetype"),
            ("Configs",    "/main/config/",  "is_superuser()"),
        ]),
        ("Documentation", [
            ("Administrator's Guide", "/static/doc/en/ag/html/index.html"),
            ("User's Guide", "/static/doc/en/ug/html/index.html"),
        ]),
    ]
##
## Load and register reports
##
report_registry.register_all()
populate_reports([(n,r.title) for n,r in report_registry.classes.items()])
