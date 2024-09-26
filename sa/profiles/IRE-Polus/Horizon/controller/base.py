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
from noc.inv.models.object import Object
from noc.inv.models.endpoint import Endpoint
from noc.core.runner.job import JobRequest


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

    @classmethod
    def get_adm200_xcvr_suffix(cls, name: str) -> str:
        """
        Get tranceiver suffix for ADM-200.

        Args:
            name: Port name.

        Raises:
            ValueError: On invalid name.

        Returns:
            Transceiver suffix.
        """
        if name.startswith("LINE"):
            return "CFP2"
        if name.startswith("CLIENT"):
            return "SFP"
        msg = f"Invalid port name: {name}"
        raise ValueError(msg)


class ChannelMixin(HorizonMixin):
    label: str

    def submit(
        self, /, ep: Endpoint, job_type: str, name: str, description: str, jobs: list[JobRequest]
    ) -> JobRequest | None:
        # Get managed object
        mo = self.get_managed_object(ep.resource)
        dry_run = not mo
        # Get card name
        obj = self.get_object(ep.resource)
        if obj.parent and obj.parent_connection:
            card = self.get_card(obj)
        else:
            card = 0
            dry_run = True
        # Get locks
        locks = None if dry_run else [f"mo:{mo.id}"]
        self.logger.info("Creating %s job for: %s (dry_run=%s)", job_type, ep.resource, dry_run)
        return JobRequest(
            name=name,
            description=description,
            locks=locks,
            jobs=jobs,
            environment={"managed_object": f"{mo.id}" if mo else "0", "card": str(card)},
        )

    def setup(self, ep: Endpoint) -> JobRequest | None:
        self.logger.info("Endpoint setup: %s", ep)
        # Get object
        obj = self.get_object(ep.resource)
        if not obj:
            self.logger.info("Object is not found: %s", ep.resource)
            return
        # Get port
        _, _, port = ep.resource.split(":", 2)
        # Get jobs
        jobs = list(self.iter_set_requests(self.iter_setup(obj, port)))
        if not jobs:
            self.logger.info("Nothing to setup, skipping")
            return None
        return self.submit(
            ep=ep,
            job_type="submit",
            name=f"{self.label} Setup: {ep.resource}",
            description=f"Setup {self.label} for endpoint",
            jobs=jobs,
        )

    def cleanup(self, ep: Endpoint) -> JobRequest | None:
        self.logger.info("Endpoint cleanup: %s", ep)
        # Get object
        obj = self.get_object(ep.resource)
        if not obj:
            self.logger.info("Object is not found: %s", ep.resource)
            return
        # Get port
        _, _, port = ep.resource.split(":", 2)
        # Get jobs
        jobs = list(self.iter_set_requests(self.iter_cleanup(obj, port)))
        if not jobs:
            self.logger.info("Nothing to setup, skipping")
            return None
        return self.submit(
            ep=ep,
            job_type="submit",
            name=f"{self.label} Cleanup: {ep.resource}",
            description="Cleanup {self.label} for endpoint",
            jobs=jobs,
        )

    def iter_setup(self, obj: Object, port: str) -> Iterable[SetValue]:
        """
        Endpoint setup sequence.
        """
        h = self.HANDLERS.get(obj.model.uuid)
        if h is None:
            self.logger.info("Model %s is not supported", obj.model.get_short_label())
            return
        yield from h[0](self, port)

    def iter_cleanup(self, obj: Object, port: str) -> Iterable[SetValue]:
        """
        Endpoint setup sequence.
        """
        h = self.HANDLERS.get(obj.model.uuid)
        if h is None:
            self.logger.info("Model %s is not supported", obj.model.get_short_label())
            return
        yield from h[1](self, port)

    HANDLERS = {}
