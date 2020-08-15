# ----------------------------------------------------------------------
# BaseTokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterator, Tuple


class BaseTokenizer(object):
    name = None

    def __init__(self, data: str):
        self.data = data

    def __iter__(self) -> Iterator[Tuple[str]]:
        return iter(())
