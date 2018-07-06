# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import operator
# Third-party modules
import pytest
# NOC modules
from noc.core.collection.base import Collection


@pytest.fixture(params=list(Collection.iter_collections()), ids=operator.attrgetter("name"))
def collection(request):
    return request.param


@pytest.mark.usefixtures("database")
def test_collection_load(database, collection):
    """
    Load collection
    :param database:
    :return:
    """
    collection.sync()
