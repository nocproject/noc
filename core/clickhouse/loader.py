# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Model loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.loader.base import BaseLoader
from .model import Model


class ModelLoader(BaseLoader):
    name = "bi"
    base_cls = Model
    base_path = ("bi", "models")
    ignored_names = {"dashboard", "dashboardlayout"}

    def is_valid_class(self, kls, name):
        if not hasattr(kls, "_meta"):
            return False
        return getattr(kls._meta, "db_table", None) == name


# Create singleton object
loader = ModelLoader()
