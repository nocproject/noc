# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Interface to execute series of commands and return a list of results
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface

from base import BooleanParameter, StringListParameter


class ICommands(BaseInterface):
    # List of commands
    commands = StringListParameter()
    # Do not stop on CLI errors
    ignore_cli_errors = BooleanParameter(default=False)
    returns = StringListParameter()
