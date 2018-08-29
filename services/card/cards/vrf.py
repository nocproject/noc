# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# VRF card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from .base import BaseCard


class VRFCard(BaseCard):
    name = "vrf"
    default_template_name = "vrf"
    model = VRF

    def get_data(self):
        ipv4_prefix = Prefix.objects.filter(vrf=self.object, prefix="0.0.0.0/0")[:1]
        if ipv4_prefix:
            ipv4_prefix = ipv4_prefix[0]
        else:
            ipv4_prefix = None
        ipv6_prefix = Prefix.objects.filter(vrf=self.object, prefix="::/0")[:1]
        if ipv6_prefix:
            ipv6_prefix = ipv6_prefix[0]
        else:
            ipv6_prefix = None
        return {
            "object": self.object,
            "ipv4_prefix": ipv4_prefix,
            "ipv6_prefix": ipv6_prefix
        }
