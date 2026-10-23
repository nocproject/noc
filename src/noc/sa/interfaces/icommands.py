# ---------------------------------------------------------------------
# Interface to execute series of commands and return a list of results
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import (
    BooleanParameter,
    StringParameter,
    StringListParameter,
    DictParameter,
    DictListParameter,
)


class ICommands(BaseInterface):
    # List of commands
    commands = StringListParameter()
    # Do not stop on CLI errors
    ignore_cli_errors = BooleanParameter(default=False)
    # Return executed commands
    include_commands = BooleanParameter(default=False)
    # Execute command on Device Config Mode
    config_mode = BooleanParameter(default=False)
    # Execute without execute on CLI
    dry_run = BooleanParameter(default=False)
    returns = DictParameter(
        attrs={
            "errors": BooleanParameter(default=False),  # Has CLI errors when execute
            "output": StringListParameter(),  # Device output
            # Detail result
            "details": DictListParameter(
                attrs={
                    "command": StringParameter(required=True),
                    "skipped": BooleanParameter(default=False),
                    "error": StringParameter(required=False),
                    "code": StringParameter(required=False),
                }
            ),
        }
    )
