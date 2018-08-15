# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Rebuild datastreams from scratch
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.dns.models.dnszone import DNSZone
from noc.core.datastream.change import bulk_datastream_changes


def fix():
    for model in [AdministrativeDomain, ManagedObject, DNSZone]:
        with bulk_datastream_changes():
            for obj in model.objects.all():
                obj.save()  # Force datastream rebuild
