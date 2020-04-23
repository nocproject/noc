# ----------------------------------------------------------------------
# Middleware loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseMiddleware


class MiddlewareLoader(BaseLoader):
    name = "middleware"
    base_cls = BaseMiddleware
    base_path = ("core", "script", "http", "middleware")


loader = MiddlewareLoader()
