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
    partition: int = 0
    # TimeZone offset in seconds
    utc_offset: Optional[int] = 0
    # Optional data
    data: Optional[Dict[str, Any]] = None

    def get_data(self):
        """
        Convert data format:
        {"meta.id": "123"} ->  {"meta": {"id": "123}}
        :return:
        """
        r = {}
        if not self.data:
            return r
        for key in self.data:
            key1, *key2 = key.split(".", 1)
            if key2 and key1 not in r:
                r[key1] = {key2[0]: self.data[key]}
            elif key2:
                r[key1][key2[0]] = self.data[key]
            else:
                r[key1] = self.data[key]
        return r
