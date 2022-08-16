# ----------------------------------------------------------------------
# AuthProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from typing import Optional
from threading import Lock

# Third-party modules
from django.contrib.postgres.fields import ArrayField
from django.db import models
import cachetools

# NOC modules
from noc.core.model.base import NOCModel
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
        ("sa.ManagedObject", "auth_profile"),
        ("sa.ManagedObjectProfile", "cpe_auth_profile"),
    ]
)
class AuthProfile(NOCModel):
    class Meta(object):
        verbose_name = "Auth Profile"
        verbose_name_plural = "Auth Profiles"
        db_table = "sa_authprofile"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", null=True, blank=True)
    type = models.CharField(
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
    user = models.CharField("User", max_length=32, blank=True, null=True)
    password = models.CharField("Password", max_length=32, blank=True, null=True)
    super_password = models.CharField("Super Password", max_length=32, blank=True, null=True)
    snmp_ro = models.CharField("RO Community", blank=True, null=True, max_length=64)
    snmp_rw = models.CharField("RW Community", blank=True, null=True, max_length=64)
    # Integration with external NRI systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem, null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.BigIntegerField(unique=True)

    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, aid) -> Optional["AuthProfile"]:
        return AuthProfile.objects.get(id=aid).first()

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

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_authprofile")
