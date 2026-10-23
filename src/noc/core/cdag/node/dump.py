# ----------------------------------------------------------------------
# DumpNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
from collections.abc import Callable

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .base import BaseCDAGNode, Category, IN_OPTIONAL, IN_REQUIRED


class DumpNodeConfig(BaseModel):
    out_format: str | None = None
    output: str | None = "console"


NS = 1_000_000_000

# scope -> name -> cleaner
scope_cleaners: dict[str, dict[str, Callable]] = {}

logger = logging.getLogger(__name__)


class DumpNode(BaseCDAGNode):
    """
    Collect all dynamic inputs and send all on log
    """

    name = "dump"
    categories = [Category.DEBUG]
    config_cls = DumpNodeConfig
    dot_shape = "folder"

    def get_value(self, ts: int, labels: list[str], **kwargs) -> None:
        r = []
        for k, v in kwargs.items():
            if v is None:
                continue
            r.append(f"{k}: {v}")
        ts = datetime.datetime.fromtimestamp(ts // NS)
        logger.info(f"[{ts}|{';'.join(labels)}] Inputs: {','.join(r)}")

    def get_input_type(self, name: str) -> int:
        if name in {"ts", "labels"}:
            return IN_REQUIRED
        return IN_OPTIONAL
