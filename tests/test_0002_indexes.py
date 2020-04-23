# ----------------------------------------------------------------------
# Test ensure-indexes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest


@pytest.mark.usefixtures("database")
def test_ensure_indexes(database):
    """
    Create indexes
    :param database:
    :return:
    """
    m = __import__("noc.commands.ensure-indexes", {}, {}, "Command")
    assert m.Command().run_from_argv([]) == 0
