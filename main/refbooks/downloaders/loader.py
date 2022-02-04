# ----------------------------------------------------------------------
# Downloader Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseDownloader


class DownloaderLoader(BaseLoader):
    name = "downloader"
    ignored_names = {"base", "loader"}
    base_cls = BaseDownloader
    base_path = ("main", "refbooks", "downloaders")


# Create singleton object
loader = DownloaderLoader()
