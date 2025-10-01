# ----------------------------------------------------------------------
# Test postgresql tables
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import connection
import pytest

# NOC modules
from .util import get_models, get_documents


@pytest.mark.parametrize("model", get_models())
def test_db_table(model, database):
    if not hasattr(model, "_meta"):
        pytest.skip("No _meta")
    if not hasattr(model._meta, "db_table"):
        pytest.skip("No db_table")

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM pg_class WHERE relname=%s", [model._meta.db_table])
    assert cursor.fetchall()[0][0] == 1, "Database table '%s' is not exists" % model._meta.db_table


@pytest.mark.parametrize("model", get_models())
def test_model_count(model, database):
    if not hasattr(model, "_meta"):
        pytest.skip("No _meta")
    if not hasattr(model._meta, "db_table"):
        pytest.skip("No db_table")

    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {model._meta.db_table}")


@pytest.mark.parametrize("model", get_documents())
def test_document_count(model, database):
    if not hasattr(model, "_meta"):
        pytest.skip("No _meta")
    model._get_collection().count_documents({})
