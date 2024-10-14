# ----------------------------------------------------------------------
# Horizon utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Iterable
from uuid import UUID

# NOC modules
from noc.core.runner.models.jobreq import JobRequest, InputMapping, KVInputMapping
from noc.inv.models.object import Object
from noc.inv.models.endpoint import Endpoint
from noc.core.runner.job import JobRequest

# Cards
ADM_200 = UUID("1187f420-fa75-4701-9e7a-816f5923203b")
OADM_4_V_4 = UUID("6aaed88a-4d69-4d91-ab45-3be075a60188")
OADM_16_V_16 = UUID("c48af1f4-570e-4b1b-936d-24e5bb966064")
OM_40_V_C = UUID("084017ac-d5f5-465d-8e67-1361b74b4a2e")
OM_40_V_H = UUID("4a0ec15c-41c7-4a92-84ab-1654b1fb4c04")
OD_40_C = UUID("3eb083ad-031f-4d86-bb3a-f52d57168a8c")
OD_40_H = UUID("cd60fe64-67da-4570-bac8-8a3dd4f5b23d")
OM_96_H = UUID("4ef97220-12fc-4df7-9be3-98a79a080ed5")
OD_96_H = UUID("1777a6a3-7546-48c8-bec2-c9693d207493")


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


class ChannelMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        attrs["_SETUP_HANDLERS"] = {}
        attrs["_CLEANUP_HANDLERS"] = {}
        for v in attrs.values():
            setup = getattr(v, "_SETUP_HANDLERS", None)
            if setup:
                for uuid in v._SETUP_HANDLERS:
                    attrs["_SETUP_HANDLERS"][uuid] = v
                delattr(v, "_SETUP_HANDLERS")
            cleanup = getattr(v, "_CLEANUP_HANDLERS", None)
            if cleanup:
                for uuid in v._CLEANUP_HANDLERS:
                    attrs["_CLEANUP_HANDLERS"][uuid] = v
                delattr(v, "_CLEANUP_HANDLERS")
        n = type.__new__(mcs, name, bases, attrs)
        return n


class ChannelMixin(HorizonMixin, metaclass=ChannelMetaclass):
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
        self.logger.info(
            "Creating %s job for: %s (dry_run=%s)", job_type, ep.resource_label, dry_run
        )
        resource_path = ep.resource_path
        for job in jobs:
            job.resource_path = resource_path
        return JobRequest(
            name=name,
            description=description,
            locks=locks,
            jobs=jobs,
            environment={"managed_object": f"{mo.id}" if mo else "0", "card": str(card)},
            resource_path=resource_path,
        )

    def setup(self, ep: Endpoint, **kwargs) -> JobRequest | None:
        self.logger.info("Endpoint setup: %s", ep)
        # Get object
        obj = self.get_object(ep.resource)
        if not obj:
            self.logger.info("Object is not found: %s", ep.resource)
            return
        # Get port
        _, _, port = ep.resource.split(":", 2)
        # Get jobs
        jobs = list(self.iter_set_requests(self.iter_setup(obj, port, **kwargs)))
        if not jobs:
            self.logger.info("Nothing to setup, skipping")
            return None
        return self.submit(
            ep=ep,
            job_type="submit",
            name=f"{self.label} Setup: {ep.resource_label}",
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
            name=f"{self.label} Cleanup: {ep.resource_label}",
            description=f"Cleanup {self.label} for endpoint",
            jobs=jobs,
        )

    def iter_setup(self, obj: Object, port: str, **kwargs) -> Iterable[SetValue]:
        """
        Endpoint setup sequence.
        """
        h = self._SETUP_HANDLERS.get(obj.model.uuid)
        if h is None:
            self.logger.info("Model %s is not supported", obj.model.get_short_label())
            return
        yield from h(self, port, **kwargs)

    def iter_cleanup(self, obj: Object, port: str) -> Iterable[SetValue]:
        """
        Endpoint setup sequence.
        """
        h = self._CLEANUP_HANDLERS.get(obj.model.uuid)
        if h is None:
            self.logger.info("Model %s is not supported", obj.model.get_short_label())
            return
        yield from h(self, port)

    @classmethod
    def setup_for(cls, *args: UUID):
        def inner(f):
            f._SETUP_HANDLERS = args
            return f

        return inner

    @classmethod
    def cleanup_for(cls, *args: UUID):
        def inner(f):
            f._CLEANUP_HANDLERS = args
            return f

        return inner
