# ----------------------------------------------------------------------
# JSONCDAGFactory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
import orjson

# NOC modules
from .base import CDAG
from .config import ConfigCDAGFactory, GraphConfig, FactoryCtx


class JSONCDAGFactory(ConfigCDAGFactory):
    def __init__(
        self,
        graph: CDAG,
        config: str,
        cfx: Optional[FactoryCtx] = None,
        namespace: Optional[str] = None,
    ):
        cfg = GraphConfig(**orjson.loads(config))
        super().__init__(graph, cfg, cfx, namespace)
