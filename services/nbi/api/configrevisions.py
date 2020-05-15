# ----------------------------------------------------------------------
# configrevisions API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import ujson

# NOC modules
from noc.core.service.apiaccess import authenticated
from noc.sa.models.managedobject import ManagedObject
from ..base import NBIAPI


class ConfigRevisionsAPI(NBIAPI):
    name = "configrevisions"

    @authenticated
    async def get(self, object_id):
        code, result = await self.executor.submit(self.handler, object_id)
        self.set_status(code)
        if isinstance(result, str):
            self.write(result)
        else:
            self.set_header("Content-Type", "text/json")
            self.write(ujson.dumps(result))

    def handler(self, object_id):
        mo = ManagedObject.get_by_id(int(object_id))
        if not mo:
            return 404, "Not Found"
        revs = [
            {"revision": str(r.id), "timestamp": r.ts.isoformat()}
            for r in mo.config.get_revisions()
        ]
        return 200, revs

    @classmethod
    def get_path(cls):
        return r"%s/(\d+)" % cls.name
