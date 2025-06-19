# ----------------------------------------------------------------------
# Create pools
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2025 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Dict
import os
from dataclasses import dataclass

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.main.models.pool import Pool


@dataclass
class PoolConfig(object):
    name: str
    description: str | None = None
    discovery_reschedule_limit: int | None = None


class Command(BaseCommand):
    """
    Create pools.
    """

    help = "create pools"

    def handle(self, *args, **options):
        pools = self.get_pools()
        if not pools:
            return
        connect()
        old_pools: Dict[str, Pool] = {pool.name: pool for pool in Pool.objects.all()}
        changed = False
        for pool in pools:
            if pool.name in old_pools:
                pv = old_pools[pool.name]
                item_changed = False
                if pool.description and pool.description != pv.description:
                    pv.description = pool.description
                    item_changed = True
                if pool.discovery_reschedule_limit is not None and (
                    not pv.discovery_reschedule_limit
                    or pv.discovery_reschedule_limit != pool.discovery_reschedule_limit
                ):
                    pv.discovery_reschedule_limit = pool.discovery_reschedule_limit
                    item_changed = True
                if item_changed:
                    self.print(f"Syncing {pool.name}")
                    changed = True
            else:
                print(f"Creating {pool.name}")
                pv = Pool(name=pool.name)
                if pool.description:
                    pv.description = pool.description
                if pool.discovery_reschedule_limit:
                    pv.discovery_reschedule_limit = pool.discovery_reschedule_limit
                pv.save()
                changed = True
        print("CHANGED" if changed else "OK")

    def get_pools(self) -> List[PoolConfig]:
        """Get pools from environment."""
        pools: Dict[str, PoolConfig] = {}
        for name, value in os.environ.items():
            if name.startswith("NOC_MIGRATE_POOL_"):
                pool_name = name[17:]
                pools[pool_name] = PoolConfig(name=pool_name, description=value)
            elif name.startswith("NOC_MIGRATE_POOLDRL_"):
                pool_name = name[20:]
                pool = pools.get(pool_name)
                if pool:
                    pool.discovery_reschedule_limit = int(value)
                else:
                    pools[pool_name] = PoolConfig(
                        name=pool_name, description=pool_name, discovery_reschedule_limit=int(value)
                    )
        return list(pools.values())


if __name__ == "__main__":
    Command().run()
