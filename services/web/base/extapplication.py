# ---------------------------------------------------------------------
# ExtApplication implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from builtins import str
from typing import Optional, List, Dict, Any  # noqa
import os
import re

# Third-party modules
from django.http import HttpResponse
from django.db.models.query import QuerySet
from cachetools import TTLCache, cached
import orjson

# NOC modules
from noc.main.models.favorites import Favorites
from noc.main.models.slowop import SlowOp
from noc.config import config
from noc.models import is_document
from .application import Application, view
from .access import HasPerm, PermitLogged


class ExtApplication(Application):
    menu = None
    icon = "icon_application_form"
    # HTTP Result Codes
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
    # Recognized GET parameters
    ignored_params = ["_dc"]
    page_param = "__page"
    start_param = "__start"
    limit_param = "__limit"
    sort_param = "__sort"
    group_param = "__group"
    format_param = "__format"  # List output format
    query_param = "__query"
    only_param = "__only"
    in_param = "__in"
    fav_status = "fav_status"
    wf_state = False
    default_ordering = []
    exclude_fields: Optional[List[str]] = []

    rx_oper_splitter = re.compile(r"^(?P<field>\S+?)(?P<f_num>\d+)__in")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document_root = os.path.join("services", "web", "apps", self.module, self.app)
        self.row_limit = config.web.api_row_limit
        self.unlimited_row_limit = config.web.api_unlimited_row_limit
        self.pk = "id"
        # Bulk fields API
        self.bulk_fields = []
        for fn in [n for n in dir(self) if n.startswith("bulk_field_")]:
            h = getattr(self, fn)
            if callable(h):
                self.bulk_fields += [h]

    def apply_bulk_fields(self, data):
        """
        Pass data through bulk_field_* handlers to enrich instance_to_dict result
        :param data: dict or list of dicts
        :return: dict or list of dicts
        """
        if not self.bulk_fields:
            return data
        if isinstance(data, dict):
            # Single dict
            nd = [data]
            for h in self.bulk_fields:
                h(nd)
            return data
        # List of dicts
        for h in self.bulk_fields:
            h(data)
        return data

    @property
    def js_app_class(self):
        m, a = self.get_app_id().split(".")
        return "NOC.%s.%s.Application" % (m, a)

    @property
    def launch_access(self):
        m, a = self.get_app_id().split(".")
        return HasPerm("%s:%s:launch" % (m, a))

    def deserialize(self, data):
        return orjson.loads(data)

    def deserialize_form(self, request):
        return {str(k): v[0] if len(v) == 1 else v for k, v in request.POST.lists()}

    def response(self, content="", status=200):
        if not isinstance(content, str):
            return HttpResponse(
                orjson.dumps(content, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS),
                content_type="text/json; charset=utf-8",
                status=status,
            )
        else:
            return HttpResponse(content, content_type="text/plain; charset=utf-8", status=status)

    def fav_convert(self, item):
        """
        Convert favorite item from string to storage format
        """
        return str(item)

    def get_favorite_items(self, user):
        """
        Returns a set of user's favorite items
        """
        f = Favorites.objects.filter(user=user.id, app=self.app_id).first()
        if f:
            return set(f.favorites)
        else:
            return set()

    @staticmethod
    @cached(TTLCache(maxsize=12, ttl=900))
    def get_exclude_states():
        from noc.wf.models.state import State

        return list(State.objects.filter(hide_with_state=True).scalar("id"))

    @staticmethod
    def format_label(ll):
        return {
            "id": ll.name,
            "is_protected": ll.is_protected,
            "scope": ll.scope,
            "name": ll.name,
            "value": ll.value,
            "badges": ll.badges,
            "bg_color1": f"#{ll.bg_color1:06x}",
            "fg_color1": f"#{ll.fg_color1:06x}",
            "bg_color2": f"#{ll.bg_color2:06x}",
            "fg_color2": f"#{ll.fg_color2:06x}",
        }

    def extra_query(self, q, order):
        # raise NotImplementedError
        return {}, order

    def cleaned_query(self, q):
        raise NotImplementedError

    def queryset(self, request, query=None):
        raise NotImplementedError

    def instance_to_dict(self, o):
        raise NotImplementedError

    def parse_request_query(self, request) -> Dict[str, Any]:
        """

        :param request:
        :return:
        """
        if request.method != "POST":
            q = {str(k): v[0] if len(v) == 1 else v for k, v in request.GET.lists()}
        elif self.site.is_json(request.META.get("CONTENT_TYPE")):
            q = self.deserialize(request.body)
        else:
            q = {str(k): v[0] if len(v) == 1 else v for k, v in request.POST.lists()}
        return q

    def list_data(self, request, formatter):
        """
        Returns a list of requested object objects
        """
        q = self.parse_request_query(request)
        # Apply row limit if necessary
        limit = q.get(self.limit_param, self.unlimited_row_limit)
        if limit:
            try:
                limit = max(int(limit), 0)
            except ValueError:
                return HttpResponse(400, "Invalid %s param" % self.limit_param)
        if limit and limit < 0:
            return HttpResponse(400, "Invalid %s param" % self.limit_param)
        # page = q.get(self.page_param)
        start = q.get(self.start_param) or 0
        if start:
            try:
                start = max(int(start), 0)
            except ValueError:
                return HttpResponse(400, "Invalid %s param" % self.start_param)
        elif start and start < 0:
            return HttpResponse(400, "Invalid %s param" % self.start_param)
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
        grouping = None
        if request.is_extjs and self.group_param in q:
            r = self.deserialize(q[self.group_param])
            if r["direction"] == "DESC":
                grouping = "-%s" % r["property"]
            else:
                grouping = r["property"]
        fs = None
        fav_items = None
        if self.fav_status in q:
            fs = q.pop(self.fav_status) == "true"
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
            if xaa:
                # data = self.queryset(request, query).filter(**q).extra(**xaa)
                xa.update(xaa)
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
            elif isinstance(data, QuerySet):  # Model
                data = data.exclude(id__in=fav_items)
            else:  # Doc
                data = data.filter(id__nin=fav_items)
        if self.wf_state and "state" not in q:
            states = self.get_exclude_states()
            if states and is_document(self.model):
                data = data.filter(state__nin=states)
            elif states:
                data = data.exclude(state__in=[str(x) for x in states])
        # Store unpaged/unordered queryset
        unpaged_data = data
        # Select related records when fetching for models
        if hasattr(data, "_as_sql"):  # For Models only
            data = data.select_related()
        # Apply sorting
        ordering = ordering or self.default_ordering
        if ordering:
            data = data.order_by(*ordering)
        if grouping:
            ordering.insert(0, grouping)
        # Apply row limit if necessary
        if self.row_limit:
            limit = min(limit or self.row_limit, self.row_limit + 1)
        # Apply paging
        if limit:
            data = data[start : start + limit]
        # Fetch and format data
        out = [formatter(o, fields=only) for o in data]
        if self.row_limit and len(out) > self.row_limit + 1:
            return self.response(
                "System records limit exceeded (%d records)" % self.row_limit, status=self.TOO_LARGE
            )
        # Set favorites
        if not only and formatter == self.instance_to_dict:
            if fav_items is None:
                fav_items = self.get_favorite_items(request.user)
            for r in out:
                r[self.fav_status] = r[self.pk] in fav_items
        # Bulk update result. Enrich with proper fields
        out = self.clean_list_data(out)
        #
        if request.is_extjs:
            ld = len(out)
            if limit and (ld == limit or start > 0):
                total = unpaged_data.count()
            else:
                total = ld
            out = {"total": total, "success": True, "data": out}
        return self.response(out, status=self.OK)

    def clean_list_data(self, data):
        """
        Finally process list_data result. Override to enrich with
        additional fields
        :param data:
        :return:
        """
        return self.apply_bulk_fields(data)

    @view(
        url=r"^favorites/app/(?P<action>set|reset)/$",
        method=["POST"],
        access=PermitLogged(),
        api=True,
    )
    def api_favorites_app(self, request, action):
        """
        Set/reset favorite app status
        """
        v = action == "set"
        fv = Favorites.objects.filter(user=request.user.id, app=self.app_id).first()
        if fv:
            if fv.favorite_app != v:
                fv.favorite_app = v
                fv.save()
        elif v:
            Favorites(user=request.user, app=self.app_id, favorite_app=v).save()
        return True

    @view(
        url=r"^favorites/item/(?P<item>[0-9a-f]+)/(?P<action>set|reset)/$",
        method=["POST"],
        access=PermitLogged(),
        api=True,
    )
    def api_favorites_items(self, request, item, action):
        """
        Set/reset favorite items
        """
        item = self.fav_convert(item)
        if action == "set":
            Favorites.add_item(request.user, self.app_id, item)
        else:
            Favorites.remove_item(request.user, self.app_id, item)
        return True

    @view(url=r"^futures/(?P<f_id>[0-9a-f]{24})/$", method=["GET"], access="launch", api=True)
    def api_future_status(self, request, f_id):
        op = self.get_object_or_404(SlowOp, id=f_id, user=request.user.username)
        if op.is_ready():
            # Note: the slow operation will be purged by TTL index
            result = op.result()
            if isinstance(result, Exception):
                return self.render_json(
                    {"success": False, "message": "Error", "traceback": str(result)},
                    status=self.INTERNAL_ERROR,
                )
            else:
                return result
        else:
            return self.response_accepted(request.path)

    def submit_slow_op(self, a, request, **kwargs):
        res = SlowOp.submit(a, user=request.user.username, **kwargs)
        return res

    def get_status_slow_op(self, future_id, request):
        res = SlowOp.status_slw(future_id, request=request)
        return res

    def get_list_slow_op(self, request):
        res = SlowOp.list_slw(request)
        return res

    def get_statuses_slow_op(self, request):
        res = SlowOp.statuses_slw(request)
        return res
