# ----------------------------------------------------------------------
# ReportDsAlarms datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable, Dict, Any
import datetime

# Third-party modules
import bson
from pymongo import ReadPreference

# NOC modules
from .base import ReportDataSource, ReportField
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.object import Object
from noc.inv.models.networksegment import NetworkSegment
from noc.project.models.project import Project
from noc.maintenance.models.maintenance import Maintenance
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.services.web.apps.fm.alarm.views import AlarmApplication


class ReportDsAlarms(ReportDataSource):
    name = "reportdsalarms"

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    FIELDS: List[ReportField] = (
        [
            ReportField(
                name="alarm_id",
                label="Alarm Id",
                description="Идентификатор аварии",
            ),
            ReportField(
                name="root_id",
                label="Alarm Root",
                description="Первопричина",
            ),
            ReportField(
                name="from_ts",
                label="FROM_TS",
                description="Время начала",
            ),
            ReportField(
                name="to_ts",
                label="TO_TS",
                description="Время окончания",
            ),
            ReportField(
                name="duration_sec",
                label="DURATION_SEC",
                description="Продолжительность (сек)",
            ),
            ReportField(
                name="object_name",
                label="OBJECT_NAME",
                description="Имя устройства",
            ),
            ReportField(
                name="object_address",
                label="OBJECT_ADDRESS",
                description="IP Адрес",
            ),
            ReportField(
                name="object_hostname",
                label="OBJECT_HOSTNAME",
                description="Hostname устройства",
            ),
            ReportField(
                name="object_profile",
                label="OBJECT_PROFILE",
                description="Профиль",
            ),
            ReportField(
                name="object_object_profile",
                label="OBJECT_OBJECT_PROFILE",
                description="Профиль объекта",
            ),
            ReportField(
                name="object_admdomain",
                label="OBJECT_ADMDOMAIN",
                description="Зона ответственности",
            ),
            ReportField(
                name="object_platform",
                label="OBJECT_PLATFORM",
                description="Платформа",
            ),
            ReportField(
                name="object_version",
                label="OBJECT_VERSION",
                description="Версия",
            ),
            ReportField(
                name="object_project",
                label="OBJECT_PROJECT",
                description="Проект",
            ),
            ReportField(
                name="alarm_class",
                label="ALARM_CLASS",
                description="Класс аварии",
            ),
            ReportField(
                name="alarm_subject",
                label="ALARM_SUBJECT",
                description="Тема",
            ),
            ReportField(
                name="maintenance",
                label="MAINTENANCE",
                description="Активный РНР",
            ),
            ReportField(
                name="objects",
                label="OBJECTS",
                description="Число задетых устройства",
            ),
            ReportField(
                name="subscribers",
                label="SUBSCRIBERS",
                description="Абоненты",
            ),
            ReportField(
                name="tt",
                label="TT",
                description="Номер ТТ",
            ),
            ReportField(
                name="escalation_ts",
                label="ESCALATION_TS",
                description="Время эскалации",
            ),
            ReportField(
                name="location",
                label="LOCATION",
                description="Месторасположение",
            ),
            ReportField(
                name="container_address",
                label="CONTAINER_ADDRESS",
                description="Месторасположение",
            ),
        ]
        + [
            ReportField(name=f"subsprof_{sp.name}", label=sp.name.upper())
            for sp in SubscriberProfile.objects.filter(show_in_summary=True).order_by("name")
        ]
        + [
            ReportField(
                name=f"container_{i}",
                label=f"CONTAINER_{i}",
                description=f"Контейнер (Уровень {i + 1})",
            )
            for i in range(CONTAINER_PATH_DEPTH)
        ]
        + [
            ReportField(
                name=f"segment_{i}", label=f"SEGMENT_{i}", description=f"Сегмент (Уровень {i + 1})"
            )
            for i in range(SEGMENT_PATH_DEPTH)
        ]
    )

    @classmethod
    def items_to_dict(cls, items):
        """
        Convert a list of summary items to dict profile -> summary
        """
        return {r["profile"]: r["summary"] for r in items}

    @classmethod
    def get_fields(cls, fields):
        r = super().get_fields(fields)
        if "subscribers" in fields:
            for f in cls.FIELDS:
                if f.name.startswith("subsprof_"):
                    r[f.name] = f
        return r

    def iter_data(self) -> Iterable[Dict[str, Any]]:
        if self.objectids:
            match = {"_id": {"$in": [bson.ObjectId(x) for x in self.objectids]}}
        else:
            match = {"timestamp": {"$gte": self.start, "$lte": self.end}}
        match_duration, mos_filter, ex_resource_group = {}, {}, None
        datenow = datetime.datetime.now()
        alarm_collections = []

        for ff in self.filters:
            name, values = ff["name"], ff["values"]
            if name == "source":
                if "active" in values or "both" in values:
                    alarm_collections += [ActiveAlarm]
                if "archive" in values or "both" in values:
                    alarm_collections += [ArchivedAlarm]
            elif name == "min_subscribers":
                match_duration["total_subscribers_sum.sum"] = {"$gte": int(values[0])}
            elif name == "min_objects":
                match_duration["total_objects_sum.sum"] = {"$gte": int(values[0])}
            elif name == "min_duration":
                match_duration["duration"] = {"$gte": int(values[0])}
            elif name == "max_duration":
                if "duration" in match_duration:
                    match_duration["duration"]["$lte"] = int(values[0])
                else:
                    match_duration["duration"] = {"$lte": int(values[0])}
            elif name == "alarm_class":
                match["alarm_class"] = bson.ObjectId(values[0])
            elif name == "adm_path":
                match["adm_path"] = {"$in": values}
                mos_filter["administrative_domain__in"] = values
            elif name == "segment":
                match["segment_path"] = bson.ObjectId(values[0])
            elif name == "resource_group":
                resource_group = ResourceGroup.get_by_id(values[0])
                mos_filter["effective_service_groups__overlap"] = ResourceGroup.get_nested_ids(
                    resource_group
                )
            if name == "ex_resource_group":
                ex_resource_group = ResourceGroup.get_by_id(values[0])

        if mos_filter:
            mos = ManagedObject.objects.filter(is_managed=True).filter(**mos_filter)
            if ex_resource_group:
                mos = mos.exclude(
                    effective_service_groups__overlap=ResourceGroup.get_nested_ids(
                        ex_resource_group
                    )
                )
            match["managed_object"] = {"$in": list(mos.values_list("id", flat=True))}
        for coll in alarm_collections:
            # if isinstance(coll, ActiveAlarm):
            pipeline = []
            if match:
                pipeline += [{"$match": match}]
            pipeline += [
                {
                    "$addFields": {
                        "duration": {
                            "$divide": [
                                {
                                    "$subtract": [
                                        "$clear_timestamp" if coll is ArchivedAlarm else datenow,
                                        "$timestamp",
                                    ]
                                },
                                1000,
                            ]
                        },
                        "total_objects_sum": {
                            "$reduce": {
                                "input": "$total_objects",
                                "initialValue": {"sum": 0},
                                "in": {"sum": {"$add": ["$$value.sum", "$$this.summary"]}},
                            }
                        },
                        "total_subscribers_sum": {
                            "$reduce": {
                                "input": "$total_subscribers",
                                "initialValue": {"sum": 0},
                                "in": {"sum": {"$add": ["$$value.sum", "$$this.summary"]}},
                            }
                        },
                    }
                },
            ]
            if match_duration:
                pipeline += [{"$match": match_duration}]

            # print(pipeline, alarm_collections)
            for row in (
                coll._get_collection()
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(pipeline)
            ):
                yield row

    def extract(self) -> Iterable[Dict[str, int]]:
        # moss = MOCache()
        self._moss = {
            mo["id"]: mo
            for mo in ManagedObject.objects.filter().values(
                "id",
                "name",
                "address",
                "profile",
                "object_profile__name",
                "administrative_domain__name",
                "platform",
                "version",
                "project",
            )
        }

        self._mo_hostname = {}
        if "object_hostname" in self.fields:
            self._mo_hostname = {
                val["object"]: val["hostname"]
                for val in DiscoveryID._get_collection()
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .find({"hostname": {"$exists": 1}}, {"object": 1, "hostname": 1})
            }
        maintenance = {}
        if "maintenance" in self.fields:
            maintenance = Maintenance.currently_affected()
        loc = None
        if "location" in self.fields:
            loc = AlarmApplication([])
        container_path_fields = [field for field in self.fields if field.startswith("container_")]
        segment_path_fields = [field for field in self.fields if field.startswith("segment_")]
        subscribers_profile = []
        if "subscribers" in self.fields:
            subscribers_profile = [
                (sp.name, sp.id)
                for sp in SubscriberProfile.objects.filter(show_in_summary=True).order_by("name")
            ]
        for aa in self.iter_data():
            mo = self._moss[aa["managed_object"]]
            platform, version, project = None, None, None
            if mo["platform"]:
                platform = Platform.get_by_id(mo["platform"]).name
            if mo["project"]:
                project = Project.get_by_id(mo["project"]).name
            if mo["version"]:
                version = Firmware.get_by_id(mo["version"]).version
            r = {
                "alarm_id": str(aa["_id"]),
                "root_id": str(aa["root"]) if aa.get("root") else "",
                "from_ts": aa["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                "to_ts": (
                    aa["clear_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                    if "clear_timestamp" in aa
                    else ""
                ),
                "duration_sec": round(aa["duration"]),
                "object_name": mo["name"],
                "object_address": mo["address"],
                "object_hostname": self._mo_hostname.get(aa["managed_object"], ""),
                "object_profile": Profile.get_by_id(mo["profile"]).name,
                "object_object_profile": mo["object_profile__name"],
                "object_admdomain": mo["administrative_domain__name"],
                "object_platform": platform,
                "object_version": version,
                "object_project": project,
                "alarm_class": AlarmClass.get_by_id(aa["alarm_class"]).name,
                "alarm_subject": "",
                "objects": aa["total_objects_sum"]["sum"],
                "subscribers": aa["total_subscribers_sum"]["sum"],
                "tt": aa.get("escalation_tt"),
                "escalation_ts": (
                    aa["escalation_ts"].strftime("%Y-%m-%d %H:%M:%S")
                    if "escalation_ts" in aa
                    else ""
                ),
                "location": (
                    ", ".join(
                        ll
                        for ll in (
                            loc.location(aa["container_path"][-1])
                            if aa.get("container_path")
                            else ""
                        )
                        if ll
                    )
                    if loc
                    else ""
                ),
                "maintenance": (
                    "Yes"
                    if "clear_timestamp" not in aa and aa["managed_object"] in maintenance
                    else "No"
                ),
                "container_address": "",
            }
            for sp_name, sp_id in subscribers_profile:
                dd = self.items_to_dict(aa["total_subscribers"])
                r[f"subsprof_{sp_name}"] = dd.get(sp_id, "")

            for field in container_path_fields:
                _, index = field.split("_")
                v, index = "", int(index)
                if index < len(aa["container_path"]):
                    o = Object.get_by_id(aa["container_path"][index])
                    if o:
                        v = o.name
                r[field] = v

            for field in segment_path_fields:
                _, index = field.split("_")
                v, index = "", int(index)
                if index < len(aa["segment_path"]):
                    o = NetworkSegment.get_by_id(aa["segment_path"][index])
                    if o:
                        v = o.name
                r[field] = v

            yield r
