# ----------------------------------------------------------------------
# Collector Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .collectors.base import BaseCollector


class CollectorLoader(BaseLoader):
    name = "collector"
    ignored_names = {"base"}
    base_cls = BaseCollector
    base_path = ("services", "selfmon", "collectors")


# Create singleton object
loader = CollectorLoader()
