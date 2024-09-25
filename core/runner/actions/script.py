# ---------------------------------------------------------------------
# script action
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import asyncio

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from .base import BaseAction, ActionError


class ScriptAction(BaseAction):
    """
    Run script
    """

    name = "script"

    async def execute(
        self: "ScriptAction",
        *,
        script: str,
        managed_object: int,
        dry_run: bool = False,
        **kwargs: str,
    ) -> None:
        mo = int(managed_object)
        if dry_run or not mo:
            self.logger.info("[Dry run] managed_object=%s script=%s args=%s", mo, script, kwargs)
            return
        # Resolve Managed Object
        mo = await asyncio.to_thread(ManagedObject.get_by_id, mo)
        if not mo:
            self.logger.info("Cannot find managed object: %s", mo)
            raise ActionError("Cannot find managed object")
        # Run script
        self.logger.info("Run managed_object=%s script=%s args=%s")
        # @todo: Wrap and catch errors
        scr = mo.scripts[script]
        await asyncio.to_thread(scr, **kwargs)
        return None
