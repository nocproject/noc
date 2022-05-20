# ---------------------------------------------------------------------
# VRFGroup model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db.models.base import Model
from django.db import models
from django.contrib.postgres.fields import ArrayField

# NOC modules
from noc.core.translation import ugettext as _
from noc.core.model.decorator import on_delete_check
from noc.core.comp import smart_text
from noc.main.models.label import Label


@Label.model
@on_delete_check(check=[("ip.VRF", "vrf_group")])
class VRFGroup(Model):
    """
    Group of VRFs with common properties
    """

    class Meta(object):
        verbose_name = _("VRF Group")
        verbose_name_plural = _("VRF Groups")
        db_table = "ip_vrfgroup"
        app_label = "ip"
        ordering = ["name"]

    name = models.CharField(
        _("VRF Group"), unique=True, max_length=64, help_text=_("Unique VRF Group name")
    )
    address_constraint = models.CharField(
        _("Address Constraint"),
        max_length=1,
        choices=[
            ("V", _("Addresses are unique per VRF")),
            ("G", _("Addresses are unique per VRF Group")),
        ],
        default="V",
    )
    description = models.TextField(_("Description"), blank=True, null=True)
    # Labels
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )

    def __str__(self):
        return smart_text(self.name)

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_vrfgroup")
