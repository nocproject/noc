# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test __unicode__ method
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import pytest
import six
# NOC modules
from .util import get_models, get_documents


@pytest.mark.parametrize("model", get_models())
def test_model_unicode(model):
    for o in model.objects.all():
        assert unicode(o)


@pytest.mark.parametrize("model", get_documents())
def test_document_unicode(model):
    for o in model.objects.all():
        assert isinstance(unicode(o), six.string_types)
