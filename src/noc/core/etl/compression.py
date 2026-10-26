# ----------------------------------------------------------------------
# Compression utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from noc.config import config
from noc.core.compressor.base import BaseCompressor, compressor_loader

compressor: type[BaseCompressor] = compressor_loader.get(config.etl.compression)
