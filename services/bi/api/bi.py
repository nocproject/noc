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
## NOC modules
from noc.core.service.api import API, APIError, api, executor
from noc.core.clickhouse.model import Model
from noc.core.bi.models.reboots import Reboots
from noc.core.bi.models.alarms import Alarms
from noc.bi.models.dashboard import Dashboard


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
                "description": None,
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
        return model.query(query)

    def get_user(self):
        return self.handler.current_user.username

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
        return [{
            "id": str(d.id),
            "title": str(d.title),
            "description": str(d.description),
            "tags": str(d.tags),
            "owner": d.owner,
            "created": d.created.isoformat(),
            "changed": d.changed.isoformat()
        } for d in Dashboard.objects
#                   .filter(owner=self.get_user())
                    .exclude("config")]

    def _get_dashboard(self, id):
        """
        Returns dashboard or None
        :param id:
        :return:
        """
        return Dashboard.objects.filter(
#           owner=self.get_user(),
            id=id
        ).first()

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
            d = self._get_dashboard(config["id"])
            if not d:
                raise APIError("Dashboard not found")
        else:
            d = Dashboard(owner=self.get_user())
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
        d = self._get_dashboard(id)
        if d:
            d.delete()
        else:
            raise APIError("Dashboard not found")
