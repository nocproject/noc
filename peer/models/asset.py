# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ASSet model
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## NOC module
from noc.project.models.project import Project
from noc.lib.fields import TagsField
from noc.lib.app.site import site
from noc.lib.rpsl import rpsl_format


class ASSet(models.Model):
    class Meta:
        verbose_name = "ASSet"
        verbose_name_plural = "ASSets"
        db_table = "peer_asset"
        app_label = "peer"

    name = models.CharField("Name", max_length=32, unique=True)
    project = models.ForeignKey(
        Project, verbose_name="Project",
        null=True, blank=True, related_name="as_set")
    description = models.CharField("Description", max_length=64)
    members = models.TextField("Members", null=True, blank=True)
    rpsl_header = models.TextField("RPSL Header", null=True, blank=True)
    rpsl_footer = models.TextField("RPSL Footer", null=True, blank=True)
    tags = TagsField("Tags", null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return site.reverse("peer:asset:change", self.id)

    @property
    def member_list(self):
        if self.members is None:
            return []
        m = sorted(self.members.replace(",", " ")
            .replace("\n", " ")
            .replace("\r", " ").upper().split())
        return m

    @property
    def rpsl(self):
        sep = "remark: %s" % ("-" * 72)
        s = []
        if self.rpsl_header:
            s += self.rpsl_header.split("\n")
        s += ["as-set: %s" % self.name]
        for m in self.member_list:
            s += ["members: %s" % m]
        if self.rpsl_footer:
            s += [sep]
            s += self.rpsl_footer.split("\n")
        return rpsl_format("\n".join(s))
