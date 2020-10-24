# ----------------------------------------------------------------------
# BaseETLModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Iterable
from itertools import zip_longest

# Third-party modules
from pydantic import BaseModel as _BaseModel
import orjson


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class BaseModel(_BaseModel):
    id: str

    class Config(object):
        json_loads = orjson.loads
        json_dumps = orjson_dumps

    # List of legacy fields in sequental order
    _csv_fields = []

    @classmethod
    def from_iter(cls, value: Iterable[Any]) -> "BaseModel":
        """
        Convert tuple or list from legacy CSV to BaseModel instance
        :param iter:
        :return:
        """
        return cls(**{fn: val for fn, val in zip_longest(cls._csv_fields, value) if fn})
