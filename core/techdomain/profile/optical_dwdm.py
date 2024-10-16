# ----------------------------------------------------------------------
# BaseOpticalDwdmProfileController
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.runner.models.jobreq import JobRequest
from noc.inv.models.endpoint import Endpoint
from .channel import ProfileChannelController


class BaseOpticalDwdmProfileController(ProfileChannelController):
    name = "optical_dwdm"

    def setup(
        self, ep: Endpoint, dry_run: bool = False, destination: str | None = None, **kwargs
    ) -> JobRequest | None:
        return super().setup(ep, dry_run=dry_run, destination=destination, **kwargs)
