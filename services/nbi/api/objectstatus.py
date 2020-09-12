# ----------------------------------------------------------------------
# objectstatus NBI API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import orjson

# NOC modules
from noc.core.service.apiaccess import authenticated
from noc.sa.interfaces.base import DictParameter, StringListParameter
from noc.sa.models.objectstatus import ObjectStatus
from ..base import NBIAPI


Request = DictParameter(attrs={"objects": StringListParameter(required=True)})


class ObjectStatusAPI(NBIAPI):
    name = "objectstatus"

    @authenticated
    async def post(self):
        code, result = await self.executor.submit(self.handler)
        self.set_status(code)
        if isinstance(result, str):
            self.write(result)
        else:
            self.write(orjson.dumps(result))

    def handler(self):
        # Decode request
        try:
            req = orjson.loads(self.request.body)
        except ValueError:
            return 400, "Cannot decode JSON"
        # Validate
        try:
            req = Request.clean(req)
            objects = [int(o) for o in req["objects"]]
        except ValueError as e:
            return 400, "Bad request: %s" % e
        statuses = ObjectStatus.get_statuses(objects)
        r = {"statuses": [{"id": str(o), "status": statuses.get(o, False)} for o in objects]}
        return 200, r
