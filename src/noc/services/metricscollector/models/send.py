# ----------------------------------------------------------------------
# SendRequest
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Any

# Third-party modules
from pydantic import BaseModel, RootModel, model_validator


class SendRequestItem(BaseModel):
    ts: datetime.datetime
    labels: list[str] | None
    service: int
    collector: str
    metrics: dict[str, Any]

    @model_validator(mode="before")
    def build_metrics(cls, values: dict[str, Any]) -> dict[str, Any]:
        r: dict[str, Any] = {
            f: values[f] for f in cls.model_fields if f in values and f != "metrics"
        }
        r["metrics"] = {f: values[f] for f in values if f not in cls.model_fields}
        return r


SendRequest = RootModel[list[SendRequestItem]]
