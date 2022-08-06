# ----------------------------------------------------------------------
# Checkers loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import Checker


class CheckersLoader(BaseLoader):
    name = "checkers"
    base_cls = Checker
    base_path = ("core", "checkers")
    ignored_names = {"loader", "base"}


# Create singleton object
loader = CheckersLoader()
