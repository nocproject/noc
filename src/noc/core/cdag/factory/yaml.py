# ----------------------------------------------------------------------
# YAMLCDAGFactory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Python modules
import yaml

from .base import CDAG
from .config import ConfigCDAGFactory, FactoryCtx, GraphConfig


class YAMLCDAGFactory(ConfigCDAGFactory):
    def __init__(
        self,
        graph: CDAG,
        config: str,
        ctx: FactoryCtx | None = None,
        namespace: str | None = None,
    ):
        cfg = GraphConfig(**yaml.safe_load(config))
        super().__init__(graph, cfg, ctx, namespace)
