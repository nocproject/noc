# ---------------------------------------------------------------------
# Streaming model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class StreamingConfig(object):
    # Liftbridge stream name
    stream: str
    # Liftbridge partition
    partition: int
    # TimeZone offset in seconds
    utc_offset: Optional[int] = 0
    # Stream message format
    format: Optional[str] = None
    # Optional data
    data: Optional[Dict[str, Any]] = None
