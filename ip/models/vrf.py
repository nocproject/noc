# ---------------------------------------------------------------------
# VRF model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional

# Third-party modules
from noc.core.translation import ugettext as _
from django.db import models
from django.contrib.postgres.fields import ArrayField
import cachetools

# NOC modules
from noc.config import config
from noc.core.model.base import NOCModel
from noc.project.models.project import Project
from noc.core.validators import check_rd
from noc.core.model.fields import DocumentReferenceField
from noc.main.models.textindex import full_text_search
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.core.model.decorator import on_delete_check, on_init
from noc.vc.models.vpnprofile import VPNProfile
from noc.wf.models.state import State
from .vrfgroup import VRFGroup
from noc.core.wf.decorator import workflow
from noc.core.vpn import get_vpn_id
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change


id_lock = Lock()


@Label.match_labels("ipvrf", allowed_op={"="})
@Label.model
@full_text_search
@on_init
@workflow
@bi_sync
@change
@on_delete_check(
    check=[
        ("ip.Address", "vrf"),
        ("ip.AddressRange", "vrf"),
        ("ip.PrefixAccess", "vrf"),
        ("ip.Prefix", "vrf"),
        # ("ip.DynamicIPPoolUsage", "vrf"),
        ("sa.ManagedObject", "vrf"),
    ],
    clean_lazy_labels="ipvrf",
)
class VRF(NOCModel):
    """
    VRF
    """

    class Meta(object):
        verbose_name = _("VRF")
        verbose_name_plural = _("VRFs")
        db_table = "ip_vrf"
        app_label = "ip"
        ordering = ["name"]

    name = models.CharField(_("VRF"), unique=True, max_length=64, help_text=_("Unique VRF Name"))
    profile: VPNProfile = DocumentReferenceField(VPNProfile)
    vrf_group = models.ForeignKey(
        VRFGroup, verbose_name=_("VRF Group"), null=True, blank=True, on_delete=models.CASCADE
    )
    rd = models.CharField(
        _("RD"),
        max_length=21,
        validators=[check_rd],
        null=True,
        blank=True,
        help_text=_("Route Distinguisher in form of ASN:N or IP:N"),
    )
    # RFC2685-compatible VPN id
    vpn_id = models.CharField(
        _("VPN ID"), max_length=15, help_text=_("RFC2685 compatible VPN ID"), unique=True
    )
    afi_ipv4 = models.BooleanField(
        _("IPv4"), default=True, help_text=_("Enable IPv4 Address Family")
    )
    afi_ipv6 = models.BooleanField(
        _("IPv6"), default=False, help_text=_("Enable IPv6 Address Family")
    )
    project = models.ForeignKey(
        Project,
        verbose_name="Project",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="vrf_set",
    )
    description = models.TextField(_("Description"), blank=True, null=True)
    tt = models.IntegerField(_("TT"), blank=True, null=True, help_text=_("Ticket #"))
    # Labels
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )
    state = DocumentReferenceField(State, null=True, blank=True)
    allocated_till = models.DateField(
        _("Allocated till"),
        null=True,
        blank=True,
        help_text=_("VRF temporary allocated till the date"),
    )
    source = models.CharField(
        "Source",
        max_length=1,
        choices=[("M", "Manual"), ("i", "Interface"), ("m", "MPLS"), ("c", "ConfDB")],
        null=False,
        blank=False,
        default="M",
    )
    # Last state change
    state_changed = models.DateTimeField("State Changed", null=True, blank=True)
    # Timestamp expired
    expired = models.DateTimeField("Expired", null=True, blank=True)
    # Timestamp of last seen
    last_seen = models.DateTimeField("Last Seen", null=True, blank=True)
    # Timestamp of first discovery
    first_discovered = models.DateTimeField("First Discovered", null=True, blank=True)
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem, null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.BigIntegerField(unique=True)

    GLOBAL_RD = "0:0"
    IPv4_ROOT = "0.0.0.0/0"
    IPv6_ROOT = "::/0"

    def __str__(self):
        if self.rd == self.GLOBAL_RD:
            return "global"
        else:
            return self.name

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _vpn_id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["VRF"]:
        vrf = VRF.objects.filter(id=id)[:1]
        if vrf:
            return vrf[0]
        return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_vpn_id_cache"), lock=lambda _: id_lock)
    def get_by_vpn_id(cls, vpn_id):
        vrf = VRF.objects.filter(vpn_id=vpn_id)[:1]
        if vrf:
            return vrf[0]
        return None

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_vrf:
            yield "vrf", self.id

    @classmethod
    def get_global(cls):
        """
        Returns VRF 0:0
        """
        return VRF.get_by_vpn_id(cls.GLOBAL_RD)

    def save(self, *args, **kwargs):
        """
        Create root entries for all enabled AFIs
        """
        from .prefix import Prefix

        # Generate unique rd, if empty
        if not self.vpn_id:
            vdata = {"type": "VRF", "name": self.name, "rd": self.rd}
            self.vpn_id = get_vpn_id(vdata)
        if self.initial_data["id"]:
            # Delete empty ipv4 root if AFI changed
            if self.initial_data.get("afi_ipv4") != self.afi_ipv4 and not self.afi_ipv4:
                root = Prefix.objects.filter(vrf=self, afi="4", prefix=self.IPv4_ROOT)[:1]
                if root:
                    root = root[0]
                    if root.is_empty():
                        root.disable_delete_protection()
                        root.delete()
                    else:
                        # Cannot change until emptied
                        self.afi_ipv4 = True
            # Delete empty ipv4 root if AFI changed
            if self.initial_data.get("afi_ipv6") != self.afi_ipv6 and not self.afi_ipv6:
                root = Prefix.objects.filter(vrf=self, afi="6", prefix=self.IPv6_ROOT)[:1]
                if root:
                    root = root[0]
                    if root.is_empty():
                        root.disable_delete_protection()
                        root.delete()
                    else:
                        # Cannot change until emptied
                        self.afi_ipv6 = True
        # Save VRF
        super().save(*args, **kwargs)
        if self.afi_ipv4:
            # Create IPv4 root, if not exists
            Prefix.objects.get_or_create(
                vrf=self,
                afi="4",
                prefix=self.IPv4_ROOT,
                defaults={
                    "description": "IPv4 Root",
                    "profile": self.profile.default_prefix_profile,
                },
            )
        if self.afi_ipv6:
            # Create IPv6 root, if not exists
            Prefix.objects.get_or_create(
                vrf=self,
                afi="6",
                prefix=self.IPv6_ROOT,
                defaults={
                    "description": "IPv6 Root",
                    "profile": self.profile.default_prefix_profile,
                },
            )

    def get_index(self):
        """
        Full-text search
        """
        content = [self.name, str(self.rd)]
        card = "VRF %s. RD %s" % (self.name, self.rd)
        if self.description:
            content += [self.description]
            card += " (%s)" % self.description
        r = {
            "id": "ip.vrf:%s" % self.id,
            "title": self.name,
            "content": "\n".join(content),
            "card": card,
        }
        if self.labels:
            r["tags"] = self.labels
        return r

    @classmethod
    def get_search_result_url(cls, obj_id):
        return "/api/card/view/vrf/%s/" % obj_id

    def delete(self, *args, **kwargs):
        # Cleanup prefixes
        self.afi_ipv4 = False
        self.afi_ipv6 = False
        self.save()
        # Delete
        super().delete(*args, **kwargs)

    @property
    def is_global(self):
        return self.vpn_id == self.GLOBAL_RD

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_vrf")

    @classmethod
    def iter_lazy_labels(cls, vrf: "VRF"):
        yield f"noc::ipvrf::{vrf.name}::="
