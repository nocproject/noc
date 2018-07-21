# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# AuthProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
# Third-party modules
from django.db import models
import cachetools
# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.core.model.decorator import on_save
from noc.core.cache.base import cache
from noc.core.model.decorator import on_delete_check
from noc.core.model.fields import TagsField, DocumentReferenceField
from noc.core.bi.decorator import bi_sync

id_lock = Lock()


@on_save
@bi_sync
@on_delete_check(check=[
    ("sa.ManagedObject", "auth_profile"),
    ("sa.ManagedObjectProfile", "cpe_auth_profile")
])
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
        ("L", "LDAP"),
        ("S", "Suggest")
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
    # Integration with external NRI systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem,
                                           null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.BigIntegerField(unique=True)

    tags = TagsField("Tags", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        try:
            return AuthProfile.objects.get(id=id)
        except AuthProfile.DoesNotExist:
            return None

    def on_save(self):
        if not self.enable_suggest:
            cache.delete_many([
                "cred-%s" % x
                for x in self.managedobject_set.values_list("id", flat=True)
            ])

    @property
    def enable_suggest(self):
        return self.type == "S"

    def iter_snmp(self):
        """
        Yield all possible snmp_ro, snmp_rw tuples
        :return:
        """
        if self.enable_suggest:
            for s in self.authprofilesuggestsnmp_set.all():
                yield s.snmp_ro, s.snmp_rw

    def iter_cli(self):
        """
        Yield all possible user, password, super_password
        :return:
        """
        if self.enable_suggest:
            for s in self.authprofilesuggestcli_set.all():
                yield s.user, s.password, s.super_password


class AuthProfileSuggestSNMP(models.Model):
    class Meta:
        verbose_name = "Auth Profile Suggest SNMP"
        verbose_name_plural = "Auth Profile Suggest SNMP"
        db_table = "sa_authprofilesuggestsnmp"
        app_label = "sa"

    auth_profile = models.ForeignKey(AuthProfile, verbose_name="Auth Profile")
    snmp_ro = models.CharField(
        "RO Community", blank=True, null=True, max_length=64)
    snmp_rw = models.CharField(
        "RW Community", blank=True, null=True, max_length=64)

    def __unicode__(self):
        return self.auth_profile.name


class AuthProfileSuggestCLI(models.Model):
    class Meta:
        verbose_name = "Auth Profile Suggest CLI"
        verbose_name_plural = "Auth Profile Suggest CLI"
        db_table = "sa_authprofilesuggestcli"
        app_label = "sa"

    auth_profile = models.ForeignKey(AuthProfile, verbose_name="Auth Profile")
    user = models.CharField(
        "User", max_length=32, blank=True, null=True)
    password = models.CharField(
        "Password", max_length=32, blank=True, null=True)
    super_password = models.CharField(
        "Super Password", max_length=32, blank=True, null=True)

    def __unicode__(self):
        return self.auth_profile.name
