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
from noc.sa.models.profile import Profile
from noc.inv.models.vendor import Vendor
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware


class ReportAttrResolver(BaseReportColumn):
    name = "reportattrresolver"
    unknown_value = ["", "", "", ""]

    ATTRS = ["profile", "vendor", "version", "platform"]

    def extract(self):
        """
        :param ids:
        :return: Dict tuple MO attributes mo_id -> (attrs_list)
        :rtype: dict
        """
        platform = {
            str(p["_id"]): p["name"]
            for p in Platform.objects.all().as_pymongo().scalar("id", "name")
        }
        vendor = {
            str(p["_id"]): p["name"] for p in Vendor.objects.all().as_pymongo().scalar("id", "name")
        }
        version = {
            str(p["_id"]): p["version"]
            for p in Firmware.objects.all().as_pymongo().scalar("id", "version")
        }
        profile = {
            str(p["_id"]): p["name"]
            for p in Profile.objects.all().as_pymongo().scalar("id", "name")
        }

        cursor = connection.cursor()
        base_select = "select id, profile, vendor, platform, version from sa_managedobject"
        query1 = base_select
        query = query1

        cursor.execute(query)
        for val in cursor:
            yield (
                val[0],
                profile.get(val[1], ""),
                vendor.get(val[2], ""),
                platform.get(val[3], ""),
                version.get(val[4], ""),
            )
