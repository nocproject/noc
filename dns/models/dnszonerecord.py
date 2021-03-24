# ---------------------------------------------------------------------
# DNSZoneRecord model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models
from django.contrib.postgres.fields import ArrayField

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_init
from noc.core.datastream.decorator import datastream
from noc.core.translation import ugettext as _
from noc.main.models.label import Label
from .dnszone import DNSZone


@Label.model
@on_init
@datastream
class DNSZoneRecord(NOCModel):
    """
    Zone RRs
    """

    class Meta(object):
        verbose_name = _("DNS Zone Record")
        verbose_name_plural = _("DNS Zone Records")
        db_table = "dns_dnszonerecord"
        app_label = "dns"

    zone = models.ForeignKey(DNSZone, verbose_name="Zone", on_delete=models.CASCADE)
    name = models.CharField(_("Name"), max_length=64, blank=True, null=True)
    ttl = models.IntegerField(_("TTL"), null=True, blank=True)
    type = models.CharField(_("Type"), max_length=16)
    priority = models.IntegerField(_("Priority"), null=True, blank=True)
    content = models.CharField(_("Content"), max_length=65536)
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )

    def __str__(self):
        return "%s %s" % (
            self.zone.name,
            " ".join([x for x in (self.name, self.type, self.content) if x]),
        )

    def iter_changed_datastream(self, changed_fields=None):
        for ds, id in self.zone.iter_changed_datastream(changed_fields=changed_fields):
            yield ds, id

    @classmethod
    def can_set_label(cls, label):
        if label.enable_dnszonerecord:
            return True
        return False
