# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..cli.stream import BaseStream
from ..cli.telnet import TelnetStream
from .base import MMLBase


class TelnetMML(MMLBase):
    name = "mml"

    def get_stream(self) -> BaseStream:
        return TelnetStream(self)
