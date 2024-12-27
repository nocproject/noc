# ---------------------------------------------------------------------
# inv.inv opm plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any
import uuid
from collections import defaultdict

# Third-party modules
import orjson

# NOC modules
from noc.inv.models.object import Object
from noc.sa.interfaces.base import StringParameter
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.extstorage import ExtStorage
from .base import InvPlugin

HS_UUID = uuid.UUID("1fd48ae6-df10-4ba4-ba72-1150fadbe6fe")
ROADM_2_9_UUID = uuid.UUID("230e3071-793d-4556-9e21-489b94812201")


class OPMPlugin(InvPlugin):
    name = "opm"
    js = "NOC.inv.inv.plugins.opm.OPMPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            f"fapi_plugin_{self.name}_data",
            self.api_data,
            url=f"^(?P<id>[0-9a-f]{{24}})/plugin/{self.name}/data/$",
            method=["GET"],
            validate={
                "g": StringParameter(),
                "b": StringParameter(),
            },
        )

    def get_data(self, request, o: Object):
        return {"status": True, "groups": self.get_groups(o), "bands": ["C", "H"]}

    def api_data(self, request, id: str, g: str, b: str):
        obj = self.app.get_object_or_404(Object, id=id)
        if obj.model.uuid == ROADM_2_9_UUID:
            gn = g.replace(" ", "")
            prefix = f"{gn}OCMPwr"
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

    def get_groups(self, obj: Object) -> list[str]:
        """
        Get all groups
        """
        if obj.model.uuid == ROADM_2_9_UUID:
            return ["Com In", "Com Out"]
        return []

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

    def fetch_data(self, obj: Object) -> dict[str, Any] | None:
        mo = self.get_managed_object(obj)
        if mo:
            # Managed
            return self.parse_slot(obj, mo.scripts.get_params())
        # Beef
        data = self.get_beef(obj)
        if data:
            return self.parse_slot(obj, self.get_beef(obj))
        return None

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

    def get_beef(self, obj: Object) -> None:
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
