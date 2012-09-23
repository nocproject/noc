# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ExtApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Django modules
from django.views.static import serve as serve_static
from django.http import HttpResponse
## NOC modules
from application import Application, view, HasPerm
from noc.lib.serialize import json_decode, json_encode


class ExtApplication(Application):
    menu = None
    icon = "icon_application_form"
    ## HTTP Result Codes
    OK = 200
    CREATED = 201
    DELETED = 204
    BAD_REQUEST = 400
    FORBIDDEN = 401
    NOT_FOUND = 404
    CONFLICT = 409
    NOT_HERE = 410
    INTERNAL_ERROR = 500
    NOT_IMPLEMENTED = 501
    THROTTLED = 503
    ## Recognized GET parameters
    ignored_params = ["_dc"]
    page_param = "__page"
    start_param = "__start"
    limit_param = "__limit"
    sort_param = "__sort"
    format_param = "__format"  # List output format
    query_param = "__query"
    only_param = "__only"

    def __init__(self, *args, **kwargs):
        super(ExtApplication, self).__init__(*args, **kwargs)
        self.document_root = os.path.join(self.module, "apps", self.app)

    @property
    def js_app_class(self):
        m, a = self.get_app_id().split(".")
        return "NOC.%s.%s.Application" % (m, a)

    @property
    def launch_access(self):
        m, a = self.get_app_id().split(".")
        return HasPerm("%s:%s:launch" % (m, a))

    def deserialize(self, data):
        return json_decode(data)

    def response(self, content="", status=200):
        if not isinstance(content, basestring):
            return HttpResponse(json_encode(content),
                mimetype="text/json; charset=utf-8",
                status=status)
        else:
            return HttpResponse(content,
                mimetype="text/plain; charset=utf-8",
                status=status)

    def cleaned_query(self, q):
        raise NotImplementedError

    def queryset(self, request, query=None):
        raise NotImplementedError

    def list_data(self, request, formatter):
        """
        Returns a list of requested object objects
        """
        # Todo: Fix
        q = dict((str(k), v[0] if len(v) == 1 else v)
            for k, v in request.GET.lists())
        limit = q.get(self.limit_param)
        # page = q.get(self.page_param)
        start = q.get(self.start_param)
        format = q.get(self.format_param)
        query = q.get(self.query_param)
        only = q.get(self.only_param)
        if only:
            only = only.split(",")
        ordering = []
        if format == "ext" and self.sort_param in q:
            for r in self.deserialize(q[self.sort_param]):
                if r["direction"] == "DESC":
                    ordering += ["-%s" % r["property"]]
                else:
                    ordering += [r["property"]]
        q = self.cleaned_query(q)
        if None in q:
            ew = q.pop(None)
            data = self.queryset(request, query).filter(**q).extra(where=ew)
        else:
            data = self.queryset(request, query).filter(**q)
        if hasattr(data, "_as_sql"):  # For Models only
            data = data.select_related()
        # Apply sorting
        if ordering:
            data = data.order_by(*ordering)
        if format == "ext":
            total = data.count()
        if start is not None and limit is not None:
            data = data[int(start):int(start) + int(limit)]
        out = [formatter(o, fields=only) for o in data]
        if format == "ext":
            out = {
                "total": total,
                "success": True,
                "data": out
            }
        return self.response(out, status=self.OK)

    @view(url="^(?P<path>(?:js|css|img)/[0-9a-zA-Z_/]+\.(?:js|css|png))$",
          url_name="static", access=True)
    def view_static(self, request, path):
        """
        Static file server
        """
        return serve_static(request, path, document_root=self.document_root)
