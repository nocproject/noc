## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TestCheck
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random
## NOC modules
from noc.pm.pmprobe.checks.base import BaseCheck
from noc.sa.interfaces.base import IntParameter


class TestCheck(BaseCheck):
    name = "test"

    description = """
        Generate random time series:
            int: Integer
            float: Float
            bool: boolean
    """

    parameters = {
        "min": IntParameter(),
        "max": IntParameter
    }

    time_series = [
        "int",
        "float",
        "bool"
    ]

    form = "NOC.pm.check.test.TestCheckForm"

    def handle(self):
        i = random.randint(self.config["min"], self.config["max"])
        f = random.random() * (self.config["max"] - self.config["min"]) + self.config["min"]
        b = random.random() >= 0.5
        return {
            "int": i,
            "float": f,
            "bool": b
        }
