# ----------------------------------------------------------------------
# Dashboadr Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import os

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseDashboard

logger = logging.getLogger(__name__)
BASE_PREFIX = os.path.join("services", "web", "apps", "pm", "ddash", "dashboards")


class PMDashboardLoader(BaseLoader):
    name = "pmdashboard"
    base_cls = BaseDashboard
    base_path = ("services", "web", "apps", "pm", "ddash", "dashboards")
    ignored_names = {"base", "loader", "jinja"}
    caps_map = {}

    def __init__(self):
        super().__init__()
        for name in self.find_classes():
            r = self[name]
            caps = getattr(r, "has_capability", None)
            if caps:
                self.caps_map[caps] = r


# Create singleton object
loader = PMDashboardLoader()
