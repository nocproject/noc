# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BI API
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.api import API, APIError, api, executor
from noc.core.clickhouse.model import Model
from noc.core.bi.models.reboots import Reboots


class BIAPI(API):
    """
    Monitoring API
    """
    name = "bi"

    # @todo: Replace with dynamic loading
    datasources = [
        Reboots
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
            r["fields"] += [{
                "name": f.name,
                "description": None,
                "type": f.db_type
            }]
        return r

    @api
    def query(self, datasource, filter, fields):
        """
        Perform query and return result
        :param datasource: Name of datasource
        :param filter:
        :param fields:
            List of dicts
            * name -- field name
            * expr -- Optional expression
            * alias
            * agg -- Aggregation function
        :return:
        """
        raise NotImplementedError()
