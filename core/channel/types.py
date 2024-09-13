# ----------------------------------------------------------------------
# Channel Types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
from enum import Enum


class ChannelTopology(Enum):
    """
    Topology of the channel.

    Attributes:
        P2P: Point-to-point.
        UP2P: Unidirectional point-to-point.
        BUNCH: Bunch of P2P pairs.
        UBUNCH: Unidirectional bunch of P2P pairs.
        P2MP: Point-to-multipoint.
        UP2MP: Unidirectional point-to-point.
        STAR: Full mesh.
    """

    P2P = "p2p"
    UP2P = "up2p"
    BUNCH = "bunch"
    UBUNCH = "ubunch"
    P2MP = "p2mp"
    UP2MP = "up2mp"
    STAR = "star"

    @property
    def is_unidirectional(self) -> bool:
        """Check if topology is unidirectional."""
        return self in (ChannelTopology.UP2P, ChannelTopology.UBUNCH, ChannelTopology.UP2MP)

    @property
    def is_bidirectional(self) -> bool:
        """Check if topology is bidirectional."""
        return not self.is_unidirectional


class ChannelKind(Enum):
    """
    Kind of channel.

    Attributes:
        L1: Level-1
        L2: Level-2
        L3: Level-3
        INTERNET: Global connectivity.
    """

    L1 = "l1"
    L2 = "l2"
    L3 = "l3"
    INTERNET = "internet"
