# ----------------------------------------------------------------------
# GroupAccess model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from noc.core.translation import ugettext as _
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.aaa.models.group import Group
from .administrativedomain import AdministrativeDomain


class GroupAccess(NOCModel):
    class Meta:
        verbose_name = _("Group Access")
        verbose_name_plural = _("Group Access")
        db_table = "sa_groupaccess"
        app_label = "sa"
        ordering = ["group"]

    group = models.ForeignKey(Group, verbose_name=_("Group"), on_delete=models.CASCADE)
    administrative_domain = models.ForeignKey(
        AdministrativeDomain, null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        r = [f"group={self.group.name}"]
        if self.administrative_domain:
            r.append(f"domain={self.administrative_domain.name}")
        return f"({', '.join(r)})"
