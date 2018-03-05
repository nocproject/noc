# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VRF model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import hashlib
import struct
import operator
from threading import Lock
# Third-party modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
import cachetools
# NOC modules
from noc.main.models import ResourceState
from noc.project.models.project import Project
from noc.peer.models.asn import AS
from noc.lib.validators import check_rd
from noc.core.model.fields import TagsField, DocumentReferenceField
from noc.lib.app.site import site
from noc.main.models.textindex import full_text_search
from noc.core.model.decorator import on_delete_check, on_init
from noc.vc.models.vpnprofile import VPNProfile
from .vrfgroup import VRFGroup

id_lock = Lock()


@full_text_search
@on_init
@on_delete_check(check=[
    ("ip.Address", "vrf"),
    ("ip.AddressRange", "vrf"),
    ("ip.IPPool", "vrf"),
    ("ip.PrefixAccess", "vrf"),
    ("ip.Prefix", "vrf"),
    # ("ip.DynamicIPPoolUsage", "vrf"),
    ("sa.ManagedObject", "vrf"),
    ("sa.ManagedObjectSelector", "filter_vrf"),
    ("vc.VCBindFilter", "vrf"),
])
class VRF(models.Model):
    """
    VRF
    """
    class Meta(object):
        verbose_name = _("VRF")
        verbose_name_plural = _("VRFs")
        db_table = "ip_vrf"
        app_label = "ip"
        ordering = ["name"]

    name = models.CharField(
        _("VRF"),
        unique=True,
        max_length=64,
        help_text=_("Unique VRF Name"))
    profile = DocumentReferenceField(VPNProfile)
    vrf_group = models.ForeignKey(
        VRFGroup, verbose_name=_("VRF Group"))
    rd = models.CharField(
        _("RD"),
        unique=True,
        max_length=21,
        validators=[check_rd],
        help_text=_("Route Distinguisher in form of ASN:N or IP:N"))
    afi_ipv4 = models.BooleanField(
        _("IPv4"),
        default=True,
        help_text=_("Enable IPv4 Address Family"))
    afi_ipv6 = models.BooleanField(
        _("IPv6"),
        default=False,
        help_text=_("Enable IPv6 Address Family"))
    project = models.ForeignKey(
        Project, verbose_name="Project",
        null=True, blank=True, related_name="vrf_set")
    description = models.TextField(
        _("Description"), blank=True, null=True)
    tt = models.IntegerField(
        _("TT"),
        blank=True,
        null=True,
        help_text=_("Ticket #"))
    tags = TagsField(_("Tags"), null=True, blank=True)
    state = models.ForeignKey(
        ResourceState,
        verbose_name=_("State"),
        default=ResourceState.get_default)
    allocated_till = models.DateField(
        _("Allocated till"),
        null=True,
        blank=True,
        help_text=_("VRF temporary allocated till the date"))

    GLOBAL_RD = "0:0"
    IPv4_ROOT = "0.0.0.0/0"
    IPv6_ROOT = "::/0"

    def __unicode__(self):
        if self.rd == self.GLOBAL_RD:
            return u"global"
        else:
            return self.name

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _rd_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_id_cache"),
        lock=lambda _: id_lock)
    def get_by_id(cls, id):
        mo = VRF.objects.filter(id=id)[:1]
        if mo:
            return mo[0]
        else:
            return None

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_rd_cache"),
        lock=lambda _: id_lock)
    def get_by_rd(cls, rd):
        mo = VRF.objects.filter(rd=rd)[:1]
        if mo:
            return mo[0]
        else:
            return None

    def get_absolute_url(self):
        return site.reverse("ip:vrf:change", self.id)

    @classmethod
    def get_global(cls):
        """
        Returns VRF 0:0
        """
        return VRF.objects.get(rd=cls.GLOBAL_RD)

    @classmethod
    def generate_rd(cls, name):
        """
        Generate unique rd for given name
        """
        return "0:%d" % struct.unpack(
            "I", hashlib.sha1(name).digest()[:4])

    def save(self, **kwargs):
        """
        Create root entries for all enabled AFIs
        """
        # Generate unique rd, if empty
        if not self.rd:
            self.rd = self.generate_rd(self.name)
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
        super(VRF, self).save(**kwargs)
        if self.afi_ipv4:
            # Create IPv4 root, if not exists
            Prefix.objects.get_or_create(
                vrf=self, afi="4", prefix=self.IPv4_ROOT,
                defaults={
                    "asn": AS.default_as(),
                    "description": "IPv4 Root",
                    "profile": self.profile.default_prefix_profile
                })
        if self.afi_ipv6:
            # Create IPv6 root, if not exists
            Prefix.objects.get_or_create(
                vrf=self, afi="6", prefix=self.IPv6_ROOT,
                defaults={
                    "asn": AS.default_as(),
                    "description": "IPv6 Root",
                    "profile": self.profile.default_prefix_profile
                })

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
            "card": card
        }
        if self.tags:
            r["tags"] = self.tags
        return r

    def get_search_info(self, user):
        return ("ip.vrf", "history", {"args": [self.id]})


# Avoid circular references
from .prefix import Prefix
