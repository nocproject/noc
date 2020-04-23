# ----------------------------------------------------------------------
# config API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import tornado.gen

# NOC modules
from noc.core.service.apiaccess import authenticated
from noc.sa.models.managedobject import ManagedObject
from ..base import NBIAPI


class ConfigAPI(NBIAPI):
    name = "config"

    @authenticated
    @tornado.gen.coroutine
    def get(self, object_id, revision=None):
        code, result = yield self.executor.submit(self.handler, object_id, revision)
        self.set_status(code)
        self.set_header("Content-Type", "text/plain")
        if code != 204:
            self.write(result)

    def handler(self, object_id, revision):
        mo = ManagedObject.get_by_id(int(object_id))
        if not mo:
            return 404, "Not Found"
        if revision:
            if not mo.config.has_revision(revision):
                return 404, "Revision not found"
            config = mo.config.get_revision(revision)
        else:
            config = mo.config.read()
        if config is None:
            return 204, ""
        return 200, config

    @classmethod
    def get_path(cls):
        return r"%s/(\d+)" % cls.name, r"%s/(\d+)/([0-9a-f]{24})" % cls.name
