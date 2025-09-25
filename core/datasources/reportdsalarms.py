# ----------------------------------------------------------------------
# ReportDsAlarms datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import operator
from typing import List, Iterable, Dict, Any, Optional, Tuple, AsyncIterable

# Third-party modules
import bson
import cachetools
from pymongo import ReadPreference


# NOC modules
from .base import BaseDataSource, FieldInfo, ParamInfo, FieldType
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
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.services.web.apps.fm.alarm.views import AlarmApplication


class ReportDsAlarms(BaseDataSource):
    name = "reportdsalarms"
    row_index = "alarm_id"

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    params = [
        ParamInfo(name="start", type="datetime", required=True),
        ParamInfo(name="end", type="datetime"),
        ParamInfo(name="source", type="str", default="active"),
        ParamInfo(name="objectids", type="int", allow_multi=True),
        ParamInfo(name="segment", type="str", model="inv.NetworkSegment"),
        ParamInfo(name="alarm_class", type="str", model="fm.AlarmClass"),
        ParamInfo(name="resource_group", type="str", model="inv.ResourceGroup"),
        ParamInfo(name="ex_resource_group", type="str", model="inv.ResourceGroup"),
        ParamInfo(name="min_duration", type="int"),
        ParamInfo(name="max_duration", type="int"),
        ParamInfo(name="min_objects", type="int"),
        ParamInfo(name="min_subscribers", type="int"),
    ]

    fields: List[FieldInfo] = [
        FieldInfo(
            name="alarm_id",
            # label="Alarm Id",
            description="Идентификатор аварии",
        ),
        FieldInfo(
            name="root_id",
            # label="Alarm Root",
            description="Первопричина",
        ),
        FieldInfo(
            name="from_ts",
            # label="FROM_TS",
            description="Время начала",
        ),
        FieldInfo(
            name="to_ts",
            # label="TO_TS",
            description="Время окончания",
        ),
        FieldInfo(
            name="duration_sec",
            # label="DURATION_SEC",
            description="Продолжительность (сек)",
            type=FieldType.UINT,
        ),
        FieldInfo(
            name="object_name",
            # label="OBJECT_NAME",
            description="Имя устройства",
        ),
        FieldInfo(
            name="object_address",
            # label="OBJECT_ADDRESS",
            description="IP Адрес",
        ),
        FieldInfo(
            name="object_hostname",
            # label="OBJECT_HOSTNAME",
            description="Hostname устройства",
        ),
        FieldInfo(
            name="object_profile",
            # label="OBJECT_PROFILE",
            description="Профиль",
        ),
        FieldInfo(
            name="object_object_profile",
            # label="OBJECT_OBJECT_PROFILE",
            description="Профиль объекта",
        ),
        FieldInfo(
            name="object_admdomain",
            # label="OBJECT_ADMDOMAIN",
            description="Зона ответственности",
        ),
        FieldInfo(
            name="object_platform",
            # label="OBJECT_PLATFORM",
            description="Платформа",
        ),
        FieldInfo(
            name="object_version",
            # label="OBJECT_VERSION",
            description="Версия",
        ),
        FieldInfo(
            name="object_project",
            # label="OBJECT_PROJECT",
            description="Проект",
        ),
        FieldInfo(
            name="alarm_class",
            # label="ALARM_CLASS",
            description="Класс аварии",
        ),
        FieldInfo(
            name="alarm_subject",
            # label="ALARM_SUBJECT",
            description="Тема",
        ),
        FieldInfo(
            name="maintenance",
            # label="MAINTENANCE",
            description="Активный РНР",
        ),
        FieldInfo(
            name="objects",
            # label="OBJECTS",
            description="Число задетых устройства",
            type=FieldType.UINT,
        ),
        FieldInfo(
            name="subscribers",
            # label="SUBSCRIBERS",
            description="Абоненты",
            type=FieldType.UINT,
        ),
        FieldInfo(
            name="tt",
            # label="TT",
            description="Номер ТТ",
        ),
        FieldInfo(
            name="escalation_ts",
            # label="ESCALATION_TS",
            description="Время эскалации",
        ),
        FieldInfo(
            name="location",
            # label="LOCATION",
            description="Месторасположение",
        ),
    ]

    _object_location_cache = cachetools.TTLCache(maxsize=1000, ttl=600)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_object_location_cache"))
    def get_object_location(cls, oid: str) -> str:
        loc = AlarmApplication(None)
        return ", ".join(loc.location(oid))

    @classmethod
    def _clear_caches(cls):
        cls._object_location_cache.clear()
        Object._id_cache.clear()
        Platform._id_cache.clear()
        Profile._id_cache.clear()
        Firmware._id_cache.clear()
        AlarmClass._id_cache.clear()

    @classmethod
    def items_to_dict(cls, items):
        """
        Convert a list of summary items to dict profile -> summary
        """
        return {r["profile"]: r["summary"] for r in items}

    @classmethod
    def iter_ds_fields(cls):
        yield from super().iter_ds_fields()

        for sp in SubscriberProfile.objects.filter(show_in_summary=True).order_by("name"):
            yield FieldInfo(name=f"subsprof_{sp.name}")  # label=sp.name.upper())
        for i in range(cls.CONTAINER_PATH_DEPTH):
            yield FieldInfo(
                name=f"container_{i}",
                # label=f"CONTAINER_{i}",
                description=f"Контейнер (Уровень {i + 1})",
            )
        for i in range(cls.SEGMENT_PATH_DEPTH):
            yield FieldInfo(
                name=f"segment_{i}",  # label=f"SEGMENT_{i}",
                description=f"Сегмент (Уровень {i + 1})",
            )

    @classmethod
    def iter_data(
        cls,
        start: datetime.datetime,
        end: Optional[datetime.datetime],
        admin_domain_ads: Optional[List[int]] = None,
        **filters: Optional[Dict[str, Any]],
    ) -> Iterable[Dict[str, Any]]:
        if "objectids" in filters:
            match = {"_id": {"$in": [bson.ObjectId(x) for x in filters["objectids"]]}}
        elif not end:
            match = {"timestamp": {"$gte": start}}
        else:
            match = {"timestamp": {"$gte": start, "$lte": end}}
        match_middle, mos_filter, ex_resource_group = {}, {}, None
        datenow = datetime.datetime.now()
        alarm_collections = []
        match_duration = {}
        # Administrative domain filter
        if not admin_domain_ads and admin_domain_ads is not None:
            raise ValueError(
                "<html><body>Permission denied: Not have permission to selected Administrative Domain</html></body>"
            )
        elif admin_domain_ads:
            match["adm_path"] = {"$in": list(admin_domain_ads)}
            mos_filter["administrative_domain__in"] = list(admin_domain_ads)
        # Main filters
        for name, values in filters.items():
            if not isinstance(values, list):
                values = [values]
            value = values[0]
            if name == "source":
                if "active" in values or "both" in values:
                    alarm_collections += [ActiveAlarm]
                if "archived" in values or "both" in values:
                    alarm_collections += [ArchivedAlarm]
                if not alarm_collections:
                    raise ValueError("alarm_collections must be not empty")
            elif name == "min_subscribers":
                match_middle["total_subscribers_sum.sum"] = {"$gte": int(value)}
            elif name == "min_objects":
                match_middle["total_objects_sum.sum"] = {"$gte": int(value)}
            elif name == "min_duration":
                match_duration["$gte"] = int(value)
            elif name == "max_duration" and int(value) > 0:
                match_duration["$lte"] = int(value)
            elif name == "alarm_class":
                match["alarm_class"] = bson.ObjectId(value)
            elif name == "segment":
                match["segment_path"] = value.id
            elif name == "resource_group":
                mos_filter["effective_service_groups__overlap"] = ResourceGroup.get_nested_ids(
                    value
                )
            if name == "ex_resource_group":
                ex_resource_group = value
        if match_duration:
            match_middle["duration"] = match_duration
        if mos_filter:
            mos = ManagedObject.objects.filter(is_managed=True).filter(**mos_filter)
            if ex_resource_group:
                mos = mos.exclude(
                    effective_service_groups__overlap=ResourceGroup.get_nested_ids(
                        ex_resource_group
                    )
                )
            match["managed_object"] = {
                "$in": list(mos.values_list("id", flat=True)),
                "$exists": True,
            }
        for coll in alarm_collections:
            # if isinstance(coll, ActiveAlarm):
            pipeline = []
            if match:
                pipeline += [{"$match": match}]
            pipeline += [
                # {
                #     "$lookup": {
                #         "from": "noc.objects",
                #         "localField": "container_path",
                #         "foreignField": "_id",
                #         "as": "container_path_l",
                #     }
                # },
                # {
                #     "$lookup": {
                #         "from": "noc.networksegments",
                #         "localField": "segment_path",
                #         "foreignField": "_id",
                #         "as": "segment_path_l",
                #     }
                # },
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
                        # "container_path_l": {
                        #     "$map": {"input": "$container_path_l", "as": "cc", "in": "$$cc.name"}
                        # },
                        "container_path_l": [],
                        # "segment_path_l": {
                        #     "$map": {"input": "$segment_path_l", "as": "ns", "in": "$$ns.name"}
                        # },
                    }
                },
            ]
            if match_middle:
                pipeline += [{"$match": match_middle}]

            # print(pipeline, alarm_collections)
            for row in (
                coll._get_collection()
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(pipeline)
            ):
                yield row

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, str]]:
        if "start" not in kwargs:
            raise ValueError("Start filter is required")
        moss = {
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
        fields = fields or []
        mo_hostname = {}
        if not fields or "object_hostname" in fields:
            mo_hostname = {
                val["object"]: val["hostname"]
                for val in DiscoveryID._get_collection()
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .find({"hostname": {"$exists": 1}}, {"object": 1, "hostname": 1})
            }
        maintenance = {}
        # if "maintenance" in fields:
        #     maintenance = Maintenance.currently_affected()
        if fields:
            container_path_fields = [field for field in fields if field.startswith("container_")]
        else:
            container_path_fields = [
                field.name for field in cls.iter_ds_fields() if field.name.startswith("container_")
            ]
        if fields:
            segment_path_fields = [field for field in fields if field.startswith("segment_")]
        else:
            segment_path_fields = [
                field.name for field in cls.iter_ds_fields() if field.name.startswith("segment_")
            ]
        subscribers_profile = []
        if not fields or "subscribers" in fields:
            subscribers_profile = [
                sp
                for sp in SubscriberProfile.objects.filter(show_in_summary=True)
                .values_list("name", "id")
                .order_by("name")
            ]
        for row_num, aa in enumerate(cls.iter_data(**kwargs), start=1):
            if "managed_object" not in aa:
                continue
            mo = moss[aa["managed_object"]]
            loc = ""
            if (not fields or "location" in fields) and aa.get("container_path"):
                loc = cls.get_object_location(aa["container_path"][-1])
            platform, version, project = None, None, None
            if mo["platform"]:
                platform = Platform.get_by_id(mo["platform"]).name
            if mo["project"]:
                project = Project.get_by_id(mo["project"]).name
            if mo["version"]:
                version = Firmware.get_by_id(mo["version"]).version

            yield row_num, "alarm_id", str(aa["_id"])
            yield row_num, "root_id", str(aa["root"]) if aa.get("root") else ""
            yield row_num, "from_ts", aa["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            yield (
                row_num,
                "to_ts",
                (
                    aa["clear_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                    if "clear_timestamp" in aa
                    else ""
                ),
            )
            yield row_num, "duration_sec", round(aa["duration"])
            yield row_num, "object_name", mo["name"]
            yield row_num, "object_address", mo["address"]
            yield row_num, "object_hostname", mo_hostname.get(aa["managed_object"], "")
            yield row_num, "object_profile", Profile.get_by_id(mo["profile"]).name
            yield row_num, "object_object_profile", mo["object_profile__name"]
            yield row_num, "object_admdomain", mo["administrative_domain__name"]
            yield row_num, "object_platform", platform
            yield row_num, "object_version", version
            yield row_num, "object_project", project
            yield row_num, "alarm_class", AlarmClass.get_by_id(aa["alarm_class"]).name
            yield row_num, "alarm_subject", ""
            yield row_num, "objects", aa["total_objects_sum"]["sum"]
            yield row_num, "subscribers", aa["total_subscribers_sum"]["sum"]
            yield row_num, "tt", aa.get("escalation_tt")
            yield (
                row_num,
                "escalation_ts",
                (
                    aa["escalation_ts"].strftime("%Y-%m-%d %H:%M:%S")
                    if "escalation_ts" in aa
                    else ""
                ),
            )
            yield row_num, "location", loc
            yield (
                row_num,
                "maintenance",
                (
                    "Yes"
                    if "clear_timestamp" not in aa and aa["managed_object"] in maintenance
                    else "No"
                ),
            )

            for sp_name, sp_id in subscribers_profile:
                dd = cls.items_to_dict(aa["total_subscribers"])
                yield row_num, f"subsprof_{sp_name}", dd.get(sp_id, "")

            for field in container_path_fields:
                _, index = field.split("_")
                v, index = "", int(index)
                if index < len(aa["container_path"]):
                    o = Object.get_by_id(aa["container_path"][index])
                    if o:
                        v = o.name
                yield row_num, field, v

            for field in segment_path_fields:
                _, index = field.split("_")
                v, index = "", int(index)
                if index < len(aa["segment_path"]):
                    o = NetworkSegment.get_by_id(aa["segment_path"][index])
                    if o:
                        v = o.name
                yield row_num, field, v

        cls._clear_caches()
