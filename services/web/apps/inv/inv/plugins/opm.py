# ---------------------------------------------------------------------
# inv.inv opm plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any
import uuid
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

# Third-party modules
import orjson

# NOC modules
from noc.inv.models.object import Object
from noc.sa.interfaces.base import StringParameter
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.extstorage import ExtStorage
from .base import InvPlugin

HS_UUID = uuid.UUID("1fd48ae6-df10-4ba4-ba72-1150fadbe6fe")
OPM4_UUID = uuid.UUID("70daffc9-b161-4933-b36f-868c34ef6221")
ROADM_2_9_UUID = uuid.UUID("230e3071-793d-4556-9e21-489b94812201")


class Band(Enum):
    """Optical bands."""

    C = "C"
    H = "H"


@dataclass
class CardConfig(object):
    """
    Card configuration.

    Attributes:
        groups: List of the measurement points.
        bands: List of the supported bands.
    """

    groups: list[str]
    bands: list[Band]


class OPMPlugin(InvPlugin):
    name = "opm"
    js = "NOC.inv.inv.plugins.opm.OPMPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            f"api_plugin_{self.name}_get_data",
            self.api_data,
            url=f"^(?P<id>[0-9a-f]{{24}})/plugin/{self.name}/data/$",
            method=["GET"],
            validate={
                "g": StringParameter(),
                "b": StringParameter(),
            },
        )

    def get_data(self, request, o: Object):
        cfg = self.CARD_CONFIG.get(o.model.uuid)
        if not cfg:
            return {"status": False, "msg": "Unsupported card"}
        return {
            "status": True,
            "groups": cfg.groups,
            "bands": [x.value for x in cfg.bands],
        }

    def api_data(self, request, id: str, g: str, b: str):
        obj = self.app.get_object_or_404(Object, id=id)
        gn = g.replace(" ", "")
        if obj.model.uuid == ROADM_2_9_UUID:
            prefix = f"{gn}OCMPwr"
        elif obj.model.uuid == OPM4_UUID:
            prefix = f"{gn}Pwr"
        else:
            msg = "Not implemented for model {obj.model.name}"
            raise NotImplementedError(msg)
        # Process data
        power = defaultdict(list)
        for item in self.fetch_data(obj):
            name: str | None = item.get("nam")
            if not name or not name.startswith(prefix):
                continue
            value: str | None = item.get("val")
            if not value:
                continue
            ch = name[len(prefix) :].split(".", 1)[0]
            power[ch].append(float(value))
        return {
            "status": True,
            "power": [{"ch": int(ch[1:]), "power": v} for ch, v in power.items() if ch[0] == b],
        }

    def parse_slot(self, obj: Object, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Leave only slot data"""
        if not data:
            return []
        slot = self._get_card(obj)
        for item in data["RK"][0]["DV"]:
            s = item.get("slt")
            if not s:
                continue
            if s == slot:
                return item["PM"]
        return []

    def fetch_data(self, obj: Object) -> list[dict[str, Any]]:
        mo = self.get_managed_object(obj)
        if mo:
            # Managed
            return self.parse_slot(obj, mo.scripts.get_params())
        # Beef
        data = self.get_beef(obj)
        if data:
            return self.parse_slot(obj, self.get_beef(obj))
        return []

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

    def get_beef(self, obj: Object) -> dict[str, Any]:
        box = obj.get_box()
        d = box.get_data("debug", "beef_path", scope="get_params")
        if not d:
            self.logger.info("beef_path is not configured")
            return {}
        storage_name, path = d.split(":", 1)
        self.logger.info("Trying to get beef fron %s", d)
        storage = ExtStorage.get_by_name(storage_name)
        if not storage:
            self.logger.info("Storage %s is not found, skipping", storage_name)
            return {}
        fs = storage.open_fs()
        with fs.open(path) as fp:
            return orjson.loads(fp.read())

    @staticmethod
    def _get_card(obj: Object) -> int:
        """
        Get `card` parameter for API call.

        Args:
            obj: Object.
        Returns:
            Card number according to API.
        """
        if obj.parent and obj.parent.model.uuid == HS_UUID:
            # Half-sized card
            return (int(obj.parent.parent_connection) - 1) * 2 + int(obj.parent_connection)
        return (int(obj.parent_connection) - 1) * 2 + 1

    CARD_CONFIG = {
        ROADM_2_9_UUID: CardConfig(groups=["Com In", "Com Out"], bands=[Band.C, Band.H]),
        OPM4_UUID: CardConfig(groups=["In 1", "In 2", "In 3", "In 4"], bands=[Band.C, Band.H]),
    }
