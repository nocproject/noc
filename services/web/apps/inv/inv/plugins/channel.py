# ---------------------------------------------------------------------
# inv.inv channel plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import List, Optional, Iterable, Tuple, Dict, DefaultDict
from collections import defaultdict

# Third party modules
from bson import ObjectId

# NOC modules
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection
from .base import InvPlugin


class ChannelPlugin(InvPlugin):
    name = "channel"
    js = "NOC.inv.inv.plugins.channel.ChannelPanel"

    def init_plugin(self):
        super().init_plugin()

    def get_data(self, request, object):
        return {
            "records": [
                {
                    "id": "1"*24,
                    "name": "Ch1",
                    "tech_domain": "444",
                    "tech_domain__label": "Optical SM",
                },
                {
                    "id": "2"*24,
                    "name": "Ch2",
                    "tech_domain": "444",
                    "tech_domain__label": "Optical SM",
                },
            ]
        }
