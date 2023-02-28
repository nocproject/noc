# ----------------------------------------------------------------------
# Report Source Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from noc.core.reporter.reportsource import ReportSource


class ReportSourcesLoader(BaseLoader):
    name = "reportsources"
    base_cls = ReportSource
    base_path = ("main", "reportsources")
    ignored_names = {"loader", "base"}


# Create singleton object
loader = ReportSourcesLoader()
