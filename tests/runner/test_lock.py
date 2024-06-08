# ---------------------------------------------------------------------
# LockManager tests
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import asyncio
from typing import List

# NOC modules
from noc.core.runner.lock import LockManager


def test_locks() -> None:
    async def job(lm: LockManager, names: List[str]) -> None:
        async with lm.acquire(names):
            await asyncio.sleep(0.0001)  # Pass control

    async def _run(lm: LockManager) -> None:
        tasks = [
            asyncio.create_task(job(lm, ["1", "4", "5"])),
            asyncio.create_task(job(lm, ["2", "3", "5"])),
            asyncio.create_task(job(lm, ["1", "2", "4"])),
            asyncio.create_task(job(lm, ["3", "4", "5"])),
        ]
        await asyncio.gather(*tasks)

    async def run() -> None:
        lm = LockManager()
        await asyncio.wait_for(_run(lm), 1.0)
        assert not lm._waiters

    asyncio.run(run())
