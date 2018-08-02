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
from .base import BaseReportColumn


class ReportObjectAttributes(BaseReportColumn):
    name = "attributes"
    unknown_value = ((None, None), )

    def extract(self):
        """
        :param ids:
        :return: Dict tuple MO attributes mo_id -> (attrs_list)
        :rtype: dict
        """
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
        for val in cursor:
            yield val[0], val[1:6]
