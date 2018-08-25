# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# AS discovery job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from ..base import MODiscoveryJob
from noc.peer.models.asn import AS
from .prefix import PrefixCheck
from noc.core.span import Span


class ASDiscoveryJob(MODiscoveryJob):
    model = AS

    def handler(self, whois_route=None, **kwargs):
        if whois_route:
            self.set_artefact("whois_route", whois_route)
        with Span(sample=0):
            PrefixCheck(self).run()

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
        pass
