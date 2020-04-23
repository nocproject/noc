# ----------------------------------------------------------------------
# Test __unicode__ method
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.comp import smart_text
from .util import get_models, get_documents


@pytest.mark.parametrize("model", get_models())
def test_model_str(model):
    for o in model.objects.all():
        assert str(o)


@pytest.mark.parametrize("model", get_documents())
def test_document_str(model):
    for o in model.objects.all():
        assert isinstance(str(o), str)


@pytest.mark.parametrize("model", get_models())
def test_model_unicode(model):
    for o in model.objects.all():
        assert smart_text(o)


@pytest.mark.parametrize("model", get_documents())
def test_document_unicode(model):
    for o in model.objects.all():
        assert isinstance(str(o), str)


@pytest.mark.parametrize("model", get_models())
def test_model_str_unicode(model):
    for o in model.objects.all():
        assert str(o) == smart_text(o)


@pytest.mark.parametrize("model", get_documents())
def test_document_str_unicode(model):
    for o in model.objects.all():
        assert str(o) == smart_text(o)
