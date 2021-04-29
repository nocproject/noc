# ----------------------------------------------------------------------
# Dependency operations
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Callable


class ListOp(object):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def get_transform(self, value) -> Callable:
        def inner(qs):
            return qs

        return inner


class FilterExact(ListOp):
    def get_transform(self, value):
        def inner(qs):
            return qs.filter(**{self.name: value})

        return inner
