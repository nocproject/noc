# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportObjectAttrubuteResolver datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from django.db import connection
# NOC modules
from .base import BaseReportDataSource


class ReportObjectAttributes(BaseReportDataSource):

    UNKNOWN = ["", ""]

    @staticmethod
    def load(ids, attributes):
        """
        :param ids:
        :return: Dict tuple MO attributes mo_id -> (attrs_list)
        :rtype: dict
        """
        mo_attrs = {}
        attr_list = ["Serial Number", "HW version"]
        cursor = connection.cursor()

        base_select = "select %s "
        base_select += "from (select distinct managed_object_id from sa_managedobjectattribute) as saa "

        value_select = "LEFT JOIN (select managed_object_id,value from sa_managedobjectattribute where key='%s') "
        value_select += "as %s on %s.managed_object_id=saa.managed_object_id"

        s = ["saa.managed_object_id"]
        s.extend([".".join([al.replace(" ", "_"), "value"]) for al in attr_list])

        query1 = base_select % ", ".join(tuple(s))
        query2 = " ".join([value_select % tuple([al, al.replace(" ", "_"), al.replace(" ", "_")]) for al in attr_list])
        query = query1 + query2
        cursor.execute(query)
        mo_attrs.update(dict([(c[0], c[1:6]) for c in cursor]))

        return mo_attrs
