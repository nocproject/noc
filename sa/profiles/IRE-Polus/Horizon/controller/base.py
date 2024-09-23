# ----------------------------------------------------------------------
# Horizon utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Iterable

# NOC modules
from noc.core.runner.models.jobreq import JobRequest, InputMapping, KVInputMapping
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.object import Object


@dataclass
class SetValue(object):
    name: str
    value: str
    description: str | None


class HorizonMixin(object):
    """
    Horizon platform utilities.
    """

    def get_card(self, obj: Object) -> int:
        """
        Get card number for module.
        """
        cn = obj.parent_connection
        if not cn:
            return 0
        if obj.parent and obj.parent.model.name.endswith("HS-H8"):
            # Half-sized card
            return (int(obj.parent.parent_connection) - 1) * 2 + int(cn)
        return (int(cn) - 1) * 2 + 1

    def set_request(self, req: SetValue) -> JobRequest:
        """
        Generate
        """
        return JobRequest(
            name=f"Set {req.name}",
            description=req.description,
            action="script",
            inputs=[
                InputMapping(name="script", value="set_param"),
                InputMapping(name="managed_object", value="{{ managed_object }}"),
                KVInputMapping(name="card", value="{{ card }}"),
                KVInputMapping(name="name", value=req.name),
                KVInputMapping(name="value", value=req.value),
            ],
        )

    def iter_set_requests(self, iter: Iterable[SetValue]) -> Iterable[JobRequest]:
        """
        Iterate a series of set requests.
        """
        last_name: str | None = None
        for set_req in iter:
            job = self.set_request(set_req)
            if last_name:
                job.depends_on = [last_name]
            yield job
            last_name = job.name

    @staticmethod
    def get_port_prefix(name: str) -> str:
        """
        Calculate configuration prefix for port name.

        Args:
            name: Port name

        Returns:
            Prefix for set commands.

        Raises:
            ValueError: On invalid name.
        """
        if name.startswith("LINE"):
            return f"Ln_{name[4:]}"
        if name.startswith("CLIENT"):
            return f"Cl_{name[6:]}"
        msg = f"Invalid port name: {name}"
        raise ValueError(msg)
