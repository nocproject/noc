# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetMetrics interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import (
    DictParameter, DictListParameter, IntParameter,
    StringParameter, FloatParameter, StringListParameter)


class IGetMetrics(BaseInterface):
    """
    Collect metrics from managed object
    """
    metrics = DictListParameter(attrs={
        # Opaque id to be returned in response
        "id": IntParameter(),
        # Metric type
        "metric": StringParameter(),
        # Optional path
        "path": StringListParameter(required=False),
        # ifindex hint
        "ifindex": IntParameter(required=False),
        # SLA probe hint
        "sla_tests": DictListParameter(attrs={
            # Test name
            "name": StringParameter(),
            # Test type
            "types": StringParameter()
        }, required=False)
    })
    returns = DictListParameter(attrs={
        # Opaque id as in input
        "id": IntParameter(),
        # Measurement timestamp
        "ts": IntParameter(),
        # Metric name, as *metric* in *metrics* input
        "metric": StringParameter(),
        # Metric path as *path* in *metrics* input
        "path": StringListParameter(required=False),
        # Measured value
        "value": FloatParameter(),
        # Measurement type
        "type": StringParameter(
            choices=["gauge", "counter", "bool"]
        ),
        # Measurement scale
        "scale": IntParameter(default=1)
    })
