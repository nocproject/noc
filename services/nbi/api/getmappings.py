# ----------------------------------------------------------------------
# nbi getmappings API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator

# Third-party modules
import tornado.gen
import ujson

# NOC modules
from noc.core.service.apiaccess import authenticated
from noc.models import get_model
from noc.main.models.remotesystem import RemoteSystem
from ..base import NBIAPI


class GetMappingsAPI(NBIAPI):
    name = "getmappings"
    SCOPES = {"managedobject": "sa.ManagedObject"}

    @staticmethod
    def cleaned_request(scope=None, id=None, remote_system=None, remote_id=None, **kwargs):
        def to_list(s):
            if s is None:
                return None
            if isinstance(s, list):
                return [str(x) for x in s]
            return [str(s)]

        if not scope:
            raise ValueError("scope must be set")
        if scope not in GetMappingsAPI.SCOPES:
            raise ValueError("Invalid scope: %s" % scope)
        if remote_id and not remote_system:
            raise ValueError("remote_system must be set")
        if not id and not remote_id:
            raise ValueError("At least one id or remote_id must be set")
        return {
            "scope": scope,
            "local_ids": to_list(id),
            "remote_system": remote_system if remote_id else None,
            "remote_ids": to_list(remote_id),
        }

    @authenticated
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        yield self.to_executor(self.do_post)

    def do_post(self):
        # Decode request
        try:
            req = ujson.loads(self.request.body)
        except ValueError:
            return 400, self.error_msg("Cannot decode JSON")
        # Validate
        try:
            req = self.cleaned_request(**req)
        except ValueError as e:
            return 400, self.error_msg("Bad request: %s" % e)

        return self.do_mapping(**req)

    @authenticated
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        try:
            req = self.cleaned_request(
                scope=self.get_argument("scope", None),
                id=self.get_arguments("id"),
                remote_id=self.get_arguments("remote_id"),
                remote_system=self.get_argument("remote_system", None),
            )
        except ValueError as e:
            self.write_result(400, "Bad request: %s" % e)
            return
        yield self.to_executor(self.do_mapping, **req)

    @tornado.gen.coroutine
    def to_executor(self, handler, *args, **kwargs):
        """
        Continue processing on executor
        :param handler:
        :param args:
        :param kwargs:
        :return:
        """
        code, result = yield self.executor.submit(handler, *args, **kwargs)
        self.write_result(code, result)

    def write_result(self, code, result):
        self.set_status(code)
        if isinstance(result, str):
            self.write(result)
        else:
            self.set_header("Content-Type", "text/json")
            self.write(ujson.dumps(result))

    @staticmethod
    def error_msg(msg):
        return {"status": False, "error": msg}

    def do_mapping(self, scope, local_ids=None, remote_system=None, remote_ids=None):
        """
        Perform mapping
        :param scope: scope name
        :param local_ids: List of Local id
        :param remote_system: Remote system id
        :param remote_ids: List of Id from remote system
        :param kwargs: Ignored args
        :return:
        """

        def format_obj(o):
            r = {"scope": scope, "id": str(o.id), "mappings": []}
            if o.remote_system:
                r["mappings"] += [
                    {"remote_system": str(o.remote_system.id), "remote_id": str(o.remote_id)}
                ]
            return r

        # Get model to query
        model = get_model(self.SCOPES[scope])
        if not model:
            return 400, self.error_msg("Invalid scope")
        # Query remote objects
        result = []
        if remote_system and remote_ids:
            rs = RemoteSystem.get_by_id(remote_system)
            if not rs:
                return 404, self.error_msg("Remote system not found")
            if len(remote_ids) == 1:
                qs = model.objects.filter(remote_system=rs.id, remote_id=remote_ids[0])
            else:
                qs = model.objects.filter(remote_system=rs.id, remote_id__in=remote_ids)
            result += [format_obj(o) for o in qs]
        # Query local objects
        seen = set(o["id"] for o in result)
        # Skip already collected objects
        local_ids = local_ids or []
        local_ids = [o for o in local_ids if o not in seen]
        if local_ids:
            if len(local_ids) == 1:
                qs = model.objects.filter(id=local_ids[0])
            else:
                qs = model.objects.filter(id__in=local_ids)
            result += [format_obj(o) for o in qs]
        # 404 if no objects found
        if not result:
            return 404, self.error_msg("Not found")
        return 200, list(sorted(result, key=operator.itemgetter("id")))
