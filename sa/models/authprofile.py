# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AuthProfile
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## NOC modules


class AuthProfile(models.Model):
    class Meta:
        verbose_name = "Auth Profile"
        verbose_name_plural = "Auth Profiles"
        db_table = "sa_authprofile"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", null=True, blank=True)
    type = models.CharField("Name", max_length=1, choices=[
        ("G", "Local Group"),
        ("R", "RADIUS"),
        ("T", "TACACS+"),
        ("L", "LDAP")
    ])
    user = models.CharField(
        "User", max_length=32, blank=True, null=True)
    password = models.CharField(
        "Password", max_length=32, blank=True, null=True)
    super_password = models.CharField(
        "Super Password", max_length=32, blank=True, null=True)
    snmp_ro = models.CharField(
        "RO Community", blank=True, null=True, max_length=64)
    snmp_rw = models.CharField(
        "RW Community", blank=True, null=True, max_length=64)

    def __unicode__(self):
        return self.name
