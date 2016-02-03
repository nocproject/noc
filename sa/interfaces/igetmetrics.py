# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetMetrics interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import (Interface, DictParameter, DictListParameter,
                  IntParameter, StringParameter, FloatParameter)


class IGetMetrics(Interface):
    metrics = DictParameter()
    hints = DictParameter(required=False)
    returns = DictListParameter(attrs={
        # Measure timestamp
        "ts": IntParameter(),
        # Metric name
        "name": StringParameter(),
        #
        "tags": DictParameter(),
        #
        "value": FloatParameter(),
        #
        "type": StringParameter(
            choices=["gauge", "counter"]
        ),
        #
        "scale": FloatParameter(default=1)
    })
