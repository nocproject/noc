# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test collection loading
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import operator
import os

# Third-party modules
import pytest

# NOC modules
from noc.core.collection.base import Collection


@pytest.fixture(params=list(Collection.iter_collections()), ids=operator.attrgetter("name"))
def collection(request):
    return request.param


@pytest.mark.xfail
def test_collection_path(collection):
    assert any(os.path.isdir(p) for p in collection.get_path())


@pytest.mark.usefixtures("database")
def test_collection_load(database, collection):
    """
    Load collection
    :param database:
    :return:
    """
    collection.sync()
