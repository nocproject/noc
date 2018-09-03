# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetMetrics interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import (DictListParameter, IntParameter, StringParameter, FloatParameter, StringListParameter)


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
        "sla_type": StringParameter(required=False)
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
            choices=["gauge", "counter", "bool", "delta"]
        ),
        # Measurement scale
        "scale": IntParameter(default=1)
    })
