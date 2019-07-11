# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Parser Loader
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
from .base import BaseParser

logger = logging.getLogger(__name__)
BASE_PREFIX = os.path.join("services", "web", "apps", "kb", "parsers")


class KBParserLoader(BaseLoader):
    name = "kbparser"
    base_cls = BaseParser
    base_path = ("services", "web", "apps", "kb", "parsers")
    ignored_names = {"base", "loader"}


# Create singleton object
loader = KBParserLoader()
