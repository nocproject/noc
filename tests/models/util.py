# ----------------------------------------------------------------------
# Various utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.models import get_model, iter_model_id, is_document


def get_models():
    for model_id in iter_model_id():
        model = get_model(model_id)
        if model and not is_document(model):
            yield model


def get_documents():
    for model_id in iter_model_id():
        model = get_model(model_id)
        if model and is_document(model):
            yield model


def get_all_models():
    for model_id in iter_model_id():
        model = get_model(model_id)
        yield model
