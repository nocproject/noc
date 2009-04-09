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
import noc.main.search # Set up signal handlers

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
