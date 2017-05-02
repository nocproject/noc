# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ExtApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
## Django modules
from django.http import HttpResponse
import ujson
## NOC modules
from application import Application, view
from access import HasPerm, PermitLogged
from noc.main.models.favorites import Favorites
from noc.main.models.slowop import SlowOp


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
    TOO_LARGE = 413
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
    in_param = "__in"
    fav_status = "fav_status"
    default_ordering = []

    def __init__(self, *args, **kwargs):
        super(ExtApplication, self).__init__(*args, **kwargs)
        self.document_root = os.path.join("services", "web", "apps", self.module, self.app)
        self.row_limit = self.config.getint("main", "json_row_limit")
        self.pk = "id"

    @property
    def js_app_class(self):
        m, a = self.get_app_id().split(".")
        return "NOC.%s.%s.Application" % (m, a)

    @property
    def launch_access(self):
        m, a = self.get_app_id().split(".")
        return HasPerm("%s:%s:launch" % (m, a))

    def deserialize(self, data):
        return ujson.loads(data)

    def response(self, content="", status=200):
        if not isinstance(content, basestring):
            return HttpResponse(ujson.dumps(content),
                mimetype="text/json; charset=utf-8",
                status=status)
        else:
            return HttpResponse(content,
                mimetype="text/plain; charset=utf-8",
                status=status)

    def fav_convert(self, item):
        """
        Convert favorite item from string to storage format
        """
        return str(item)

    def get_favorite_items(self, user):
        """
        Returns a set of user's favorite items
        """
        f = Favorites.objects.filter(
            user=user.id, app=self.app_id).first()
        if f:
            return set(f.favorites)
        else:
            return set()

    def extra_query(self, q, order):
        # raise NotImplementedError
        return {}, order

    def cleaned_query(self, q):
        raise NotImplementedError

    def queryset(self, request, query=None):
        raise NotImplementedError

    def list_data(self, request, formatter):
        """
        Returns a list of requested object objects
        """
        # Todo: Fix
        if request.method == "POST":
            q = dict((str(k), v[0] if len(v) == 1 else v)
                     for k, v in request.POST.lists())
        else:
            q = dict((str(k), v[0] if len(v) == 1 else v)
                     for k, v in request.GET.lists())
        limit = q.get(self.limit_param)
        # page = q.get(self.page_param)
        start = q.get(self.start_param)
        query = q.get(self.query_param)
        only = q.get(self.only_param)
        if only:
            only = only.split(",")
        ordering = []
        if request.is_extjs and self.sort_param in q:
            for r in self.deserialize(q[self.sort_param]):
                if r["direction"] == "DESC":
                    ordering += ["-%s" % r["property"]]
                else:
                    ordering += [r["property"]]
        fs = None
        fav_items = None
        if self.fav_status in q:
            fs = q.pop(self.fav_status) == "true"
        # @todo Filter models field (validate) data.model._meta.get_all_field_names()
        xaa, ordering = self.extra_query(q, ordering)
        q = self.cleaned_query(q)
        if None in q:
            w = []
            p = []
            for x in q.pop(None):
                if type(x) in (list, tuple):
                    w += [x[0]]
                    p += x[1]
                else:
                    w += [x]
            xa = {"where": w}
            if p:
                xa["params"] = p
            data = self.queryset(request, query).filter(**q).extra(**xa)
        elif xaa:
            # ExtraQuery
            data = self.queryset(request, query).filter(**q).extra(**xaa)
        else:
            data = self.queryset(request, query).filter(**q)
        # Favorites filter
        if fs is not None:
            fav_items = self.get_favorite_items(request.user)
            if fs:
                data = data.filter(id__in=fav_items)
            else:
                data = data.exclude(id__in=fav_items)
        if hasattr(data, "_as_sql"):  # For Models only
            data = data.select_related()
        # Apply sorting
        ordering = ordering or self.default_ordering
        if ordering:
            data = data.order_by(*ordering)
        if request.is_extjs:
            total = data.count()  # Total unpaged count
        if start is not None and limit is not None:
            data = data[int(start):int(start) + int(limit)]
        ld = len(data)
        if self.row_limit and ld > self.row_limit:
            # Request too large
            return self.response(
                "System limit is %d records (%d requested)" % (self.row_limit, ld),
                status=self.TOO_LARGE)
        out = [formatter(o, fields=only) for o in data]
        # Set favorites
        if not only and formatter == self.instance_to_dict:
            if fav_items is None:
                fav_items = self.get_favorite_items(request.user)
            for r in out:
                r[self.fav_status] = r[self.pk] in fav_items
        if request.is_extjs:
            out = {
                "total": total,
                "success": True,
                "data": out
            }
        return self.response(out, status=self.OK)

    @view(url="^favorites/app/(?P<action>set|reset)/$",
        method=["POST"],
        access=PermitLogged(), api=True)
    def api_favorites_app(self, request, action):
        """
        Set/reset favorite app status
        """
        v = action == "set"
        fv = Favorites.objects.filter(
            user=request.user.id, app=self.app_id).first()
        if fv:
            if fv.favorite_app != v:
                fv.favorite_app = v
                fv.save()
        elif v:
            Favorites(user=request.user, app=self.app_id,
                favorite_app=v).save()
        return True

    @view(url="^favorites/item/(?P<item>[0-9a-f]+)/(?P<action>set|reset)/$",
        method=["POST"],
        access=PermitLogged(), api=True)
    def api_favorites_items(self, request, item, action):
        """
        Set/reset favorite items
        """
        v = action == "set"
        item = self.fav_convert(item)
        if action == "set":
            Favorites.add_item(request.user, self.app_id, item)
        else:
            Favorites.remove_item(request.user, self.app_id, item)
        return True

    @view(url="^futures/(?P<f_id>[0-9a-f]{24})/$", method=["GET"],
          access="launch", api=True)
    def api_future_status(self, request, f_id):
        op = self.get_object_or_404(SlowOp, id=f_id,
                                    app_id=self.get_app_id(),
                                    user=request.user.username)
        if op.is_ready():
            # Note: the slow operation will be purged by TTL index
            result = op.result()
            if isinstance(result, Exception):
                return self.render_json({
                    "success": False,
                    "message": "Error",
                    "traceback": str(result)
                }, status=self.INTERNAL_ERROR)
            else:
                return result
        else:
            return self.response_accepted(request.path)

    def submit_slow_op(self, request, fn, *args, **kwargs):
        f = SlowOp.submit(
            fn,
            self.get_app_id(), request.user.username,
            *args, **kwargs
        )
        if f.done():
            return f.result()
        else:
            return self.response_accepted(
                location="%sfutures/%s/" % (self.base_url, f.slow_op.id)
            )
