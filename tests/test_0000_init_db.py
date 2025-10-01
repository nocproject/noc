# ----------------------------------------------------------------------
# Database initialization test.
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import pytest


@pytest.mark.run_on_setup
def test_init_db(database):
    """Trigger database initialization."""
