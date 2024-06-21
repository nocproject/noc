# ----------------------------------------------------------------------
# AuthProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from typing import Optional, List
from threading import Lock

# Third-party modules
import cachetools
from django.contrib.postgres.fields import ArrayField
from django.db import models
from pydantic import BaseModel, validator

# NOC modules
from noc.core.model.base import NOCModel
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.model.decorator import on_save
from noc.core.cache.base import cache
from noc.core.model.decorator import on_delete_check
from noc.core.model.fields import DocumentReferenceField, PydanticField
from noc.core.bi.decorator import bi_sync
from noc.main.models.handler import Handler
from noc.core.translation import ugettext as _

id_lock = Lock()


class MatchRule(BaseModel):
    dynamic_order: int = 0
    labels: List[str] = []
    handler: Optional[str]

    @validator("handler")
    def handler_must_handler(cls, v):  # pylint: disable=no-self-argument
        if not v:
            return v
        h = Handler.objects.filter(id=v).first()
        if not h:
            raise ValueError(f"[{h}] Handler not found")
        elif not h.allow_match_rule:
            raise ValueError(f"[{h}] Handler must be set Allow Match Rule")
        return str(h.id)


class MatchRules(BaseModel):
    __root__: List[Optional[MatchRule]] = []


@Label.model
@on_save
@bi_sync
@on_delete_check(check=[("sa.ManagedObject", "auth_profile")])
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
        ],
    )
    user = models.CharField("User", max_length=32, blank=True, null=True)
    password = models.CharField("Password", max_length=32, blank=True, null=True)
    super_password = models.CharField("Super Password", max_length=32, blank=True, null=True)
    snmp_ro = models.CharField("RO Community", blank=True, null=True, max_length=64)
    snmp_rw = models.CharField("RW Community", blank=True, null=True, max_length=64)
    # Allow to suggest credential by credential rules
    enable_suggest_by_rule: bool = models.BooleanField(default=True)
    # Auth Profile credential preferred on local
    preferred_profile_credential = models.BooleanField(default=True)
    # Integration with external NRI systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem, null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.BigIntegerField(unique=True)
    #
    # Dynamic Profile Classification
    dynamic_classification_policy = models.CharField(
        _("Dynamic Classification Policy"),
        max_length=1,
        choices=[("D", "Disable"), ("R", "By Rule"), ("U", "By Username/SNMP RO")],
        default="R",
    )
    match_rules = PydanticField(
        _("Match Dynamic Rules"),
        schema=MatchRules,
        blank=True,
        null=True,
        default=list,
        # ? Internal validation not worked with JSON Field
        # validators=[match_rules_validate],
    )

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
        return AuthProfile.objects.filter(id=aid).first()

    def on_save(self):
        from .managedobject import CREDENTIAL_CACHE_VERSION

        cache.delete_many(
            ["cred-%s" % x for x in self.managedobject_set.values_list("id", flat=True)],
            version=CREDENTIAL_CACHE_VERSION,
        )

    @property
    def enable_suggest(self) -> bool:
        return self.enable_suggest_by_rule

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_authprofile")
