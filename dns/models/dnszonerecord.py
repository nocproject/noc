# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DNSZoneRecord model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from noc.core.translation import ugettext as _
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_init
from noc.core.model.fields import TagsField
from noc.core.datastream.decorator import datastream
from .dnszone import DNSZone


@on_init
@datastream
@six.python_2_unicode_compatible
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
    tags = TagsField(_("Tags"), null=True, blank=True)

    def __str__(self):
        return "%s %s" % (
            self.zone.name,
            " ".join([x for x in (self.name, self.type, self.content) if x]),
        )

    def iter_changed_datastream(self, changed_fields=None):
        for ds, id in self.zone.iter_changed_datastream(changed_fields=changed_fields):
            yield ds, id
