# ----------------------------------------------------------------------
# Pydentic models for MRT service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Optional, Literal

# Third-party modules
from pydantic import BaseModel

# [
#   {
#     "id": "19129",
#     "script": "commands",
#     "args": {
#       "commands": [
#         "display version"
#       ],
#       "include_commands": "true",
#       "ignore_cli_errors": "true"
#     }
#   }
# ]


class MRTCommandsArgs(BaseModel):
    commands: List[str]
    include_commands: bool = False
    config_mode: bool = False
    ignore_cli_errors: bool = False


class MRTInterfaceArgs(BaseModel):
    interface: str


class MRTInterfaceScript(BaseModel):
    id: int
    script: Literal["get_mac_address_table"]
    args: Optional[MRTInterfaceArgs]


class MRTAnyScript(BaseModel):
    id: int
    script: Literal["get_version"]


class MRTCommandScript(BaseModel):
    id: int
    script: Literal["commands"]
    args: MRTCommandsArgs
