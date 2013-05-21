# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VC model
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## Django modules
from django.db import models
from django.db.models import Q
## NOC modules
from error import InvalidLabelException, MissedLabelException
from vcdomain import VCDomain
from noc.main.models import ResourceState, Style
from noc.project.models.project import Project
from noc.lib.fields import TagsField
from noc.lib.app.site import site
from noc.lib.validators import is_int
from noc.lib.search import SearchResult

## Regular expressions
rx_vc_underline = re.compile("\s+")
rx_vc_empty = re.compile(r"[^a-zA-Z0-9\-_]+")


class VC(models.Model):
    """
    Virtual circuit
    """
    class Meta:
        verbose_name = "VC"
        verbose_name_plural = "VCs"
        unique_together = [("vc_domain", "l1", "l2"), ("vc_domain", "name")]
        db_table = "vc_vc"
        app_label = "vc"
        ordering = ["vc_domain", "l1", "l2"]

    vc_domain = models.ForeignKey(VCDomain, verbose_name="VC Domain")
    name = models.CharField("Name", max_length=64)
    state = models.ForeignKey(ResourceState, verbose_name="State",
        default=ResourceState.get_default)
    project = models.ForeignKey(
        Project, verbose_name="Project",
        null=True, blank=True, related_name="vc_set")
    l1 = models.IntegerField("Label 1")
    l2 = models.IntegerField("Label 2", default=0)
    description = models.CharField("Description", max_length=256, null=True,
                                   blank=True)
    style = models.ForeignKey(Style, verbose_name="Style", blank=True,
                              null=True)
    tags = TagsField("Tags", null=True, blank=True)

    def __unicode__(self):
        s = u"%s %d" % (self.vc_domain, self.l1)
        if self.l2:
            s += u"/%d" % self.l2
        s += u": %s" % self.name
        return s

    def get_absolute_url(self):
        return site.reverse("vc:vc:change", self.id)

    @classmethod
    def convert_name(cls, name):
        name = rx_vc_underline.sub("_", name)
        name = rx_vc_empty.sub("", name)
        return name

    def save(self):
        """
        Enforce additional checks
        """
        if (self.l1 < self.vc_domain.type.label1_min or
            self.l1 > self.vc_domain.type.label1_max):
            raise InvalidLabelException("Invalid value for L1")
        if self.vc_domain.type.min_labels > 1 and not self.l2:
            raise MissedLabelException("L2 required")
        if (self.vc_domain.type.min_labels > 1 and
            not (self.vc_domain.type.label2_min <= self.l2 <= self.vc_domain.type.label2_max)):
            raise InvalidLabelException("Invalid value for L2")
        # Format name
        if self.name:
            self.name = self.convert_name(self.name)
        else:
            self.name = "VC_%04d" % self.l1
        super(VC, self).save()

    @classmethod
    def search(cls, user, search, limit):
        """
        Search engine
        """
        if user.has_perm("vc.change_vc"):
            if is_int(search):
                tag = int(search)
                for r in VC.objects.filter(Q(l1=tag) | Q(l2=tag))[:limit]:
                    yield SearchResult(
                        url=("vc:vc:change", r.id),
                        title="VC: %s" % unicode(r),
                        text=r.description,
                        relevancy=1.0)
