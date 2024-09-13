# ----------------------------------------------------------------------
# Channel primitives tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party module
import pytest

# NOC modules
from noc.core.channel.types import ChannelTopology


@pytest.mark.parametrize(
    ("topology", "is_unidirectional", "is_bidirectional"),
    [
        (ChannelTopology.P2P, False, True),
        (ChannelTopology.UP2P, True, False),
        (ChannelTopology.BUNCH, False, True),
        (ChannelTopology.UBUNCH, True, False),
        (ChannelTopology.P2MP, False, True),
        (ChannelTopology.UP2MP, True, False),
        (ChannelTopology.STAR, False, True),
    ],
)
def test_check_direction(
    topology: ChannelTopology, is_unidirectional: bool, is_bidirectional: bool
) -> None:
    assert topology.is_unidirectional is is_unidirectional
    assert topology.is_bidirectional is is_bidirectional
