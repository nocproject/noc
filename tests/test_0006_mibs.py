# ----------------------------------------------------------------------
# Test sync-mibs
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest


@pytest.mark.usefixtures("database")
def test_sync_mibs(database):
    """
    Test sync-mibs
    :param database:
    :return:
    """
    m = __import__("noc.commands.sync-mibs", {}, {}, "Command")
    assert m.Command().run_from_argv([]) == 0
