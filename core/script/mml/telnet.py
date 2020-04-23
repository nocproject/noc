# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..cli.telnet import TelnetIOStream
from .base import MMLBase


class TelnetMML(MMLBase):
    iostream_class = TelnetIOStream
    default_port = 23
