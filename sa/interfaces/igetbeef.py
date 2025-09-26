# ----------------------------------------------------------------------
# IGetBeefInterface
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import (
    DictParameter,
    DictListParameter,
    StringParameter,
    IntParameter,
    OIDParameter,
    StringListParameter,
)

Q_TYPES = [
    "str",  # Arbitrary string answer
    "int",  # Arbitrary integer answer
    "bool",  # Arbitrary boolean parameter
    "cli",  # CLI command, should be executed
    "snmp-get",  # Single SNMP get
    "snmp-getnext",  # Getnext/bulk
]


class IGetBeef(BaseInterface):
    # Input spec
    spec = DictParameter(
        attrs={
            # Spec format version
            "version": StringParameter(default="1"),
            # @todo: Replace with UUID parameter
            "uuid": StringParameter(),
            "revision": IntParameter(default=1, required=False),
            "profile": StringParameter(),
            "author": StringParameter(),
            # @todo: Replace with UUID
            "quiz": StringParameter(),
            "answers": DictListParameter(
                attrs={
                    "name": StringParameter(),
                    "type": StringParameter(choices=Q_TYPES),
                    # Command for type == cli
                    # OID for type == snmp-get, snmp-getnext
                    "value": StringParameter(),
                    # Arbitrary comment from expert
                    "comment": StringParameter(required=False),
                }
            ),
        }
    )
    # Returned beef
    returns = DictParameter(
        attrs={
            # Beef format version
            "version": StringParameter(default="1"),
            # @todo: Replace with UUID parameter
            "uuid": StringParameter(),
            # spec.uuid
            "spec": StringParameter(),
            "box": DictParameter(
                attrs={
                    "profile": StringParameter(),
                    "vendor": StringParameter(),
                    "platform": StringParameter(),
                    "version": StringParameter(),
                }
            ),
            "changed": StringParameter(),
            "description": StringParameter(required=False),
            # CLI setup FSM sequences
            "cli_fsm": DictListParameter(
                attrs={"state": StringParameter(), "reply": StringListParameter()}
            ),
            # Output for type == cli
            "cli": DictListParameter(
                attrs={
                    # ans.name
                    "names": StringListParameter(),
                    # ans.value
                    "request": StringParameter(),
                    "reply": StringListParameter(),
                }
            ),
            # MIB dump
            "mib": DictListParameter(attrs={"oid": OIDParameter(), "value": StringParameter()}),
            # MIB binary encoding
            "mib_encoding": StringParameter(default="hex", choices=["hex", "base64"]),
            # CLI binary encoding
            "cli_encoding": StringParameter(default="quopri", choices=["quopri"]),
        }
    )
