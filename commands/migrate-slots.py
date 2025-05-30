# ----------------------------------------------------------------------
# Pretty command
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2025 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import asyncio
from typing import Dict

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.service.loader import get_dcs


class Command(BaseCommand):
    """
    Create slots.
    """

    help = "migrate slots"

    def handle(self, *args, **options):
        async def inner() -> bool:
            changed = False
            for k, v in sorted(slots.items()):
                current = await dcs.get_slot_limit(k)
                if current is None or current != v:
                    if current:
                        self.print(f"Chaning {k}: {current}->{v}")
                    else:
                        self.print(f"Setting {k} to {v}")
                    await dcs.set_slot_limit(k, v)
                    changed = True
            return changed

        slots: Dict[str, int] = {}
        for name, value in os.environ.items():
            if not name.startswith("NOC_MIGRATE_SLOTS_"):
                continue
            svc = name[18:]
            if "_" in svc:
                x, y = svc.split("_", 1)
                svc = f"{x}-{y}"
            slots[svc] = int(value)
        # Apply
        dcs = get_dcs()
        changed = asyncio.run(inner())
        self.print("CHANGED" if changed else "OK")


if __name__ == "__main__":
    Command().run()
