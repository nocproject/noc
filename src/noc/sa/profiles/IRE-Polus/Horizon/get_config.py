# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "IRE-Polus.Horizon.get_config"
    cache = True
    interface = IGetConfig

    def execute(self, **kwargs):
        config = self.http.get(
            "/snapshots/full/config.json",
            json=True,
        )
        return self.parse_config(config)

    def parse_config(self, data: dict[str, Any]) -> str:
        r = ["slots:"]
        for item in data["RK"][0]["DV"]:
            slot = item["slt"]
            r += [
                f"  # Slot:  {slot}",
                f"  # Class: {item['cls']}",
                f"  # PID:   {item['pid']}",
                f'  "{slot}":',
            ]
            for pp in item["PM"]:
                if pp.get("acs") != "W":
                    continue
                name = pp["nam"]
                if name in {"SetFactory"}:
                    continue
                value = pp.get("val", "").strip()
                if value == "::" or not value:
                    continue
                description = None
                choices = pp.get("EM")
                if choices:
                    for cc in choices:
                        if cc["dsc"] == value:
                            description = value
                            value = cc["val"]
                            break
                r.append(f'    - name: "{name}"')
                r.append(f'      value: "{value}"')
                if description:
                    r.append(f'      description: "{description}"')
        r.append("")
        return "\n".join(r)
