# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NBI API Loader
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
from .base import NBIAPI

logger = logging.getLogger(__name__)
BASE_PREFIX = os.path.join("services", "nbi", "api")


class NBIAPILoader(BaseLoader):
    name = "nbi"
    base_cls = NBIAPI
    base_path = ("services", "nbi", "api")


# Create singleton object
loader = NBIAPILoader()
