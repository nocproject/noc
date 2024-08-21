# ---------------------------------------------------------------------
# IDiagnosticCheck
# SAE service to check address availability
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import (
    DictListParameter,
    DictParameter,
    IPParameter,
    StringParameter,
    BooleanParameter,
    IntParameter,
    FloatParameter,
    LabelListParameter,
)


class IDiagnosticCheck(BaseInterface):
    checks = DictListParameter(
        attrs={
            "name": StringParameter(required=True),
            "args": DictParameter(required=False),
            "address": IPParameter(required=False),
            "port": IntParameter(required=False),
        },
        required=True,
    )
    returns = DictListParameter(
        attrs={
            "status": BooleanParameter(required=True),
            "address": IPParameter(required=False),
            "port": IntParameter(required=False),
            "skipped": BooleanParameter(default=False),
            "error": DictParameter(
                attrs={
                    "code": StringParameter(required=True),
                    "message": StringParameter(required=False),
                    "is_access": BooleanParameter(required=False),
                    "is_available": BooleanParameter(required=False),
                },
                required=False,
            ),
            "data": DictListParameter(
                attrs={
                    "name": StringParameter(required=True),
                    "value": StringParameter(required=True),
                },
                required=False,
            ),
            "metrics": DictListParameter(
                attrs={
                    "metric_type": StringParameter(required=True),
                    "value": FloatParameter(required=True),
                    "labels": LabelListParameter(required=False),
                },
                required=False,
            ),
        }
    )
