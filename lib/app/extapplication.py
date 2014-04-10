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
from django.views.static import serve as serve_static
from django.http import HttpResponse
## NOC modules
from application import Application, view
from access import HasPerm, PermitLogged
from noc.lib.serialize import json_decode, json_encode
from noc.main.models.favorites import Favorites


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
    fav_status = "fav_status"
    default_ordering = []

    def __init__(self, *args, **kwargs):
        super(ExtApplication, self).__init__(*args, **kwargs)
        self.document_root = os.path.join(self.module, "apps", self.app)
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
        fs = None
        fav_items = None
        if self.fav_status in q:
            fs = q.pop(self.fav_status) == "true"
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
        if format == "ext":
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
        fv = Favorites.objects.filter(
            user=request.user.id, app=self.app_id).first()
        if fv:
            fi = fv.favorites
            if v and item not in fi:
                fv.favorites += [item]
                fv.save()
            elif not v and item in fi:
                fi.remove(item)
                fv.favorites = fi
                fv.save()
        elif v:
            # Add single item
            Favorites(user=request.user, app=self.app_id,
                favorites=[item]).save()
        return True

    @view(url="^templates/(?P<name>[0-9a-zA-Z_/]+)\.js$", access=True)
    def view_template(self, request, name):
        """
        Handlebars template wrapper
        """
        src = os.path.join(self.document_root,
            "templates", "%s.html" % name)
        if not os.path.isfile(src):
            return self.response_not_found()
        with open(src) as f:
            tpl = f.read()
        return self.render_plain_text("""
Ext.apply(
    NOC.templates, {
        "%s": Ext.merge(
            NOC.templates["%s"] || {},
            {
                %s: Handlebars.compile(%r)
            }
        )
    }
);
Ext.define("NOC.%s.templates.%s", {});
""" % (self.app_id, self.app_id, name, tpl, self.app_id, name),
            mimetype="application/javascript;charset=utf-8")
