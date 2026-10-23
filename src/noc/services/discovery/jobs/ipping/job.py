# ----------------------------------------------------------------------
# IP Ping discovery job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.ip.models.prefixprofile import PrefixProfile
from noc.core.span import Span
from ..base import MODiscoveryJob
from .address import AddressCheck

DEFAULT_INTERVAL = 600


class IPPingDiscoveryJob(MODiscoveryJob):
    model = PrefixProfile

    def handler(self, **kwargs):
        with Span(sample=0):
            AddressCheck(self).run()

    def can_run(self):
        return True

    def get_interval(self):
        return DEFAULT_INTERVAL

    def get_failed_interval(self):
        return DEFAULT_INTERVAL

    def update_alarms(self):
        """
        Disable umbrella alarms creation
        :return:
        """
