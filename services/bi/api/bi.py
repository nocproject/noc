# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BI API
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import zlib
## Third-party modules
import ujson
from mongoengine.queryset import Q
## NOC modules
from noc.core.service.api import API, APIError, api, executor
from noc.core.clickhouse.model import Model
from noc.core.bi.models.reboots import Reboots
from noc.core.bi.models.alarms import Alarms
from noc.bi.models.dashboard import Dashboard
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
                "description": f.description,
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
        parents = {}
        r = []
        for row in result["result"]:
            names = map((lambda z: z), row[0].strip("[] ").split(","))
            ids = map((lambda z: int(z)), row[1].strip("[] ").split(","))
            x = 1
            while x < len(ids) - 1:
                parents[ids[x]] = {"name": names[x], "id": ids[x], "p_id": ids[x + 1]}
                x += 1
            if len(ids) > 1:
                r.append({"name": names[0], "id": ids[0], "p_id": ids[1]})
            parents['root'] = {"name": names[-1], "id": ids[-1], "p_id": "null"}
        for k in parents:
            r.append(parents[k])
        return r
