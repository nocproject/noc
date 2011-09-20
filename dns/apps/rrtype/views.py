# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNS RR Types Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext as _
## NOC modules
from noc.lib.app import ExtModelApplication
from noc.dns.models import DNSZoneRecordType


class DNSZoneRecordTypeApplication(ExtModelApplication):
    title = _("RR Types")
    model = DNSZoneRecordType
    menu = "Setup | RR Types"
