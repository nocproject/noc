# ----------------------------------------------------------------------
# Report DataSource Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseDataSource


class DataSourceLoader(BaseLoader):
    name = "datasource"
    base_cls = BaseDataSource
    base_path = ("core", "datasources")
    ignored_names = {"loader", "base"}


# Create singleton object
loader = DataSourceLoader()
