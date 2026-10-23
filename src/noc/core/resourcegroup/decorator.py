# ----------------------------------------------------------------------
# @resourcegroup decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db.models import signals as django_signals
from mongoengine import signals as mongo_signals
from noc.inv.models.resourcegroup import ResourceGroup

# NOC models
from noc.models import is_document, get_model_id


def _apply_dynamic_service_groups(obj):
    dynamic_service_groups = []
    if hasattr(obj, "effective_labels"):
        dynamic_service_groups = ResourceGroup.get_dynamic_service_groups(
            obj.effective_labels, get_model_id(obj)
        )
    return (obj.static_service_groups or []) + dynamic_service_groups


def _apply_dynamic_client_groups(obj):
    dynamic_client_groups = []
    if hasattr(obj, "effective_labels"):
        dynamic_client_groups = ResourceGroup.get_dynamic_client_groups(
            obj.effective_labels, get_model_id(obj)
        )
    return (obj.static_client_groups or []) + dynamic_client_groups


def _apply_model_effective_groups(sender, instance=None, *args, **kwargs):
    instance.effective_service_groups = [str(x) for x in _apply_dynamic_service_groups(instance)]
    instance.effective_client_groups = [str(x) for x in _apply_dynamic_client_groups(instance)]


def _apply_document_effective_groups(sender, document=None, *args, **kwargs):
    document.effective_service_groups = _apply_dynamic_service_groups(document)
    document.effective_client_groups = _apply_dynamic_client_groups(document)


def resourcegroup(cls):
    if is_document(cls):
        mongo_signals.pre_save.connect(_apply_document_effective_groups, sender=cls)
    else:
        django_signals.pre_save.connect(_apply_model_effective_groups, sender=cls)
    return cls
