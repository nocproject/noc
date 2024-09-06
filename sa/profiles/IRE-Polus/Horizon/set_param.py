# ---------------------------------------------------------------------
# IRE-Polus.Horizon.set_param
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import orjson

# NOC modules
from noc.core.script.base import BaseScript
from noc.core.script.http.base import HTTPError
from noc.core.interface.base import BaseInterface
from noc.sa.interfaces.base import BooleanParameter, StringParameter, IntParameter


class ISetParam(BaseInterface):
    # Chassis id
    chassis = IntParameter(default=1)
    # Card id
    card = IntParameter(required=True)
    # Param name
    name = StringParameter(required=True)
    # Param value
    value = StringParameter()
    returns = BooleanParameter()


class Script(BaseScript):
    name = "IRE-Polus.Horizon.set_param"
    interface = ISetParam

    def execute_cli(self, chassis, card, name, value):
        req_data = {
            "crateId": chassis,
            "slotNumber": card,
            "name": name,
            "value": value,
        }

        try:
            self.http.post(
                "/api/devices/params/set",
                orjson.dumps(req_data),
                headers={"Content-Type": b"application/json"},
                json=True,
            )
        except HTTPError as e:
            self.logger.warning(
                "Error core %s received while set_param. Message is |%s|", e.code, e
            )
            return False

        return True
