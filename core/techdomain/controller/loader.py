# ----------------------------------------------------------------------
# Controller loader class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseController


class ControllerLoader(BaseLoader):
    name = "controllers"
    base_cls = BaseController
    base_path = ("core", "techdomain", "controller")
    ignored_names = {"loader", "base"}


# Create singleton object
loader = ControllerLoader()
