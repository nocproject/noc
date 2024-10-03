# ----------------------------------------------------------------------
# OTN ODU Controller for Horizon platform
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable

# NOC modules
from noc.core.techdomain.profile.otn_odu import BaseODUProfileController
from .base import ChannelMixin, SetValue, ADM_200


class Controller(ChannelMixin, BaseODUProfileController):
    label = "ODU"

    @ChannelMixin.setup_for(ADM_200)
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

    @ChannelMixin.cleanup_for(ADM_200)
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
