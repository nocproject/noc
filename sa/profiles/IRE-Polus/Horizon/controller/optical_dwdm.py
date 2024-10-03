# ----------------------------------------------------------------------
# Optical DWDM Controller for Horizon platform
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable

# NOC modules
from noc.core.techdomain.profile.optical_dwdm import BaseOpticalDwdmProfileController
from .base import ChannelMixin, SetValue, OM_40_V_C, OM_40_V_H, OM_96_H, OD_96_H, OD_40_C, OD_40_H

DESTINATION_MODELS = (OM_40_V_C, OM_40_V_H, OD_40_C, OD_40_H, OM_96_H, OD_96_H)


class Controller(ChannelMixin, BaseOpticalDwdmProfileController):
    label = "Optical"

    @ChannelMixin.setup_for(*DESTINATION_MODELS)
    def iter_optical_setup(self, name: str, destination: str | None = None) -> Iterable[SetValue]:
        """
        Endpoint initialization.

        Args:
            name: Port name.
        """
        # Set destination
        if destination:
            yield SetValue(
                name=f"{name}Destination",
                value=destination,
                description=f"Set destination to {destination}",
            )

    @ChannelMixin.cleanup_for(*DESTINATION_MODELS)
    def iter_optical_cleanup(self, name: str) -> Iterable[SetValue]:
        """
        Endpoint cleanup.

        Args:
            name: Port name.
        """
        yield SetValue(name="{name}Destination", value="-", description="Reset destination")
