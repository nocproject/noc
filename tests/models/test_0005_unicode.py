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
from noc.core.comp import smart_text
from .util import get_models, get_documents


@pytest.mark.parametrize("model", get_models())
def test_model_str(model):
    for o in model.objects.all():
        assert six.text_type(o)


@pytest.mark.parametrize("model", get_documents())
def test_document_str(model):
    for o in model.objects.all():
        assert isinstance(six.text_type(o), six.string_types)


@pytest.mark.parametrize("model", get_models())
def test_model_unicode(model):
    for o in model.objects.all():
        assert smart_text(o)


@pytest.mark.parametrize("model", get_documents())
def test_document_unicode(model):
    for o in model.objects.all():
        assert isinstance(six.text_type(o), six.text_type)


@pytest.mark.parametrize("model", get_models())
def test_model_str_unicode(model):
    for o in model.objects.all():
        assert six.text_type(o) == smart_text(o)


@pytest.mark.parametrize("model", get_documents())
def test_document_str_unicode(model):
    for o in model.objects.all():
        assert six.text_type(o) == smart_text(o)
