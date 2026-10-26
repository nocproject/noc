# ----------------------------------------------------------------------
# Various utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from functools import cache

# NOC modules
from noc.models import DB_MODEL_TYPE, get_model, is_document, iter_model_id


@cache
def get_models() -> list[DB_MODEL_TYPE]:
    return [model for model in get_all_models() if not is_document(model)]


@cache
def get_documents():
    return [model for model in get_all_models() if is_document(model)]


@cache
def get_all_models():
    r: list[DB_MODEL_TYPE] = []
    for model_id in iter_model_id():
        model = get_model(model_id)
        if model:
            r.append(model)
    return r
