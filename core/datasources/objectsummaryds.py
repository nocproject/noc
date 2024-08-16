# ----------------------------------------------------------------------
# Object Summary Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable, Union

# Third-party modules
from django.db import connection as pg_connection

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.profile import Profile
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.inv.models.firmwarepolicy import FirmwarePolicy

fp_map = {
    "r": "Recommended",
    "a": "Acceptable",
    "n": "Not recommended",
    "d": "Denied",
}


class ObjectSummaryDS(BaseDataSource):
    name = "objectsummaryds"

    fields = [
        FieldInfo(name="category", description="Category"),
        FieldInfo(name="quantity", description="Quantity", type=FieldType.UINT),
    ]

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, user=None, **kwargs
    ) -> AsyncIterable[Tuple[int, str, Union[str, int]]]:
        if "report_type" not in kwargs:
            raise ValueError("'report_type' parameter is required")
        report_type = kwargs.get("report_type")[0]

        wr = ("", "")
        wr_and = ("", "")
        platform = {
            str(p["_id"]): p["name"]
            for p in Platform.objects.all().as_pymongo().scalar("id", "name")
        }
        version = {str(p.id): p for p in Firmware.objects.all()}
        profile = {
            str(p["_id"]): p["name"]
            for p in Profile.objects.all().as_pymongo().scalar("id", "name")
        }
        if user and not user.is_superuser:
            ad = tuple(UserAccess.get_domains(user))
            wr = ("WHERE administrative_domain_id in ", ad)
            wr_and = ("AND administrative_domain_id in ", ad)
            if len(ad) == 1:
                wr = ("WHERE administrative_domain_id in (%s)" % ad, "")
                wr_and = ("AND administrative_domain_id in (%s)" % ad, "")
        # By Profile
        if report_type == "profile":
            query = (
                """SELECT profile, COUNT(*)
                    FROM sa_managedobject
                    %s%s GROUP BY 1 ORDER BY 2 DESC"""
                % wr
            )
        # By Administrative Domain
        elif report_type == "domain":
            query = (
                """SELECT a.name, COUNT(*)
                  FROM sa_managedobject o JOIN sa_administrativedomain a ON (o.administrative_domain_id=a.id)
                  %s%s
                  GROUP BY 1
                  ORDER BY 2 DESC"""
                % wr
            )
        # By Profile and Administrative Domains
        elif report_type == "domain-profile":
            query = (
                """SELECT d.name, profile, COUNT(*)
                    FROM sa_managedobject o JOIN sa_administrativedomain d ON (o.administrative_domain_id=d.id)
                    %s%s
                    GROUP BY 1, 2
                    ORDER BY 3 DESC"""
                % wr
            )
        # By Labels
        elif report_type == "label":
            query = (
                """SELECT t.label, COUNT(*)
                    FROM (
                      SELECT unnest(labels) AS label
                      FROM sa_managedobject
                      WHERE
                        labels IS NOT NULL
                        %s%s
                        AND array_length(labels, 1) > 0
                      ) t
                    GROUP BY 1
                    ORDER BY 2 DESC"""
                % wr_and
            )
        elif report_type == "platform":
            query = (
                """select sam.profile, sam.platform, COUNT(platform)
                    from sa_managedobject sam %s%s group by 1, 2 order by count(platform) desc"""
                % wr
            )
        elif report_type == "version":
            query = (
                """select sam.profile, sam.version, COUNT(version)
                    from sa_managedobject sam %s%s group by 1, 2 order by count(version) desc"""
                % wr
            )
        else:
            raise Exception("Invalid report type: %s" % report_type)

        with pg_connection.cursor() as cursor:
            cursor.execute(query, ())
            for num, c in enumerate(cursor.fetchall()):
                if report_type == "profile":
                    record = (profile.get(c[0]), c[1])
                elif report_type == "domain-profile":
                    record = (f"{c[0]} / {profile.get(c[1])}", c[2])
                elif report_type == "platform":
                    record = (f"{profile.get(c[0])} / {platform.get(c[1])}", c[2])
                elif report_type == "version":
                    fw, fps = version.get(c[1]), None
                    if fw:
                        try:
                            fps = FirmwarePolicy.get_status(fw)
                        except ValueError:
                            pass
                    record = (f"{profile.get(c[0])} / {fw} / {fp_map.get(fps, fps or '')}", c[2])
                else:
                    record = c
                yield num, "category", record[0]
                yield num, "quantity", record[1]
