# ----------------------------------------------------------------------
# Test migrate-liftbridge
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest


@pytest.mark.usefixtures("database")
def test_migrate_lb(database):
    """
    Test migrate-liftbridge
    :param database:
    :return:
    """
    m = __import__("noc.commands.migrate-liftbridge", {}, {}, "Command")
    assert m.Command().run_from_argv(["--slots", "1"]) == 0
