# ----------------------------------------------------------------------
# Compression utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Type

# NOC modules
from noc.config import config
from noc.core.compressor.base import BaseCompressor
from noc.core.compressor.loader import loader


compressor: Type[BaseCompressor] = loader.get_class(config.etl.compression)
