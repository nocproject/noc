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

    ADM200_CLIENT_PROTOCOL_MAP = {
        "OTU2": "1",
        "OTU2e": "9",
        "STM64": "131",
        "TransEth10G": "258",
        "TransEth100G": "260",
        "8GFC": "515",
        "16GFC": "517",
    }

    @ChannelMixin.setup_for(ADM_200)
    def iter_adm200_setup(
        self, name: str, /, client_protocol: str | None = None, **kwargs: dict[str, str]
    ) -> Iterable[SetValue]:
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
        # Set client protocol
        if client_protocol:
            if client_protocol not in self.ADM200_CLIENT_PROTOCOL_MAP:
                msg = f"Invalid client protocol: {client_protocol}"
                raise ValueError(msg)
            yield SetValue(
                name=f"{prefix}_SetDataType",
                value=self.ADM200_CLIENT_PROTOCOL_MAP[client_protocol],
                description=f"Set data type to {client_protocol}",
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
        # Reset data type
        yield SetValue(
            name=f"{prefix}_SetDataType", value="258", description="Set data type to 10GE"
        )
        # Disable laser
        yield SetValue(name=f"{prefix}_{xcvr}_EnableTx", value="0", description="Disable laser.")
