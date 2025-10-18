# ---------------------------------------------------------------------
# action commands
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import asyncio

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.core.service.error import RPCError
from .base import BaseAction, ActionError


class ActionCommands(BaseAction):
    """
    Run Action Commands
    """

    name = "action_commands"

    async def execute(
        self: "ActionCommands",
        *,
        action: str,
        managed_object: int,
        dry_run: bool = False,
        **kwargs: str,
    ) -> None:
        # Resolve Managed Object
        mo = await asyncio.to_thread(ManagedObject.get_by_id, managed_object)
        if not mo:
            self.logger.info("Cannot find managed object: %s", managed_object)
            raise ActionError("Cannot find managed object")
        username = self.env.get("username")
        # Run script
        if dry_run:
            self.logger.info(
                "[Dry Run] Run managed_object=%s script=%s by=%s args=%s",
                managed_object,
                action,
                username,
                kwargs,
            )
        else:
            self.logger.info(
                "Run managed_object=%s script=%s by=%s args=%s",
                managed_object,
                action,
                username,
                kwargs,
            )
        # @todo: Wrap and catch errors
        scr = getattr(mo.actions, action)
        # Processed Result
        try:
            return await asyncio.to_thread(scr, dry_run=dry_run, username=username, **kwargs)
        except RPCError as e:
            self.logger.error("RPC Call failed: %s", e)
        return None
