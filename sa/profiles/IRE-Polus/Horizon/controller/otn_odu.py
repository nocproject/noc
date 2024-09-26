# ----------------------------------------------------------------------
# OTN ODU Controller for Horizon platform
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable
from uuid import UUID

# NOC modules
from noc.core.runner.job import JobRequest
from noc.inv.models.endpoint import Endpoint
from noc.inv.models.object import Object
from noc.core.techdomain.profile.otn_odu import BaseODUProfileController
from .base import HorizonMixin, SetValue


ADM200 = UUID("1187f420-fa75-4701-9e7a-816f5923203b")


class Controller(BaseODUProfileController, HorizonMixin):
    def _submit(
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
        return self._submit(
            ep=ep,
            job_type="submit",
            name=f"ODU Setup: {ep.resource}",
            description="Setup ODU for endpoint",
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
        return self._submit(
            ep=ep,
            job_type="submit",
            name=f"ODU Cleanup: {ep.resource}",
            description="Cleanup ODU for endpoint",
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

    def iter_adm200_setup(self, name: str) -> Iterable[SetValue]:
        """
        ADM-200 initialization.

        Args:
            name: Port name.
        """
        prefix = self.get_port_prefix(name)
        xcvr = self.get_adm200_xcvr_suffix(name)
        # Bring port up
        yield SetValue(
            name=f"{prefix}_SetState", value="2", description="Bring port up. Set state to IS."
        )
        # Enable laser
        yield SetValue(name=f"{prefix}_{xcvr}_EnableTx", value="1", description="Enable laser.")

    def iter_adm200_cleanup(self, name: str) -> Iterable[SetValue]:
        """
        ADM-200 initialization.

        Args:
            name: Port name.
        """
        prefix = self.get_port_prefix(name)
        xcvr = self.get_adm200_xcvr_suffix(name)
        # Bring port up
        yield SetValue(
            name=f"{prefix}_SetState", value="1", description="Bring port down. Set state to MT."
        )
        # Enable laser
        yield SetValue(name=f"{prefix}_{xcvr}_EnableTx", value="0", description="Disable laser.")

    HANDLERS = {ADM200: (iter_adm200_setup, iter_adm200_cleanup)}
