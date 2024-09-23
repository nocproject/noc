# ----------------------------------------------------------------------
# AdministrativeDomain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
from typing import Optional, TYPE_CHECKING

# Third-party modules
from noc.core.translation import ugettext as _
from django.contrib.postgres.fields import ArrayField
from django.db import models
import cachetools

# NOC modules
from noc.config import config
from noc.core.model.base import NOCModel
from noc.main.models.pool import Pool
from noc.main.models.template import Template
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.model.fields import DocumentReferenceField
from noc.core.model.decorator import on_delete_check, on_init, tree
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change

id_lock = Lock()
_path_cache = cachetools.TTLCache(maxsize=1000, ttl=60)


@tree(field="parent")
@Label.match_labels("adm_domain", allowed_op={"=", "<"})
@Label.model
@on_init
@bi_sync
@change(audit=True)
@on_delete_check(
    check=[
        ("cm.ObjectNotify", "administrative_domain"),
        # ("fm.EscalationItem", "administrative_domain"),
        ("sa.GroupAccess", "administrative_domain"),
        ("sa.ManagedObject", "administrative_domain"),
        ("sa.UserAccess", "administrative_domain"),
        ("sa.AdministrativeDomain", "parent"),
        ("maintenance.Maintenance", "administrative_domain"),
        ("phone.PhoneNumber", "administrative_domain"),
        ("phone.PhoneRange", "administrative_domain"),
    ],
    clean_lazy_labels="adm_domain",
)
class AdministrativeDomain(NOCModel):
    """
    Administrative Domain
    """

    class Meta(object):
        verbose_name = _("Administrative Domain")
        verbose_name_plural = _("Administrative Domains")
        db_table = "sa_administrativedomain"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=255, unique=True)
    parent = models.ForeignKey(
        "self", verbose_name="Parent", null=True, blank=True, on_delete=models.CASCADE
    )
    description = models.TextField(_("Description"), null=True, blank=True)
    default_pool = DocumentReferenceField(Pool, null=True, blank=True)
    # Biosegmentation settings
    bioseg_floating_name_template = models.ForeignKey(
        Template, null=True, blank=True, on_delete=models.CASCADE
    )
    bioseg_floating_parent_segment = DocumentReferenceField(
        "inv.NetworkSegment", null=True, blank=True
    )
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

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _nested_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["AdministrativeDomain"]:
        ad = AdministrativeDomain.objects.filter(id=id)[:1]
        if ad:
            return ad[0]
        return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["AdministrativeDomain"]:
        ad = AdministrativeDomain.objects.filter(bi_id=bi_id)[:1]
        if ad:
            return ad[0]
        return None

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_administrativedomain:
            yield "administrativedomain", self.id

    @cachetools.cached(_path_cache, key=lambda s: s.id, lock=id_lock)
    def get_path(self):
        """
        Returns list of parent administrative domain ids
        :return:
        """
        if self.parent:
            return self.parent.get_path() + [self.id]
        return [self.id]

    def get_default_pool(self):
        if self.default_pool:
            return self.default_pool
        if self.parent:
            return self.parent.get_default_pool()
        return None

    def get_nested(self):
        """
        Returns list of nested administrative domains
        :return:
        """
        r = [self]
        for d in AdministrativeDomain.objects.filter(parent=self):
            r += d.get_nested()
        return r

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_nested_cache"), lock=lambda _: id_lock)
    def get_nested_ids(cls, administrative_domain):
        from django.db import connection

        if hasattr(administrative_domain, "id"):
            administrative_domain = administrative_domain.id
        cursor = connection.cursor()
        cursor.execute(
            """
            WITH RECURSIVE r AS (
                 SELECT id, parent_id
                 FROM sa_administrativedomain
                 WHERE id = %d
                 UNION
                 SELECT ad.id, ad.parent_id
                 FROM sa_administrativedomain ad JOIN r ON ad.parent_id = r.id
            )
            SELECT id FROM r
        """
            % administrative_domain
        )
        return [r[0] for r in cursor]

    @property
    def has_children(self):
        return True if AdministrativeDomain.objects.filter(parent=self.id) else False

    def get_bioseg_floating_name(self, object) -> Optional[str]:
        if self.bioseg_floating_name_template:
            return self.bioseg_floating_name_template.render_body(object=object)
        if self.parent:
            return self.parent.get_bioseg_floating_name(object)
        return None

    def get_bioseg_floating_parent_segment(self) -> Optional["NetworkSegment"]:
        if self.bioseg_floating_parent_segment:
            return self.bioseg_floating_parent_segment
        if self.parent:
            return self.parent.get_bioseg_floating_parent_segment()
        return None

    @property
    def level(self) -> int:
        """
        Return level
        :return:
        """
        if not self.parent:
            return 0
        return len(self.get_path()) - 1  # self

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_administrativedomain")

    @classmethod
    def iter_lazy_labels(cls, adm_domain: "AdministrativeDomain"):
        for ad in AdministrativeDomain.objects.filter(id__in=adm_domain.get_path()):
            if ad == adm_domain:
                yield f"noc::adm_domain::{ad.name}::="
            yield f"noc::adm_domain::{ad.name}::<"


if TYPE_CHECKING:
    from noc.inv.models.networksegment import NetworkSegment  # noqa
