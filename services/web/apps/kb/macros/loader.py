# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Macro Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
import os

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseMacro

logger = logging.getLogger(__name__)
BASE_PREFIX = os.path.join("services", "web", "apps", "kb", "macros")


class KBMacroLoader(BaseLoader):
    name = "kbmacro"
    base_cls = BaseMacro
    base_path = ("services", "web", "apps", "kb", "macros")
    ignored_names = {"base", "loader"}


# Create singleton object
loader = KBMacroLoader()
