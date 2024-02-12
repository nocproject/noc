# ----------------------------------------------------------------------
# IP Ping discovery job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..base import MODiscoveryJob
from noc.ip.models.prefixprofile import PrefixProfile
from .address import AddressCheck
from noc.core.span import Span

#                 Job.submit(
#                     "scheduler",
#                     self.JCLS_IPPING_PREFIX,
#                     key=AS.get_by_asn(int(a[2:])).id,
#                     delta=delay,
#                     data={},
#                 )


class IPPingDiscoveryJob(MODiscoveryJob):
    model = PrefixProfile

    def handler(self, profile_id=None, **kwargs):
        if profile_id:
            self.set_artefact("profile_id", profile_id)
        with Span(sample=0):
            AddressCheck(self).run()

    def can_run(self):
        return True

    def get_interval(self):
        return None

    def get_failed_interval(self):
        return None

    def update_alarms(self):
        """
        Disable umbrella alarms creation
        :return:
        """
