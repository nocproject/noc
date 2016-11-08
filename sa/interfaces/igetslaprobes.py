# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetSLAProbe
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


## NOC modules
from base import (Interface, DictListParameter, StringParameter,
                  BooleanParameter)


class IGetSLAProbes(Interface):
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
                "udp-echo",
                "http-get",
                "dns",
                "ftp",
                "dhcp"
            ]),
            "target": StringParameter(),
            "hw_timestamp": BooleanParameter(default=False)
        })
    })
