# ----------------------------------------------------------------------
# TT System with alarm groups
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseTTSystem
from .types import EscalationContext


class BaseGroupTTSystem(BaseTTSystem):
    def create(self, ctx: EscalationContext) -> str:
        """
        Create TT implemetation.

        Args:
            ctx: EscalationContext structure

        Returns:
            Created TT id

        Raises:
            TemporaryTTError: When escalation attempt may be retried.
            TTError: When escalation is failed.
        """
        # Create TT
        tt_id = self.create_tt(ctx)
        # Create Group TT
        gtt = self.create_group_tt(tt_id, ctx.timestamp)
        # Add to group
        for item in ctx.items:
            try:
                self.add_to_group_tt(gtt, item.tt_id)
                item.set_ok()
            except self.TemporaryTTError as e:
                item.set_temp(str(e))
            except self.TTError as e:
                item.set_fail(str(e))
        return tt_id

    def create_group_tt(self, tt_id: str, timestamp=None) -> str:
        """
        Promote tt as the group tt.

        Args:
            tt_id as returned by create_tt
            timestamp: Optional group TT timestamp

        Returns:
            group tt id
        """
        return tt_id

    def add_to_group_tt(self, gtt_id, obj):
        """
        Add object to the group tt
        :param gtt_id: Group tt id, as returned by create_group_tt
        :param obj: Supported object's identifier
        """
        raise NotImplementedError()
