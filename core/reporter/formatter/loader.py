# ----------------------------------------------------------------------
# Report DataFormatter Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import DataFormatter


class DataFormatterLoader(BaseLoader):
    name = "dataformatter"
    base_cls = DataFormatter
    base_path = ("core", "reporter", "formatter")
    ignored_names = {"loader", "base"}


# Create singleton object
loader = DataFormatterLoader()
