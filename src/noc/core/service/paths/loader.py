# ----------------------------------------------------------------------
# FastAPI Path Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import importlib

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.core.loader.base import BaseLoader


class PathLoader(BaseLoader):
    name = "path"
    base_path = ("core", "service", "paths")
    ignored_names = {"loader"}

    def find_class(self, module_name, base_cls, name):
        """
        Load subclass of *base_cls* from module

        :param module_name: String containing module name
        :param base_cls: Base class
        :param name: object name
        :return: class reference or None
        """
        try:
            sm = importlib.import_module(module_name)
            if hasattr(sm, "router") and isinstance(sm.router, APIRouter):
                return sm.router
        except ImportError as e:
            self.logger.error("Failed to load %s %s: %s", self.name, name, e)
        return None


class ServicePathLoader(PathLoader):
    pass


loader = PathLoader()
