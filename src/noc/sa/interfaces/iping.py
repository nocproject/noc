# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import (
    IPParameter,
    DictParameter,
    IntParameter,
    BooleanParameter,
    StringParameter,
    FloatParameter,
)


class IPing(BaseInterface):
    check = "remoteping"
    check_script = "ping"

    address = IPParameter()
    count = IntParameter(required=False)
    source_address = IPParameter(required=False)
    size = IntParameter(required=False)
    df = BooleanParameter(required=False)
    vrf = StringParameter(required=False)
    returns = DictParameter(
        attrs={
            "success": IntParameter(),
            "count": IntParameter(),
            "min": FloatParameter(required=False),
            "avg": FloatParameter(required=False),
            "max": FloatParameter(required=False),
        }
    )

    def get_check_params(self, check):
        return {"address": check["address"]}

    def clean_check_result(self, check, result):
        return {
            "status": bool(result["success"]),
            "address": check["address"],
            "metrics": [
                {
                    "metric_type": "Check | Result",
                    "value": result["success"],
                    "labels": [
                        f"noc::check::name::{self.check}",
                        f"noc::check::arg0::{check['address']}",
                    ],
                }
            ],
        }
