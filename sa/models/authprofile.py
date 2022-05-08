# ----------------------------------------------------------------------
# AuthProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock

# Third-party modules
from django.db.models.base import Model
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CharField,
    TextField,
    ForeignKey,
    BigIntegerField,
    CASCADE,
)
import cachetools

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.model.decorator import on_save
from noc.core.cache.base import cache
from noc.core.model.decorator import on_delete_check
from noc.core.model.fields import DocumentReferenceField
from noc.core.bi.decorator import bi_sync

id_lock = Lock()


@Label.model
@on_save
@bi_sync
@on_delete_check(
    check=[
        ("sa.AuthProfileSuggestSNMP", "auth_profile"),
        ("sa.AuthProfileSuggestCLI", "auth_profile"),
        ("sa.ManagedObject", "auth_profile"),
        ("sa.ManagedObjectProfile", "cpe_auth_profile"),
    ]
)
class AuthProfile(Model):
    class Meta(object):
        verbose_name = "Auth Profile"
        verbose_name_plural = "Auth Profiles"
        db_table = "sa_authprofile"
        app_label = "sa"
        ordering = ["name"]

    name = CharField("Name", max_length=64, unique=True)
    description = TextField("Description", null=True, blank=True)
    type = CharField(
        "Name",
        max_length=1,
        choices=[
            ("G", "Local Group"),
            ("R", "RADIUS"),
            ("T", "TACACS+"),
            ("L", "LDAP"),
            ("S", "Suggest"),
        ],
    )
    user = CharField("User", max_length=32, blank=True, null=True)
    password = CharField("Password", max_length=32, blank=True, null=True)
    super_password = CharField("Super Password", max_length=32, blank=True, null=True)
    snmp_ro = CharField("RO Community", blank=True, null=True, max_length=64)
    snmp_rw = CharField("RW Community", blank=True, null=True, max_length=64)
    # Integration with external NRI systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem, null=True, blank=True)
    # Object id in remote system
    remote_id = CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = BigIntegerField(unique=True)

    labels = ArrayField(CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(CharField(max_length=250), blank=True, null=True, default=list)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        try:
            return AuthProfile.objects.get(id=id)
        except AuthProfile.DoesNotExist:
            return None

    def on_save(self):
        from .managedobject import CREDENTIAL_CACHE_VERSION

        if not self.enable_suggest:
            cache.delete_many(
                ["cred-%s" % x for x in self.managedobject_set.values_list("id", flat=True)],
                version=CREDENTIAL_CACHE_VERSION,
            )

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

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_authprofile")


class AuthProfileSuggestSNMP(Model):
    class Meta(object):
        verbose_name = "Auth Profile Suggest SNMP"
        verbose_name_plural = "Auth Profile Suggest SNMP"
        db_table = "sa_authprofilesuggestsnmp"
        app_label = "sa"

    auth_profile = ForeignKey(AuthProfile, verbose_name="Auth Profile", on_delete=CASCADE)
    snmp_ro = CharField("RO Community", blank=True, null=True, max_length=64)
    snmp_rw = CharField("RW Community", blank=True, null=True, max_length=64)

    def __str__(self):
        return self.auth_profile.name


class AuthProfileSuggestCLI(Model):
    class Meta(object):
        verbose_name = "Auth Profile Suggest CLI"
        verbose_name_plural = "Auth Profile Suggest CLI"
        db_table = "sa_authprofilesuggestcli"
        app_label = "sa"

    auth_profile = ForeignKey(AuthProfile, verbose_name="Auth Profile", on_delete=CASCADE)
    user = CharField("User", max_length=32, blank=True, null=True)
    password = CharField("Password", max_length=32, blank=True, null=True)
    super_password = CharField("Super Password", max_length=32, blank=True, null=True)

    def __str__(self):
        return self.auth_profile.name
