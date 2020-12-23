# ----------------------------------------------------------------------
# Compressor loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseCompressor


class CompressorLoader(BaseLoader):
    name = "compressor"
    base_cls = BaseCompressor
    base_path = ("core", "compressor")
    ignored_names = {"base", "loader", "util"}


loader = CompressorLoader()
