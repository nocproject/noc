# ----------------------------------------------------------------------
# Pydentic models for MRT service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List

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


class MRTArgs(BaseModel):
    commands: List[str]
    include_commands: str
    ignore_cli_errors: str


class MRTScript(BaseModel):
    id: str
    script: str
    args: MRTArgs
