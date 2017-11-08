# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# System Version Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import sys

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.simplereport import *
from noc.lib.nosql import get_connection
from noc.lib.version import get_version


class ReportSystemVersion(SimpleReport):
    title = _("System Version")

    def get_data(self, **kwargs):
        si = get_connection().server_info()
        versions = [
            ["NOC", get_version()],
            SectionRow("Host Software"),
            ["OS", " ".join(os.uname())],
            ["Python", sys.version],
            ["PostgreSQL", self.execute("SELECT VERSION()")[0][0]],
            ["MongoDB", "%s (%dbit)" % (si["version"], si["bits"])]
        ]
        versions += [SectionRow("Python Path")]
        for p in sys.path:
            versions += [("", p)]
        return self.from_dataset(
            title=self.title,
            columns=["Component", "Version"],
            data=versions
        )
