# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DNSZoneRecord model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
# NOC modules
from dnszone import DNSZone
from noc.core.model.fields import TagsField
from noc.core.datastream.decorator import datastream


@datastream
class DNSZoneRecord(models.Model):
    """
    Zone RRs
    """
    class Meta:
        verbose_name = _("DNS Zone Record")
        verbose_name_plural = _("DNS Zone Records")
        db_table = "dns_dnszonerecord"
        app_label = "dns"

    zone = models.ForeignKey(DNSZone, verbose_name="Zone")
    name = models.CharField(_("Name"), max_length=64, blank=True, null=True)
    ttl = models.IntegerField(_("TTL"), null=True, blank=True)
    type = models.CharField(_("Type"), max_length=16)
    priority = models.IntegerField(_("Priority"), null=True, blank=True)
    content = models.CharField(_("Content"), max_length=256)
    tags = TagsField(_("Tags"), null=True, blank=True)

    def __unicode__(self):
        return u"%s %s" % (self.zone.name,
            " ".join([x for x in (self.name, self.type, self.content) if x ]))

    def iter_changed_datastream(self):
        for ds, id in self.zone.iter_changed_datastream():
            yield ds, id
