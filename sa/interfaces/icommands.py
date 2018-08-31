# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Interface to execute series of commands and return a list of results
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.interface.base import BaseInterface
from .base import BooleanParameter, StringListParameter, DictParameter


class ICommands(BaseInterface):
    # List of commands
    commands = StringListParameter()
    # Do not stop on CLI errors
    ignore_cli_errors = BooleanParameter(default=False)
    returns = DictParameter(attrs={
        "errors": BooleanParameter(default=False),  # Has CLI errors when execute
        "output": StringListParameter()  # Device output
    })
