# ---------------------------------------------------------------------
# IGetMetrics interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import (
    DictListParameter,
    IntParameter,
    StringParameter,
    FloatParameter,
    StringListParameter,
    OIDParameter,
)


class IGetMetrics(BaseInterface):
    """
    Collect metrics from managed object
    """

    metrics = DictListParameter(
        attrs={
            # Opaque id to be returned in response
            "id": IntParameter(),
            # Metric type
            "metric": StringParameter(),
            # Optional path
            "labels": StringListParameter(required=False),
            # oid hint
            "oid": OIDParameter(required=False),
            # ifindex hint
            "ifindex": IntParameter(required=False),
            # SLA probe hint
            "sla_type": StringParameter(required=False),
        },
        required=False,
    )
    collected = DictListParameter(
        attrs={
            # "cpe", "sla", "sensor", "managed_object"
            "collector": StringParameter(default="managed_object"),
            # List Metric type for collected
            "metrics": StringListParameter(),
            # Optional key labels
            "labels": StringListParameter(required=False),
            # Like settings: ifindex::<ifindex>, oid::<oid>, ac::<SC/CS/S/C>
            "hints": StringListParameter(required=False),
            "service": IntParameter(required=False),
            # Collector field id
            "sensor": IntParameter(required=False),
            "sla_probe": IntParameter(required=False),
            "cpe": IntParameter(required=False),
        },
        required=False,
    )
    returns = DictListParameter(
        attrs={
            # Opaque id as in input
            "id": IntParameter(),
            # Measurement timestamp
            "ts": IntParameter(),
            # Metric name, as *metric* in *metrics* input
            "metric": StringParameter(),
            # Metric path as *labels* in *metrics* input
            "labels": StringListParameter(required=False),
            # Measured value
            "value": FloatParameter(),
            # Measurement type
            "type": StringParameter(choices=["gauge", "counter", "bool", "delta"]),
            # Measurement scale
            "scale": IntParameter(default=1),
            # Measurement units
            "units": StringParameter(required=False),
        }
    )
