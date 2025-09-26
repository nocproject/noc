# ---------------------------------------------------------------------
# ASSet model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models
from django.contrib.postgres.fields import ArrayField

# NOC module
from noc.core.model.base import NOCModel
from noc.project.models.project import Project
from noc.main.models.label import Label
from noc.core.rpsl import rpsl_format
from noc.core.gridvcs.manager import GridVCSField
from noc.core.model.decorator import on_save


@Label.model
@on_save
class ASSet(NOCModel):
    class Meta(object):
        verbose_name = "ASSet"
        verbose_name_plural = "ASSets"
        db_table = "peer_asset"
        app_label = "peer"

    name = models.CharField("Name", max_length=32, unique=True)
    project = models.ForeignKey(
        Project,
        verbose_name="Project",
        null=True,
        blank=True,
        related_name="asset_set",
        on_delete=models.CASCADE,
    )
    description = models.CharField("Description", max_length=64)
    members = models.TextField("Members", null=True, blank=True)
    rpsl_header = models.TextField("RPSL Header", null=True, blank=True)
    rpsl_footer = models.TextField("RPSL Footer", null=True, blank=True)
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )
    rpsl = GridVCSField("rpsl_asset")

    def __str__(self):
        return self.name

    @property
    def member_list(self):
        if self.members is None:
            return []
        return sorted(
            self.members.replace(",", " ").replace("\n", " ").replace("\r", " ").upper().split()
        )

    def get_rpsl(self):
        sep = "remark: %s" % ("-" * 72)
        s = []
        s += ["as-set: %s" % self.name]
        if self.rpsl_header:
            s += self.rpsl_header.split("\n")
        for m in self.member_list:
            s += ["members: %s" % m]
        if self.rpsl_footer:
            s += [sep]
            s += self.rpsl_footer.split("\n")
        return rpsl_format("\n".join(s))

    def touch_rpsl(self):
        c_rpsl = self.rpsl.read()
        n_rpsl = self.get_rpsl()
        if c_rpsl == n_rpsl:
            return  # Not changed
        self.rpsl.write(n_rpsl)

    def on_save(self):
        self.touch_rpsl()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_assetpeer")
