# ----------------------------------------------------------------------
# BI JSON-RPC API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import zlib
import threading
import operator
from collections import defaultdict

# Third-party modules
import bson
from fastapi import APIRouter
import orjson
import uuid
from mongoengine.queryset import Q
import cachetools

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.loader import loader
from noc.core.bi.dictionaries.loader import loader as dict_loader
from noc.core.service.jsonrpcapi import JSONRPCAPI, api, executor, APIError
from noc.aaa.models.user import User
from noc.aaa.models.group import Group
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from noc.bi.models.dashboard import Dashboard, DashboardAccess, DAL_ADMIN, DAL_RO
from noc.sa.interfaces.base import DictListParameter, DictParameter, IntParameter, StringParameter
from noc.core.perf import metrics
from noc.core.comp import smart_bytes
from noc.core.translation import ugettext as _
from noc.config import config


router = APIRouter()

# Access items validations
I_VALID = DictListParameter(
    attrs={
        "group": DictParameter(
            attrs={"id": IntParameter(required=True), "name": StringParameter(required=False)},
            required=False,
        ),
        "user": DictParameter(
            attrs={"id": IntParameter(required=True), "name": StringParameter(required=False)},
            required=False,
        ),
        "level": IntParameter(min_value=-1, max_value=3, default=-1),
    }
)

DEFAULT_USER = "NOC"

ds_lock = threading.Lock()
model_lock = threading.Lock()


class BIAPI(JSONRPCAPI):
    """
    BI API
    """

    api_name = "api_bi"
    api_description = "Service BI API"
    openapi_tags = ["JSON-RPC API"]
    url_path = "/api/bi"
    auth_required = True

    _ds_cache = cachetools.TTLCache(maxsize=1000, ttl=300)
    _model_cache = cachetools.TTLCache(maxsize=1000, ttl=300)

    ref_dict = {"sa.ManagedObject": "managedobject"}

    @classmethod
    def get_pm_datasources(cls):
        result = []
        # Collect fields
        scope_fields = defaultdict(list)
        for mt in MetricType.objects.all().order_by("field_name"):
            scope_fields[mt.scope.table_name] += [
                {
                    "name": mt.field_name,
                    "description": mt.description,
                    "type": mt.field_type,
                    "dict": None,
                }
            ]
        # Attach scopes as datasources
        for ms in MetricScope.objects.all().order_by("table_name"):
            r = {
                "name": ms.table_name,
                "description": ms.description,
                "tags": [],
                "sample": False,
                "fields": [
                    {"name": "date", "description": "Date", "type": "Date", "dict": None},
                    {"name": "ts", "description": "Timestamp", "type": "DateTime", "dict": None},
                ],
            }
            for k in ms.key_fields:
                r["fields"] += [
                    {
                        "name": k.field_name,
                        "description": k.field_name,
                        "type": "UInt64",
                        "dict": (
                            f"{config.clickhouse.db_dictionaries}.{cls.ref_dict[k.model]}"
                            if k.model in cls.ref_dict
                            else None
                        ),
                        "model": k.model,
                    }
                ]
                if cls.ref_dict.get(k.model, None):
                    dcls = dict_loader[cls.ref_dict[k.model]]
                    if dcls:
                        for f in dcls._meta.ordered_fields:
                            r["fields"] += [
                                {
                                    "name": f.name,
                                    "description": f.description or f.name,
                                    "type": "UInt64",
                                    "ro": True,
                                    "dict": f"{config.clickhouse.db_dictionaries}.{cls.ref_dict[k.model]}",
                                    "dict_id": k.field_name,
                                    "model": k.model,
                                }
                            ]
            if ms.labels:
                r["fields"] += [
                    {
                        "name": "labels",
                        "description": "Metric labels",
                        "type": "Array(String)",
                        "dict": None,
                    }
                ]
            r["fields"] += scope_fields[ms.table_name]
            result += [r]
        return result

    @classmethod
    def get_bi_datasources(cls):
        result = []
        for mn in loader:
            model = loader[mn]
            if not model:
                continue
            r = {
                "name": model._meta.db_table,
                "description": model._meta.description,
                "tags": model._meta.tags,
                "sample": False,
                "fields": [],
            }
            for f in model._meta.ordered_fields:
                d = getattr(f, "dict_type", None)
                if d:
                    d = f"{config.clickhouse.db_dictionaries}.{d._meta.name}"
                r["fields"] += [
                    {
                        "name": f.name,
                        "description": _(f.description or ""),
                        "type": f.get_displayed_type(),
                        "is_agg": f.is_agg,
                        "dict": d,
                    }
                ]
                if hasattr(f, "model"):
                    r["fields"][-1]["model"] = f.model
            result += [r]
        return result

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_ds_cache"), lock=lambda _: ds_lock)
    def get_datasources(cls):
        return cls.get_bi_datasources() + cls.get_pm_datasources()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_model_cache"), lock=lambda _: model_lock)
    def get_model(cls, name):
        # Static datasource
        model = loader[name]
        if model:
            return model
        # Dynamic datasource
        return Model.wrap_table(name)

    @api
    def list_datasources(self):
        """
        Returns the list of available datasources.
        Each item is a dict of:
        * name -- unique datasource name, can be referred in queries
        * description -- optional description
        * tags -- list of tags
        :return: List of datasource items
        """
        return [
            {"name": ds["name"], "description": ds.get("description", ""), "tags": ds["tags"]}
            for ds in self.get_datasources()
        ]

    @api
    def get_datasource_info(self, name):
        """
        Returns datasource metadata as a dict of
        * name
        * description
        * tags
        * fields - list of dicts
            * name
            * description
            * type
        :param name:
        :return:
        """
        for ds in self.get_datasources():
            if ds["name"] == name:
                return ds
        metrics["error", ("type", "info_invalid_datasource")] += 1
        raise APIError("Invalid datasource")

    @executor("query")
    @api
    def query(self, query):
        """
        Perform query and return result
        :param query: Dict containing fields
            datasource - name of datasource
            see model.query for the rest
        :return:
        """
        if "datasource" not in query:
            metrics["error", ("type", "query_no_datasource")] += 1
            raise APIError("No datasource")
        model = self.get_model(query["datasource"])
        if not model:
            metrics["error", ("type", "query_invalid_datasource")] += 1
            raise APIError("Invalid datasource")
        return model.query(query, self.current_user)

    @executor("query")
    @api
    def list_dashboards(self, query=None):
        """
        Returns list of user dashboards. Each item is a dict of
        * id
        * title
        * description
        * tags
        * owner
        * created
        * changed
        :param query:
        :return:
        """
        user = self.current_user
        groups = user.groups.values_list("id", flat=True)
        aq = (
            Q(owner=user.id) | Q(owner=None) | Q(access__user=user.id) | Q(access__group__in=groups)
        )
        if user.is_superuser:
            aq = Q()
        if query and "query" in query:
            aq &= Q(title__icontains=query["query"])
        if query and "version" in query:
            aq &= Q(format=str(query["version"]))
        return [
            {
                "id": str(d.id),
                "format": int(d.format),
                "title": str(d.title),
                "description": str(d.description),
                "tags": str(d.tags),
                "owner": d.owner.username if d.owner else DEFAULT_USER,
                "created": d.created.isoformat(),
                "changed": d.changed.isoformat(),
            }
            for d in Dashboard.objects.filter(aq).exclude("config")
        ]

    def _get_dashboard(self, id, access_level=DAL_RO):
        """
        Returns dashboard or None
        :param id:
        :return:
        """
        user = self.current_user
        groups = user.groups.values_list("id", flat=True)
        d = Dashboard.objects.filter(id=id).first()
        if not d:
            return None
        if d.owner == DEFAULT_USER or d.owner == user or user.is_superuser:
            return d
        # @todo: Filter by groups
        for i in d.access:
            if i.user == user and i.level >= access_level:
                return d
            elif i.group and i.group.id in groups and i.level >= access_level:
                return d
        # No access
        metrics["error", ("type", "no_permission")] += 1
        raise APIError("User have no permission to access dashboard")

    @executor("query")
    @api
    def get_dashboard(self, id):
        """
        Returns dashboard config by id
        :param id:
        :return:
        """
        d = self._get_dashboard(id)
        if d:
            config = orjson.loads(zlib.decompress(smart_bytes(d.config)))
            config["id"] = str(d.id)
            config["title"] = d.title
            config["owner"] = d.owner.username if d.owner else DEFAULT_USER
            config["description"] = d.description
            return config
        else:
            metrics["error", ("type", "dashboard_not_found")] += 1
            raise APIError("Dashboard not found")

    @executor("query")
    @api
    def set_dashboard(self, config):
        """
        Save dashboard config.
        :param config:
        :return: datshboard id
        """
        if "id" in config:
            d = self._get_dashboard(config["id"], access_level=1)
            if not d:
                metrics["error", ("type", "dashboard_not_found")] += 1
                raise APIError("Dashboard not found")
        else:
            d = Dashboard.objects.filter(title=config.get("title")).first()
            if d:
                metrics["error", ("type", "bad_dashboard_name")] += 1
                raise APIError("Dashboard name exists")
            d = Dashboard(id=str(bson.ObjectId()), owner=self.current_user)
        d.format = config.get("format", 1)
        config["id"] = str(d.id)
        d.config = zlib.compress(orjson.dumps(config))
        d.changed = datetime.datetime.now()
        d.title = config.get("title")  # @todo: Generate title
        d.description = config.get("description")
        d.tags = config.get("tags", [])
        if not d.uuid:
            d.uuid = uuid.uuid4()
        d.save()
        return str(d.id)

    @executor("query")
    @api
    def remove_dashboard(self, id):
        """
        Remove user dashboard
        :param id:
        :return:
        """
        d = self._get_dashboard(id, access_level=2)
        if d:
            d.delete()
            return True
        else:
            metrics["error", ("type", "dashboard_not_found")] += 1
            raise APIError("Dashboard not found")

    @executor("query")
    @api
    def get_hierarchy(self, params):
        """
        Get Hierarchy data for field
        :param params:
        :return:
        """

        def search_parent(node, p_id):
            if p_id is None:
                return node
            if node and node["id"] == p_id:
                return node
            elif node and "children" in node:
                for child in node["children"]:
                    _searched = search_parent(child, p_id)
                    if _searched:
                        return _searched
            else:
                return None

        def sort_children(node):
            if "children" not in set(node):
                return
            else:
                node["children"] = sorted(node["children"], key=lambda x: x["text"])
                for n in node["children"]:
                    sort_children(n)

        if "datasource" not in params:
            metrics["error", ("type", "get_hierarchy_no_datasource")] += 1
            raise APIError("No datasource")
        if "dic_name" not in params:
            metrics["error", ("type", "get_hierarchy_no_dict_name")] += 1
            raise APIError("No dictionary name")
        if "field_name" not in params:
            metrics["error", ("type", "get_hierarchy_no_field_name")] += 1
            raise APIError("No field name")
        model = loader[params["datasource"]]
        if not model:
            metrics["error", ("type", "get_hierarchy_invalid_datasource")] += 1
            raise APIError("Invalid datasource")
        query = {
            "fields": [
                {"expr": {"$names": [params["dic_name"], params["field_name"]]}, "alias": "names"},
                {
                    "expr": {"$hierarchy": [params["dic_name"], {"$field": params["field_name"]}]},
                    "alias": "ids",
                },
                {"expr": params["field_name"], "group": 0},
            ],
            "datasource": params["datasource"],
        }
        if "limit" in params:
            query["limit"] = params["limit"]
        if "filter" in params:
            query["filter"] = {
                "$like": [
                    {"$lower": {"$field": "arrayElement(names,1)"}},
                    {"$lower": "%" + params["filter"] + "%"},
                ]
            }

        result = model.query(query, self.current_user)
        tree = {}
        for row in result["result"]:
            names = reversed([x[1:-1] for x in row[0][1:-1].split(",")])
            ids = reversed([str(x) for x in row[1][1:-1].split(",")])
            parent_id = None
            for id, text in zip(ids, names):
                searched = search_parent(tree, parent_id)
                parent_id = id
                if searched:
                    if searched["id"] != id:
                        if "children" not in searched:
                            searched["children"] = []
                        if id not in [x["id"] for x in searched["children"]]:
                            searched["children"] += [{"id": id, "text": text}]
                else:
                    # starting point
                    tree = {"id": id, "text": text, "children": []}

        sort_children(tree)
        return tree

    @executor("query")
    @api
    def list_users(self, query=None):
        qs = User.objects.all()
        if query and "query" in query:
            qs = qs.filter(username__icontains=query["query"])
        return sorted(
            (
                {
                    "id": u.id,
                    "username": u.username,
                    "full_name": "%s %s" % (u.last_name, u.first_name),
                }
                for u in qs
            ),
            key=lambda u: u["username"],
        )

    @executor("query")
    @api
    def list_groups(self, query=None):
        # @todo username - list groups for user
        qs = Group.objects.all()
        if query and "query" in query:
            qs = qs.filter(name__icontains=query["query"])
        qs = qs.order_by("name")
        return [{"id": g.id, "name": g.name} for g in qs]

    @executor("query")
    @api
    def get_dashboard_access(self, id):
        d = self._get_dashboard(id["id"])
        if not d:
            return None
        r = []
        for ar in d.access:
            i = {"level": ar.level}
            if ar.user:
                i["user"] = {
                    "id": ar.user.id,
                    "name": "%s %s" % (ar.user.last_name, ar.user.first_name),
                }
            if ar.group:
                i["group"] = {"id": ar.group.id, "name": ar.group.name}
            r += [i]
        return r

    @executor("query")
    @api
    def get_user_access(self, id):
        d = self._get_dashboard(id["id"])
        if not d:
            return None
        if self.current_user.is_superuser:
            return DAL_ADMIN
        return d.get_user_access(self.current_user)

    def _set_dashboard_access(self, id, items, acc_limit=""):
        """

        :param id: Dashboard ID
        :param items: Dictionary rights
        :param acc_limit: User or Group only set
        :return:
        """
        self.logger.info("Settings dashboard access")
        d = self._get_dashboard(id)
        if not d:
            self.logger.error("Dashboards not find %s", id)
            metrics["error", ("type", "dashboard_not_found")] += 1
            raise APIError("Dashboard not found")
        if d.get_user_access(self.current_user) < DAL_ADMIN:
            self.logger.error("Access for user Dashboards %s", self.current_user)
            metrics["error", ("type", "no_permissions_to_set_permissions")] += 1
            raise APIError("User have no permission to set permissions")
        access = []
        if acc_limit == "user":
            access = [x for x in d.access if x.user]
        elif acc_limit == "group":
            access = [x for x in d.access if x.group]
        if not items:
            # @todo Clear rights (protect Admin rights?)
            return True
        try:
            items = I_VALID.clean(items)
        except ValueError as e:
            self.logger.error("Validation items with rights: %s", e)
            metrics["error", ("type", "validation")] += 1
            raise APIError("Validation error %s" % e)
        for i in items:
            da = DashboardAccess(level=i.get("level", -1))
            if i.get("user"):
                da.user = User.objects.get(id=i["user"]["id"])
            if i.get("group"):
                da.group = Group.objects.get(id=i["group"]["id"])
            access += [da]
        d.access = access
        d.save()
        return True

    @executor("query")
    @api
    def set_dashboard_access(self, id, items):
        """

        :param id:
        :param items:
        :return:
        """
        if not id.get("id"):
            metrics["error", ("type", "wrong_json")] += 1
            raise APIError("Not id field in JSON")
        return self._set_dashboard_access(id.get("id"), items.get("items"))

    @executor("query")
    @api
    def set_dashboard_access_user(self, id, items):
        """

        :param id:
        :param items:
        :return:
        """
        if not id.get("id"):
            return False
        return self._set_dashboard_access(id.get("id"), items.get("items"), acc_limit="group")

    @executor("query")
    @api
    def set_dashboard_access_group(self, id, items):
        """

        :param id:
        :param items:
        :return:
        """
        if not id.get("id"):
            return False
        return self._set_dashboard_access(id.get("id"), items.get("items"), acc_limit="user")


# Install endpoints
BIAPI(router)
