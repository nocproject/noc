# ----------------------------------------------------------------------
# Test migrate-liftbridge
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.debug import error_report


@pytest.mark.usefixtures("database")
def test_migrate_lb(database):
    """
    Test migrate-liftbridge
    :param database:
    :return:
    """
    m = __import__("noc.commands.migrate-liftbridge", {}, {}, "Command")
    try:
        r = m.Command().run_from_argv(["--slots", "1"])
        assert r == 0
    except Exception as e:
        error_report()
        pytest.exit(f"Not migrated streams: {e}", returncode=3)
