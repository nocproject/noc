# ----------------------------------------------------------------------
# Tracer loader class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseTracer


class TracerLoader(BaseLoader):
    name = "tracers"
    base_cls = BaseTracer
    base_path = ("core", "techdomain", "tracer")
    ignored_names = {"loader", "base"}


# Create singleton object
loader = TracerLoader()
