# ---------------------------------------------------------------------
# inv.inv pconf plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any, Iterable
from enum import IntEnum, Enum
from dataclasses import dataclass
import uuid
from collections import defaultdict

# Third-party modules
import orjson
from pymongo.collection import Collection

# NOC modules
from noc.inv.models.object import Object, Crossing
from noc.sa.interfaces.base import StringParameter
from noc.sa.models.managedobject import ManagedObject
from noc.core.mongo.connection import get_db
from noc.main.models.extstorage import ExtStorage
from .base import InvPlugin

DEFAULT_GROUP = "Card"


class Status(Enum):
    """
    Threshold status.
    """

    UNKNOWN = "u"
    OK = "o"
    WARN = "w"
    CRITICAL = "c"


@dataclass
class Threshold(object):
    c_min: str | None = None
    w_min: str | None = None
    w_max: str | None = None
    c_max: str | None = None

    def to_json(self) -> list[str | None]:
        """Serialize to JSON"""
        return [self.c_min, self.w_min, self.w_max, self.c_max]

    def get_status(self, v: str) -> Status:
        """Calculate threshold status"""

        def to_float(x: str | None) -> float | None:
            if x is None:
                return None
            try:
                return float(x)
            except ValueError:
                return None

        # Convert value
        fv = to_float(v)
        if fv is None:
            return Status.UNKNOWN
        # c_min
        c_min = to_float(self.c_min)
        if c_min is not None and fv <= c_min:
            return Status.CRITICAL
        # w_min
        w_min = to_float(self.w_min)
        if w_min is not None and fv <= w_min:
            return Status.WARN
        # c_max
        c_max = to_float(self.c_max)
        if c_max is not None and fv >= c_max:
            return Status.CRITICAL
        # w_max
        w_max = to_float(self.w_max)
        if w_max is not None and fv >= w_max:
            return Status.WARN
        # ok
        return Status.OK


class Table(IntEnum):
    INFO = 1
    STATUS = 2
    CONFIG = 3
    THRESHOLD = 4


class Type(Enum):
    STRING = "string"
    ENUM = "enum"


@dataclass
class Item(object):
    """
    Configuration item
    """

    name: str
    value: str
    description: str = ""
    units: str = ""
    read_only: bool = False
    type: Type = Type.STRING
    table: Table | None = None
    group: str = DEFAULT_GROUP
    options: dict[str, str] | None = None
    thresholds: Threshold | None = None

    def to_json(self) -> dict[str, Any]:
        r = {
            "name": self.name,
            "value": self.value,
            "description": self.description,
            "units": self.units,
            "read_only": self.read_only,
            "type": self.type.value,
        }
        if self.options is not None:
            r["options"] = [{"id": k, "label": v} for k, v in self.options.items()]
        if self.thresholds is not None:
            r["thresholds"] = self.thresholds.to_json()
            r["status"] = self.thresholds.get_status(self.value).value
        return r

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "Item":
        # Determine type
        name = row["nam"]
        options = row.get("EM")
        t = row.get("typ")
        if options:
            dt = Type.ENUM
        elif t == 32:
            dt = Type.STRING
        else:
            dt = Type.STRING
        table = row.get("tbl", 1)
        value = row.get("val") or ""
        r = Item(
            name=name,
            value=value,
            description=row.get("dsc") or "",
            units=row.get("unt") or "",
            read_only=(row.get("acs") or "") != "W",
            type=dt,
            table=table,
        )
        if options:
            r.options = {x["val"]: x["dsc"] for x in options}
        return r


@dataclass
class ParsedData(object):
    groups: list[str]
    conf: list[Item]
    mgmt_url: str | None = None

    @classmethod
    def empty(cls) -> "ParsedData":
        return ParsedData(groups={}, conf=[])


H8_CT_UUID = uuid.UUID("4aa9afdc-7420-4dde-9727-2c3de1c3a8f4")
CU_UUID = uuid.UUID("1cde0558-d43d-4485-9be2-89f08d85ed61")
HS_UUID = uuid.UUID("1fd48ae6-df10-4ba4-ba72-1150fadbe6fe")


class PConfPlugin(InvPlugin):
    name = "pconf"
    js = "NOC.inv.inv.plugins.pconf.PConfPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            "f_api_plugin_{self.name}_data",
            self.api_data,
            url=f"^(?P<id>[0-9a-f]{{24}})/plugin/{self.name}/data/$",
            method=["GET"],
            validate={
                "t": StringParameter(default="1"),
                "g": StringParameter(default=DEFAULT_GROUP),
            },
        )
        self.add_view(
            f"api_plugin_{self.name}_set",
            self.api_set,
            url=f"^(?P<id>[0-9a-f]{{24}})/plugin/{self.name}/set/$",
            method=["POST"],
            validate={"name": StringParameter(), "value": StringParameter()},
        )

    def get_data(self, request, o: Object):
        def q_table(t: Table) -> dict[str, str | int]:
            r = {"id": t.value, "label": t.name.capitalize()}
            if t == Table.STATUS:
                r["autoreload"] = 3
            return r

        # Build sections
        data = self.fetch_data(o, table=Table.INFO, group=DEFAULT_GROUP)
        r = {
            "status": True,
            "tables": [
                q_table(x) for x in (Table.INFO, Table.STATUS, Table.CONFIG, Table.THRESHOLD)
            ],
            "groups": [{"id": x, "label": x} for x in data.groups],
            "conf": [x.to_json() for x in data.conf],
        }
        if data.mgmt_url:
            r["mgmt_url"] = data.mgmt_url
        return r

    def api_data(self, request, id: str, t: str, g: str) -> dict[str, Any]:
        obj = self.app.get_object_or_404(Object, id=id)
        try:
            tbl = Table(int(t))
        except ValueError:
            return self.app.response_not_found("Invalid table")
        data = self.fetch_data(obj, tbl, group=g)
        return {"status": True, "conf": [x.to_json() for x in data.conf]}

    def fetch_data(self, obj: Object, /, table: Table, group: str) -> ParsedData:
        mo = self.get_managed_object(obj)
        if mo:
            # Managed
            return self.parse_data(
                obj, mo.scripts.get_params(), table=table, group=group, address=mo.address
            )
        # Beef
        data = self.get_pconf_beef(obj)
        if data:
            return self.parse_data(obj, data, table=table, group=group)
        # Headless
        items = list(self.iter_headless(obj))
        return ParsedData(
            groups=list(set(i.group or DEFAULT_GROUP for i in items)),
            conf=[i for i in items if i.table == table and i.group == group],
        )

    @staticmethod
    def get_nvram_collection() -> Collection:
        """
        Get collection for NVRAM storage.

        Returns:
            Mongo collection instance.
        """
        return get_db()["pconf_nvram"]

    def get_nvram(self, obj: Object, defaults: dict[str, Any]) -> dict[str, Any]:
        """
        Get headless NVRAM config.

        Args:
            obj: Object instance.
            defailts: Map of defaults
        """
        coll = self.get_nvram_collection()
        data = coll.find_one({"_id": obj.id})
        cfg = defaults.copy()
        if data:
            d = data.get("config")
            if d:
                cfg.update(d)
        return cfg

    def set_nvram(self, obj: Object, name: str, value: Any) -> None:
        """
        Save config value to NVRAM.

        Args:
            obj: Object reference.
            name: Parameter name.
            value: Parameter value.
        """
        coll = self.get_nvram_collection()
        coll.update_one({"_id": obj.id}, {"$set": {f"config.{name}": value}}, upsert=True)

    def parse_data(
        self,
        obj: Object,
        data: dict[str, Any],
        /,
        table: Table,
        group: str,
        address: str | None = None,
    ) -> ParsedData:
        """
        Extract config for given slot and filters.

        Args:
            obj: Object reference.
            data: Input data.
            table: Current table.
            group: Current group.

        Returns:
            Parsed data
        """
        slot = self._get_card(obj)
        for item in data["RK"][0]["DV"]:
            s = item.get("slt")
            if not s:
                continue
            if s == slot:
                slot_cfg = item
                break
        else:
            return ParsedData.empty()

        conf: list[Item] = []
        pm = slot_cfg.get("PM")
        if not pm:
            return ParsedData.empty()
        # Groups
        g_map: dict[str, str] = {}  # param -> group
        groups: list[str] = [DEFAULT_GROUP]
        gm = slot_cfg.get("GM")
        if gm:
            for g in gm:
                gn = g["nam"]
                if gn:
                    groups.append(gn)
                    for v in g["val"]:
                        g_map[v] = gn
        # Parameters
        threholds: defaultdict[str, Threshold] = defaultdict(Threshold)
        for row in pm:
            name = row.get("nam")
            if not name:
                continue
            row_table = row.get("tbl", 1)
            row_group = g_map.get(name, "") or DEFAULT_GROUP
            if row_table == Table.THRESHOLD and table == Table.STATUS:
                # Get threshold
                value = row.get("val") or ""
                match name[-4:]:
                    case "CMin":
                        threholds[name[:-4]].c_min = value
                    case "WMin":
                        threholds[name[:-4]].w_min = value
                    case "WMax":
                        threholds[name[:-4]].w_max = value
                    case "CMax":
                        threholds[name[:-4]].c_max = value
                    case _:
                        pass
            elif row_table == table and row_group == group:
                conf.append(Item.from_dict(row))
        # Apply thresholds
        if threholds:
            for c in conf:
                if c.name in threholds:
                    c.thresholds = threholds[c.name]
        r = ParsedData(groups=groups, conf=conf)
        if address:
            r.mgmt_url = f"https://{address}/?devcrate=1&devslot={slot}"
        return r

    @staticmethod
    def _get_card(obj: Object) -> int:
        """
        Get `card` parameter for API call.

        Args:
            obj: Object.
        Returns:
            Card number according to API.
        """
        if (
            obj.model.uuid == CU_UUID
            and obj.parent
            and obj.parent_connection
            and obj.parent_connection.startswith("cu")
        ):
            # CU require additional treatment
            # Get number of slots
            n_slots = sum(1 for cn in obj.parent.model.connections if cn.type.uuid == H8_CT_UUID)
            cu_n = int(obj.parent_connection[2:])
            return 2 * n_slots + cu_n
        if obj.parent and obj.parent.model.uuid == HS_UUID:
            # Half-sized card
            return (int(obj.parent.parent_connection) - 1) * 2 + int(obj.parent_connection)
        return (int(obj.parent_connection) - 1) * 2 + 1

    def iter_headless(self, obj: Object) -> Iterable[Item]:
        """
        Generate data for headless mode.
        """
        match self.get_model_name(obj):
            case "ADM-200":
                yield from self.iter_headless_adm200(obj)
            case _:
                return

    def iter_headless_adm200(self, obj: Object) -> Iterable[Item]:
        """
        Generate headless config for ADM200
        """
        nvram = self.get_nvram(obj, {"SetMode": "AGG-200"})
        # pId
        yield Item(
            name="pId",
            value=obj.get_data("asset", "part_no"),
            description="Идентификатор блока",
            type=Type.STRING,
            table=Table.INFO,
            read_only=True,
        )
        # SetMode
        yield Item(
            name="SetMode",
            value=nvram["SetMode"],
            description="Установка режима",
            type=Type.ENUM,
            table=Table.CONFIG,
            read_only=False,
            options={k: v for k, v in ADM200_VMAP.items()},
        )

    def api_set(self, request, id: str, name: str, value: str):
        obj = self.app.get_object_or_404(Object, id=id)
        mo = self.get_managed_object(obj)
        if mo is None:
            return self.set_headless(obj, name, value)
        return self.set_managed(obj, mo, name, value)

    def set_headless(self, obj: Object, name: str, value: Any) -> dict[str, Any]:
        """
        Set operation in headless mode.

        Args:
            obj: Object instance.
            name: Parameter name.
            value: Parameter value.

        Returns:
            Dict for response.
        """
        match self.get_model_name(obj):
            case "ADM-200":
                return self.set_headless_adm200(obj, name, value)
            case _:
                return self.error_response("Headless mode is not supported")

    def set_headless_adm200(self, obj: Object, name: str, value: Any) -> dict[str, Any]:
        """
        Emulate ADM-200 commands.

        Args:
            obj: Object instance.
            name: Parameter name.
            value: Parameter value.

        Returns:
            Dict for response.
        """
        match name:
            case "SetMode":
                return self.set_headless_adm200_set_mode(obj, value)
            case _:
                return self.error_response("Command is unsupported in headless mode")

    def set_headless_adm200_set_mode(self, obj: Object, mode: Any) -> dict[str, Any]:
        """
        ADM-200 SetMode emulation.

        Args:
            obj: Object reference.
            mode: Mode value.

        Returns:
            Dict for response.
        """
        if not isinstance(mode, str):
            return self.error_response("Invalid mode")
        # Check mode name
        mode_name = ADM200_VMAP.get(mode)
        if mode_name is None:
            return self.error_response(f"Unsupported mode: {mode}")
        # Check crossings are available
        crossings = ADM200_MAP.get(mode_name)
        if crossings is None:
            return self.error_response(f"Unsupported mode: {mode}")
        # Save to NVRAM
        self.set_nvram(obj, "SetMode", mode_name)
        # Set crossing
        obj.cross = [
            Crossing(
                input=item["input"],
                output=item["output"],
                input_discriminator=item.get("input_discriminnator"),
                output_discriminator=item.get("output_discriminator"),
            )
            for item in crossings
        ]
        obj.save()
        return self.success_response("Crossings has been set")

    def set_managed(self, obj: Object, mo: ManagedObject, name: str, value: Any) -> dict[str, Any]:
        """
        Apply settings to managed object.

        Args:
            obj: Object instance.
            mo: Managed object instance.
            name: Parameter name.
            value: Parameter value.

        Returns:
            Dict for response.
        """
        # @todo: Wrap to catch errors
        mo.scripts.set_param(card=self._get_card(obj), name=name, value=value)
        # Check if we must refetch crossings
        if self._to_refresh_crossings(obj, name):
            self._refresh_crossings(mo, obj)
        return {"status": True}

    def _refresh_crossings(self, mo: ManagedObject, _obj: Object) -> None:
        """
        Refresh crossings.
        """
        # @todo: Run asset check
        mo.run_discovery(delta=0)

    def _to_refresh_crossings(self, obj: Object, cmd: str) -> bool:
        """
        Check if we need to refetch crossings after command.

        Args:
            obj: Object instance.
            cmd: Issued commands.

        Returns:
            True: if the crossings needs to be refreshed.
            False: if crossings are untouched.
        """
        match self.get_model_name(obj):
            case "ADM-200":
                return self._to_refresh_crossings_adm200(cmd)
            case _:
                return False

    def _to_refresh_crossings_adm200(self, cmd: str) -> bool:
        """
        Check if ADM-200 command must refresh crossings.
        """
        match cmd:
            case "SetMode":
                return True
            case _:
                return False

    @classmethod
    def get_managed_object(cls, obj: Object) -> ManagedObject | None:
        """
        Get M.O. related to module.

        Returns:
            id: If object is managed.
            None: otherwise.
        """
        box = obj.get_box()
        mo_id = box.get_data("management", "managed_object")
        if not mo_id:
            return None
        return ManagedObject.get_by_id(mo_id)

    def get_pconf_beef(self, obj: Object) -> None:
        box = obj.get_box()
        d = box.get_data("debug", "beef_path", scope="get_params")
        if not d:
            return None
        storage_name, path = d.split(":", 1)
        self.logger.info("Trying to get beef fron %s", d)
        storage = ExtStorage.get_by_name(storage_name)
        if not storage:
            self.logger.info("Storage %s is not found, skipping", storage_name)
            return None
        fs = storage.open_fs()
        with fs.open(path) as fp:
            return orjson.loads(fp.read())

    @classmethod
    def get_model_name(cls, obj: Object) -> str:
        """
        Get model name.

        Args:
            obj: Object instance.

        Returns:
            Normalized model name.
        """
        return obj.model.name.split("|")[-1].strip()

    @classmethod
    def success_response(cls, msg: str) -> dict[str, Any]:
        """
        Generate success response.

        Args:
            msg: Error message

        Returns:
            Response dict.
        """
        return {"status": True, "message": msg}

    @classmethod
    def error_response(cls, msg: str) -> dict[str, Any]:
        """
        Generate error response.

        Args:
            msg: Error message

        Returns:
            Response dict.
        """
        return {"status": False, "message": msg}


# Crossing table for ADM-200
ADM200_VMAP = {
    "0": "AGG-2x100",
    "1": "AGG-100-BS",
    "2": "AGG-200",
    "3": "ADM-100",
    "4": "TP-100+TP-10x10",
}

ADM200_MAP = {
    # AGG-100-BS
    "AGG-200": [
        {"input": "CLIENT1", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-1"},
        {"input": "CLIENT2", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-2"},
        {"input": "CLIENT3", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-3"},
        {"input": "CLIENT4", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-4"},
        {"input": "CLIENT5", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-5"},
        {"input": "CLIENT6", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-6"},
        {"input": "CLIENT7", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-7"},
        {"input": "CLIENT8", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-8"},
        {"input": "CLIENT9", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-9"},
        {"input": "CLIENT10", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-10"},
        {"input": "CLIENT11", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-11"},
        {"input": "CLIENT12", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-12"},
        {"input": "CLIENT13", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-13"},
        {"input": "CLIENT14", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-14"},
        {"input": "CLIENT15", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-15"},
        {"input": "CLIENT16", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-16"},
        {"input": "CLIENT17", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-17"},
        {"input": "CLIENT18", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-18"},
        {"input": "CLIENT19", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-19"},
        {"input": "CLIENT20", "output": "LINE1", "output_discriminator": "odu::ODUC2::ODU2-20"},
    ],
    "ADM-10": [
        {"input": "CLIENT1", "output": "LINE1", "output_discriminator": "odu::ODU2::ODU0-1"},
        {"input": "CLIENT2", "output": "LINE1", "output_discriminator": "odu::ODU2::ODU0-2"},
        {"input": "CLIENT3", "output": "LINE1", "output_discriminator": "odu::ODU2::ODU0-3"},
        {"input": "CLIENT4", "output": "LINE1", "output_discriminator": "odu::ODU2::ODU0-4"},
        {"input": "CLIENT5", "output": "LINE1", "output_discriminator": "odu::ODU2::ODU0-5"},
        {"input": "CLIENT6", "output": "LINE1", "output_discriminator": "odu::ODU2::ODU0-6"},
        {"input": "CLIENT7", "output": "LINE1", "output_discriminator": "odu::ODU2::ODU0-7"},
        {"input": "CLIENT8", "output": "LINE1", "output_discriminator": "odu::ODU2::ODU0-8"},
        {"input": "CLIENT9", "output": "LINE2", "output_discriminator": "odu::ODU2::ODU0-1"},
        {"input": "CLIENT10", "output": "LINE2", "output_discriminator": "odu::ODU2::ODU0-2"},
        {"input": "CLIENT11", "output": "LINE2", "output_discriminator": "odu::ODU2::ODU0-3"},
        {"input": "CLIENT12", "output": "LINE2", "output_discriminator": "odu::ODU2::ODU0-4"},
        {"input": "CLIENT13", "output": "LINE2", "output_discriminator": "odu::ODU2::ODU0-5"},
        {"input": "CLIENT14", "output": "LINE2", "output_discriminator": "odu::ODU2::ODU0-6"},
        {"input": "CLIENT15", "output": "LINE2", "output_discriminator": "odu::ODU2::ODU0-7"},
        {"input": "CLIENT16", "output": "LINE2", "output_discriminator": "odu::ODU2::ODU0-8"},
    ],
    "AGG-2x100": [
        {"input": "CLIENT1", "output": "LINE1", "output_discriminator": "odu::ODU4::ODU2-1"},
        {"input": "CLIENT2", "output": "LINE1", "output_discriminator": "odu::ODU4::ODU2-2"},
        {"input": "CLIENT3", "output": "LINE1", "output_discriminator": "odu::ODU4::ODU2-3"},
        {"input": "CLIENT4", "output": "LINE1", "output_discriminator": "odu::ODU4::ODU2-4"},
        {"input": "CLIENT5", "output": "LINE1", "output_discriminator": "odu::ODU4::ODU2-5"},
        {"input": "CLIENT6", "output": "LINE1", "output_discriminator": "odu::ODU4::ODU2-6"},
        {"input": "CLIENT7", "output": "LINE1", "output_discriminator": "odu::ODU4::ODU2-7"},
        {"input": "CLIENT8", "output": "LINE1", "output_discriminator": "odu::ODU4::ODU2-8"},
        {"input": "CLIENT9", "output": "LINE1", "output_discriminator": "odu::ODU4::ODU2-9"},
        {"input": "CLIENT10", "output": "LINE1", "output_discriminator": "odu::ODU4::ODU2-10"},
        {"input": "CLIENT11", "output": "LINE2", "output_discriminator": "odu::ODU4::ODU2-1"},
        {"input": "CLIENT12", "output": "LINE2", "output_discriminator": "odu::ODU4::ODU2-2"},
        {"input": "CLIENT13", "output": "LINE2", "output_discriminator": "odu::ODU4::ODU2-3"},
        {"input": "CLIENT14", "output": "LINE2", "output_discriminator": "odu::ODU4::ODU2-4"},
        {"input": "CLIENT15", "output": "LINE2", "output_discriminator": "odu::ODU4::ODU2-5"},
        {"input": "CLIENT16", "output": "LINE2", "output_discriminator": "odu::ODU4::ODU2-6"},
        {"input": "CLIENT17", "output": "LINE2", "output_discriminator": "odu::ODU4::ODU2-7"},
        {"input": "CLIENT18", "output": "LINE2", "output_discriminator": "odu::ODU4::ODU2-8"},
        {"input": "CLIENT19", "output": "LINE2", "output_discriminator": "odu::ODU4::ODU2-9"},
        {"input": "CLIENT20", "output": "LINE2", "output_discriminator": "odu::ODU4::ODU2-10"},
    ],
    "TP-100+TP-10x10": [
        {"input": "CLIENT1", "output": "CLIENT11", "output_discriminator": "odu::ODU2"},
        {"input": "CLIENT2", "output": "CLIENT12", "output_discriminator": "odu::ODU2"},
        {"input": "CLIENT3", "output": "CLIENT13", "output_discriminator": "odu::ODU2"},
        {"input": "CLIENT4", "output": "CLIENT14", "output_discriminator": "odu::ODU2"},
        {"input": "CLIENT5", "output": "CLIENT15", "output_discriminator": "odu::ODU2"},
        {"input": "CLIENT6", "output": "CLIENT16", "output_discriminator": "odu::ODU2"},
        {"input": "CLIENT7", "output": "CLIENT17", "output_discriminator": "odu::ODU2"},
        {"input": "CLIENT8", "output": "CLIENT18", "output_discriminator": "odu::ODU2"},
        {"input": "CLIENT9", "output": "CLIENT19", "output_discriminator": "odu::ODU2"},
        {"input": "CLIENT10", "output": "CLIENT20", "output_discriminator": "odu::ODU2"},
        {"input": "LINE2", "output": "LINE1", "output_discriminator": "odu::ODU4"},
    ],
}
