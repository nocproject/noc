# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: Ericsson
# OS:     BS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Ericsson.BS"
    command_submit = "\r"
    pattern_prompt = r"(?:^\$ )|(?:\[ManagedElement=1\])"

    class ncli(object):
        """Switch context manager to use with "with" statement"""

        def __init__(self, script):
            self.script = script

        def __enter__(self):
            """Enter switch context"""
            self.script.cli("ncli")

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave switch context"""
            if exc_type is None:
                self.script.cli("exit")
