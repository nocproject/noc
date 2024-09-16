# ---------------------------------------------------------------------
# Result data type
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass

# Third-party modules
from django.http import HttpResponse
import orjson


@dataclass
class Result(object):
    status: bool
    message: str | None = None

    def to_json(self) -> dict[str, bool | str]:
        """
        Render as dict suitable to serialize to json.

        Returns:
            Dict form.
        """
        r = {"status": self.status}
        if self.message:
            r["message"] = self.message
        return r

    def as_response(self) -> HttpResponse:
        """
        Render as HttpResponse.
        """
        return HttpResponse(
            orjson.dumps(
                self.to_json(), option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS
            ),
            content_type="text/json",
            status=200 if self.status else 400,
        )
