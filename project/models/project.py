# ---------------------------------------------------------------------
# Project models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional

# Third-party modules
from django.db import models
import cachetools

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check
from noc.core.model.fields import DocumentReferenceField
from noc.main.models.glyph import Glyph
from noc.main.models.remotesystem import RemoteSystem
from noc.core.bi.decorator import bi_sync
from noc.core.topology.types import ShapeOverlayPosition, ShapeOverlayForm

id_lock = Lock()


@bi_sync
@on_delete_check(
    check=[
        ("crm.Subscriber", "project"),
        ("crm.Supplier", "project"),
        ("dns.DNSZone", "project"),
        ("inv.Interface", "project"),
        ("inv.SubInterface", "project"),
        ("ip.Address", "project"),
        ("ip.Prefix", "project"),
        ("ip.VRF", "project"),
        ("peer.AS", "project"),
        ("peer.ASSet", "project"),
        ("peer.Peer", "project"),
        ("phone.PhoneNumber", "project"),
        ("phone.PhoneRange", "project"),
        ("sa.ManagedObject", "project"),
        ("vc.VPN", "project"),
        ("vc.VLAN", "project"),
    ]
)
class Project(NOCModel):
    """
    Projects are used to track investment projects expenses and profits
    """

    class Meta(object):
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        app_label = "project"
        db_table = "project_project"

    code = models.CharField("Code", max_length=256, unique=True)
    name = models.CharField("Name", max_length=256)
    description = models.TextField("Description", null=True, blank=True)
    shape_overlay_glyph = DocumentReferenceField(Glyph, null=True, blank=True)
    shape_overlay_position = models.CharField(
        "S.O. Position",
        max_length=2,
        choices=[(x.value, x.value) for x in ShapeOverlayPosition],
        null=True,
        blank=True,
    )
    shape_overlay_form = models.CharField(
        "S.O. Form",
        max_length=1,
        choices=[(x.value, x.value) for x in ShapeOverlayForm],
        null=True,
        blank=True,
    )
    # Integration with external NRI systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem, null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.BigIntegerField(unique=True)

    _id_cache = cachetools.TTLCache(100, ttl=60)

    def __str__(self):
        return self.code

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda x: id_lock)
    def get_by_id(cls, id: int) -> Optional["Project"]:
        p = Project.objects.filter(id=id)[:1]
        if p:
            return p[0]
        return None
