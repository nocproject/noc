# ----------------------------------------------------------------------
# BaseTokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections.abc import Iterator

# Third-party modules
from gufo.loader import Loader

# NOC modules
from noc.config import config


class BaseTokenizer:
    name = None

    def __init__(self, data: str) -> None:
        self.data = data

    def __iter__(self) -> Iterator[tuple[str]]:
        return iter(())


tokenizer_loader = Loader[type[BaseTokenizer]](
    bases=config.iter_customized_bases("noc.core.confdb.tokenizer"),
    exclude=("base",),
)
