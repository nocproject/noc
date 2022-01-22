# ---------------------------------------------------------------------
# IGetInventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import (
    DictListParameter,
    StringParameter,
    BooleanParameter,
    FloatParameter,
    StringListParameter,
    REStringParameter,
    OIDParameter,
    LabelListParameter,
)


class IGetInventory(BaseInterface):
    returns = DictListParameter(
        attrs={
            # Object type, used in ConnectionRule
            "type": StringParameter(required=False),
            # Object number as reported by script
            "number": StringParameter(required=False),
            # Builtin modules apply ConnectionRule scopes
            # But does not submitted into database
            "builtin": BooleanParameter(default=False),
            # Object vendor. Must match Vendor.code
            "vendor": StringParameter(),
            # List of part numbers
            # May contain
            # * NOC model name
            # * asset.part_no* value (Part numbers)
            # * asset.order_part_no* value (FRU numbers)
            "part_no": StringListParameter(convert=True),
            # Optional revision
            "revision": StringParameter(required=False),
            # Serial number
            "serial": StringParameter(required=False),
            #
            "mfg_date": REStringParameter(r"^\d{4}-\d{2}-\d{2}$", required=False),
            # Optional description
            "description": StringParameter(required=False),
            # Optional internal crossing
            "crossing": DictListParameter(
                attrs={
                    # Input connection name, according to model
                    "in": StringParameter(),
                    # Output connection name, according to model
                    "out": StringParameter(),
                    # Power gain, in dB
                    "gain": FloatParameter(),
                },
                required=False,
            ),
            # Optional Sensors
            "sensors": DictListParameter(
                attrs={
                    # Sensor number inside object, for deduplicate
                    # "number": StringParameter(),
                    # Sensor name. Must be unique
                    "name": StringParameter(required=True),
                    # Sensor operational status
                    # True - ok (agent can obtain the sensor value)
                    # False - nonoperational (agent believes the sensor is broken)
                    "status": BooleanParameter(default=True),
                    # Optional description
                    "description": StringParameter(required=False),
                    #
                    "labels": LabelListParameter(required=False),
                    # MeasurementUnit Name
                    "measurement": StringParameter(default="Scalar"),
                    # Collected hints
                    # OID for collecting by SNMP
                    "snmp_oid": OIDParameter(required=False),
                    # ID for IPMI collected
                    "ipmi_id": StringParameter(required=False),
                    # Optional internals Thresholds ?
                },
                required=False,
            ),
        }
    )
    preview = "NOC.sa.managedobject.scripts.ShowInventory"
