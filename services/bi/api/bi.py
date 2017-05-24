# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# BI API
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import zlib
# Third-party modules
import ujson
from mongoengine.queryset import Q
# NOC modules
from noc.core.service.api import API, APIError, api, executor
from noc.core.clickhouse.model import Model
from noc.bi.models.reboots import Reboots
from noc.bi.models.alarms import Alarms
from noc.bi.models.dashboard import Dashboard
from noc.core.translation import ugettext as _
from noc.lib.nosql import get_db


class BIAPI(API):
    """
    Monitoring API
    """
    name = "bi"

    # @todo: Replace with dynamic loading
    datasources = [
        Reboots,
        Alarms
    ]

    def iter_datasources(self):
        """
        @todo: Dynamic loading
        @todo: Load from custom/
        :return:
        """
        for ds in self.datasources:
            yield ds

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
            {
                "name": ds._meta.db_table,
                "decscription": ds._meta.description,
                "tags": ds._meta.tags
            } for ds in self.iter_datasources()
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
        model = Model.get_model_class(name)
        if not model:
            raise APIError("Invalid datasource")
        r = {
            "name": model._meta.db_table,
            "description": model._meta.description,
            "tags": model._meta.tags,
            "fields": []
        }
        for fn in model._fields_order:
            f = model._fields[fn]
            d = getattr(f, "dict_type", None)
            if d:
                d = d._meta.name
            r["fields"] += [{
                "name": f.name,
                "description": _(f.description),
                "type": f.db_type,
                "dict": d
            }]
        return r

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
            raise APIError("No datasource")
        model = Model.get_model_class(query["datasource"])
        if not model:
            raise APIError("Invalid datasource")
        return model.query(query, self.handler.current_user)

    @executor("query")
    @api
    def list_dashboards(self, q=None):
        """
        Returns list of user dashboards. Each item is a dict of
        * id
        * title
        * description
        * tags
        * owner
        * created
        * changed
        @todo: Access control
        :param q:
        :return:
        """
        user = self.handler.current_user
        # @todo: Filter by groups
        aq = Q(owner=user.id) | Q(access__user=user.id)
        return [{
                    "id": str(d.id),
                    "title": str(d.title),
                    "description": str(d.description),
                    "tags": str(d.tags),
                    "owner": d.owner.username,
                    "created": d.created.isoformat(),
                    "changed": d.changed.isoformat()
                } for d in Dashboard.objects
                    .filter(aq)
                    .exclude("config")]

    def _get_dashboard(self, id, access_level=0):
        """
        Returns dashboard or None
        :param id:
        :return:
        """
        user = self.handler.current_user
        d = Dashboard.objects.filter(id=id).first()
        if not d:
            return None
        if d.owner == user:
            return d
        # @todo: Filter by groups
        for i in d.access:
            if i.user == user and i.level >= access_level:
                return d
        # No access
        return None

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
            return ujson.loads(zlib.decompress(d.config))
        else:
            return None

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
                raise APIError("Dashboard not found")
        else:
            d = Dashboard(owner=self.handler.current_user)
        d.format = config.get("format", 1)
        d.config = zlib.compress(ujson.dumps(config))
        d.changed = datetime.datetime.now()
        d.title = config.get("title")  # @todo: Generate title
        d.description = config.get("description")
        d.tags = config.get("tags", [])
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
        else:
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
            else:
                if node and "children" in node.keys():
                    for child in node["children"]:
                        _searched = search_parent(child, p_id)
                        if _searched:
                            return _searched
                else:
                    return None

        def sort_children(node):
            if "children" not in node.keys():
                return
            else:
                node["children"] = sorted(node["children"], key=lambda x: x["text"])
                for n in node["children"]:
                    sort_children(n)

        if "datasource" not in params:
            raise APIError("No datasource")
        if "dic_name" not in params:
            raise APIError("No dictionary name")
        if "field_name" not in params:
            raise APIError("No field name")
        model = Model.get_model_class(params["datasource"])
        if not model:
            raise APIError("Invalid datasource")
        query = {
            "fields": [
                {
                    "expr": {
                        "$names": [
                            params["dic_name"],
                            params["field_name"]
                        ]
                    },
                    "alias": "names"
                },
                {
                    "expr": {
                        "$hierarchy": [
                            params["dic_name"],
                            {
                                "$field": params["field_name"]
                            }
                        ]
                    },
                    "alias": "ids"
                },
                {
                    "expr": params["field_name"],
                    "group": 0
                }
            ],
            "datasource": params["datasource"]
        }
        if "limit" in params:
            query["limit"] = params["limit"]
        if "filter" in params:
            query["filter"] = {
                "$like": [
                    {
                        "$lower": {
                            "$field": "arrayElement(names,1)"
                        }
                    },
                    {
                        "$lower": "%" + params["filter"] + "%"
                    }
                ]
            }

        result = model.query(query, self.handler.current_user)
        tree = {}
        for row in result["result"]:
            names = map(lambda x: x[1:-1], row[0][1:-1].split(","))
            ids = map(lambda x: int(x), row[1][1:-1].split(","))
            ids.reverse()
            names.reverse()
            parent_id = None
            for col in zip(ids, names):
                searched = search_parent(tree, parent_id)
                parent_id = col[0]
                if searched:
                    if searched["id"] != col[0]:
                        if "children" not in searched.keys():
                            searched["children"] = []
                        if not col[0] in map(lambda x: x["id"], searched["children"]):
                            searched["children"].append({"id": col[0], "text": col[1]})
                else:  # start point
                    tree = {"id": col[0], "text": col[1], "children": []}

        sort_children(tree)
        return tree
