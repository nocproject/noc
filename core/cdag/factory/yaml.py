# ----------------------------------------------------------------------
# YAMLCDAGFactory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
import yaml

# NOC modules
from .base import CDAG
from .config import ConfigCDAGFactory, NodeItem, FactoryCtx


class YAMLCDAGFactory(ConfigCDAGFactory):
    def __init__(
        self,
        graph: CDAG,
        config: str,
        ctx: Optional[FactoryCtx] = None,
        namespace: Optional[str] = None,
    ):
        items = [NodeItem(**i) for i in yaml.safe_load(config)]
        super().__init__(graph, items, ctx, namespace)
