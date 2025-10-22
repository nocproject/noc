# ----------------------------------------------------------------------
# ReportObjectAttrubuteResolver datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import connection

# NOC modules
from .base import BaseReportColumn


class ReportObjectAttributes(BaseReportColumn):
    name = "attributes"
    unknown_value = ((None, None, None, None),)
    builtin_sorted = True

    def extract(self):
        """
        :param ids:
        :return: Dict tuple MO attributes mo_id -> (attrs_list)
        :rtype: dict
        """
        attr_list = ["Serial Number", "HW version", "Boot PROM", "Patch Version"]
        cursor = connection.cursor()

        base_select = "select %s "
        base_select += (
            "from (select distinct managed_object_id from sa_managedobjectattribute) as saa "
        )

        value_select = "LEFT JOIN (select managed_object_id,value from sa_managedobjectattribute where key='%s') "
        value_select += "as %s on %s.managed_object_id=saa.managed_object_id"

        s = ["saa.managed_object_id"]
        s.extend([".".join([al.replace(" ", "_"), "value"]) for al in attr_list])

        query1 = base_select % ", ".join(tuple(s))
        query2 = " ".join(
            [value_select % (al, al.replace(" ", "_"), al.replace(" ", "_")) for al in attr_list]
        )
        query = query1 + query2 + " ORDER BY saa.managed_object_id"
        cursor.execute(query)
        for val in cursor:
            yield val[0], val[1:7]
