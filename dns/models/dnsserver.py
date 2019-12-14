# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DNSServer model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules modules
import six
from noc.core.translation import ugettext as _
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_init
from noc.config import config
from noc.core.model.fields import INETField
from noc.core.datastream.decorator import datastream


@on_init
@datastream
@six.python_2_unicode_compatible
class DNSServer(NOCModel):
    """
    DNS Server is an database object representing real DNS server.

    :param name: Unique DNS server name (usually, FQDN)
    :param ip: Server's IP address
    :param description: Optional description
    """

    class Meta(object):
        verbose_name = _("DNS Server")
        verbose_name_plural = _("DNS Servers")
        db_table = "dns_dnsserver"
        app_label = "dns"

    name = models.CharField(_("Name"), max_length=64, unique=True)
    ip = INETField(_("IP"), null=True, blank=True)
    description = models.CharField(_("Description"), max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name

    def iter_changed_datastream(self, changed_fields=None):
        if not config.datastream.enable_dnszone:
            return
        for zp in self.masters.all():
            for ds, id in zp.iter_changed_datastream(changed_fields=changed_fields):
                yield ds, id
        for zp in self.slaves.all():
            for ds, id in zp.iter_changed_datastream(changed_fields=changed_fields):
                yield ds, id
