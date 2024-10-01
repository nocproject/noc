# ----------------------------------------------------------------------
# OTN OSC Controller for Horizon platform
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable

# NOC modules
from noc.core.techdomain.profile.otn_osc import BaseOSCProfileController
from .base import ChannelMixin, SetValue, OADM_4_V_4, OADM_16_V_16, OM_40_V_C, OM_40_V_H, OM_96_H

OSC_SET_STATE_MODELS = (OADM_4_V_4, OADM_16_V_16, OM_40_V_C, OM_40_V_H, OM_96_H)


class Controller(ChannelMixin, BaseOSCProfileController):
    label = "OCS"

    @ChannelMixin.setup_for(*OSC_SET_STATE_MODELS)
    def iter_osc_setup(self, name: str) -> Iterable[SetValue]:
        """
        OSC initialization.

        Args:
            name: Port name.
        """
        # Bring port up
        yield SetValue(name="OSCSetState", value="2", description="Bring OSC up. Set state to IS.")

    @ChannelMixin.cleanup_for(*OSC_SET_STATE_MODELS)
    def iter_osc_cleanup(self, name: str) -> Iterable[SetValue]:
        """
        OSC cleanup.

        Args:
            name: Port name.
        """
        # Bring port up
        yield SetValue(
            name="OSCSetState", value="1", description="Bring OSC down. Set state to MT."
        )
