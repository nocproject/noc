# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VC model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import re
import operator
from threading import Lock

# Third-party modules
import six
from django.db import models
from mongoengine.queryset import Q as MEQ
import cachetools

# NOC modules
from noc.core.model.base import NOCModel
from noc.main.models.style import Style
from noc.main.models.resourcestate import ResourceState
from noc.project.models.project import Project
from noc.core.model.fields import TagsField
from noc.lib.app.site import site
from noc.main.models.textindex import full_text_search
from noc.core.cache.decorator import cachedmethod
from noc.core.model.decorator import on_delete_check
from .error import InvalidLabelException, MissedLabelException
from .vcdomain import VCDomain

# Regular expressions
rx_vc_underline = re.compile(r"\s+")
rx_vc_empty = re.compile(r"[^a-zA-Z0-9\-_]+")

id_lock = Lock()


@on_delete_check(check=[("ip.Prefix", "vc")])
@full_text_search
@six.python_2_unicode_compatible
class VC(NOCModel):
    """
    Virtual circuit
    """

    class Meta(object):
        verbose_name = "VC"
        verbose_name_plural = "VCs"
        unique_together = [("vc_domain", "l1", "l2"), ("vc_domain", "name")]
        db_table = "vc_vc"
        app_label = "vc"
        ordering = ["vc_domain", "l1", "l2"]

    vc_domain = models.ForeignKey(VCDomain, verbose_name="VC Domain", on_delete=models.CASCADE)
    name = models.CharField("Name", max_length=64)
    state = models.ForeignKey(
        ResourceState,
        verbose_name="State",
        default=ResourceState.get_default,
        on_delete=models.CASCADE,
    )
    project = models.ForeignKey(
        Project,
        verbose_name="Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vc_set",
    )
    l1 = models.IntegerField("Label 1")
    l2 = models.IntegerField("Label 2", default=0)
    description = models.CharField("Description", max_length=256, null=True, blank=True)
    style = models.ForeignKey(
        Style, verbose_name="Style", blank=True, null=True, on_delete=models.CASCADE
    )
    tags = TagsField("Tags", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        s = "%s %d" % (self.vc_domain, self.l1)
        if self.l2:
            s += "/%d" % self.l2
        s += ": %s" % self.name
        return s

    @classmethod
    @cachedmethod(operator.attrgetter("_id_cache"), key="vc-id-%s", lock=lambda _: id_lock)
    def get_by_id(cls, id):
        mo = VC.objects.filter(id=id)[:1]
        if mo:
            return mo[0]
        else:
            return None

    def get_absolute_url(self):
        return site.reverse("vc:vc:change", self.id)

    @classmethod
    def convert_name(cls, name):
        name = rx_vc_underline.sub("_", name)
        name = rx_vc_empty.sub("", name)
        return name

    def save(self, *args, **kwargs):
        """
        Enforce additional checks
        """
        if self.l1 < self.vc_domain.type.label1_min or self.l1 > self.vc_domain.type.label1_max:
            raise InvalidLabelException("Invalid value for L1")
        if self.vc_domain.type.min_labels > 1 and self.l2 is None:
            raise MissedLabelException("L2 required")
        if self.vc_domain.type.min_labels > 1 and not (
            self.vc_domain.type.label2_min <= self.l2 <= self.vc_domain.type.label2_max
        ):
            raise InvalidLabelException("Invalid value for L2")
        # Format name
        if self.name:
            self.name = self.convert_name(self.name)
        else:
            self.name = "VC_%04d" % self.l1
        super(VC, self).save(*args, **kwargs)

    def get_index(self):
        """
        Full-text search
        """
        content = [self.name, str(self.l1)]
        card = "VC %s. Tag %s" % (self.name, self.l1)
        if self.description:
            content += [self.description]
            card += " (%s)" % self.description
        if self.l2:
            content += [str(self.l2)]
        r = {
            "id": "vc.vc:%s" % self.id,
            "title": self.name,
            "content": "\n".join(content),
            "card": card,
        }
        if self.tags:
            r["tags"] = self.tags
        return r

    @classmethod
    def get_search_result_url(cls, obj_id):
        return "/api/card/view/vlan/%s/" % obj_id

    def get_bridge_subinterfaces(self):
        """
        Returns a list of SubInterface instances belonging to VC
        """
        from noc.inv.models.interface import Interface
        from noc.inv.models.subinterface import SubInterface

        r = []
        si_q = MEQ(untagged_vlan=self.l1) | MEQ(tagged_vlans=self.l1)
        # VC Domain's objects
        objects = set(self.vc_domain.managedobject_set.values_list("id", flat=True))
        for si in SubInterface.objects.filter(
            managed_object__in=objects, enabled_afi="BRIDGE"
        ).filter(si_q):
            if si.interface.vc_domain is None or si.interface.vc_domain.id == self.vc_domain.id:
                r += [si]
        # Explicit interfaces
        for i in Interface.objects.filter(vc_domain=self.vc_domain.id):
            for si in SubInterface.objects.filter(interface=i.id, enabled_afi="BRIDGE").filter(
                si_q
            ):
                r += [si]
        return r
