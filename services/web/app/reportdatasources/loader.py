# ----------------------------------------------------------------------
# ReportDataSource Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import os

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import ReportDataSource

logger = logging.getLogger(__name__)
BASE_PREFIX = os.path.join("lib", "app", "reportdatasources")


class ReportDataSourceLoader(BaseLoader):
    name = "reportdatasource"
    base_cls = ReportDataSource
    base_path = ("lib", "app", "reportdatasources")
    ignored_names = {"base", "loader"}


# Create singleton object
loader = ReportDataSourceLoader()
