# ----------------------------------------------------------------------
# Database initialization test.
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest


@pytest.mark.run_on_setup
def test_init_db(database) -> None:
    """Trigger database initialization."""
