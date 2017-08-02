# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetSLAProbe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.interface.base import BaseInterface
from base import (DictListParameter, StringParameter,
                  BooleanParameter)


class IGetSLAProbes(BaseInterface):
    """
    name: Unique probe name
    description: Probe description
    tests: List of configured tests
        name: Unique test name
        type: Test type
        target: Target IP or URL, depending on test
    """
    returns = DictListParameter(attrs={
        "name": StringParameter(),
        "description": StringParameter(required=False),
        "tests": DictListParameter(attrs={
            "name": StringParameter(),
            "type": StringParameter(choices=[
                "icmp-echo",
                "path-jitter",
                "udp-echo",
                "http-get",
                "dns",
                "ftp",
                "dhcp",
                "owamp",  # One-Way Active Measurement Protocol (RFC4656)
                "twamp"   # Two-Way Active Measurement Protocol (RFC5357)
            ]),
            "target": StringParameter(),
            "hw_timestamp": BooleanParameter(default=False)
        })
    })
