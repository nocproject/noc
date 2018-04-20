# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DNSServer model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
# NOC modules
from noc.core.model.fields import INETField, DocumentReferenceField
=======
##----------------------------------------------------------------------
## DNSServer model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from noc.lib.fields import INETField, DocumentReferenceField
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.main.models.sync import Sync


class DNSServer(models.Model):
    """
    DNS Server is an database object representing real DNS server.

    :param name: Unique DNS server name (usually, FQDN)
    :param ip: Server's IP address
    :param description: Optional description
    :param sync_channel: Synchronization channel name
    """
    class Meta:
        verbose_name = _("DNS Server")
        verbose_name_plural = _("DNS Servers")
        db_table = "dns_dnsserver"
        app_label = "dns"

    name = models.CharField(_("Name"), max_length=64, unique=True)
    ip = INETField(_("IP"), null=True, blank=True)
    description = models.CharField(_("Description"), max_length=128,
        blank=True, null=True)
    sync = DocumentReferenceField(Sync, blank=True, null=True)

    def __unicode__(self):
        return self.name
