# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Segment discovery job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

from noc.core.span import Span
from noc.inv.models.networksegment import NetworkSegment

from .mac import MACDiscoveryCheck
# NOC modules
from ..base import MODiscoveryJob


class SegmentDiscoveryJob(MODiscoveryJob):
    model = NetworkSegment

    def handler(self, **kwargs):
        with Span(sample=0):
            MACDiscoveryCheck(self).run()

    def can_run(self):
        return True

    def get_interval(self):
        if self.object:
            return self.object.profile.discovery_interval

    def get_failed_interval(self):
        return self.object.object_profile.discovery_interval

    def update_alarms(self):
        """
        Disable umbrella alarms creation
        :return:
        """
        pass
