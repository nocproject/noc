# ----------------------------------------------------------------------
# Test migrate-ch
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest


@pytest.mark.usefixtures("database")
def test_migrate_ch(database):
    """
    Test migrate-ch
    :param database:
    :return:
    """
    m = __import__("noc.commands.migrate-ch", {}, {}, "Command")
    assert m.Command().run_from_argv([]) == 0
