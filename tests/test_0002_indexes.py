# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test ensure-indexes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest


@pytest.mark.usefixtures("database")
def test_indexes(database):
    """
    Create indexes
    :param database:
    :return:
    """
    try:
        with open("commands/ensure-indexes.py") as f:
            exec(f.read())
    except SystemExit as e:
        assert e.code == 0
