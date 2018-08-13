# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# @resourcegroup decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db.models import signals as django_signals
from mongoengine import signals as mongo_signals
# NOC models
from noc.models import is_document


def _apply_dynamic_service_groups(obj):
    # @todo: Apply dynamic groups
    return obj.static_service_groups or []


def _apply_dynamic_client_groups(obj):
    # @todo: Apply dynamic groups
    return obj.static_client_groups or []


def _apply_effective_groups(sender, instance=None, *args, **kwargs):
    instance.effective_service_groups = _apply_dynamic_service_groups(instance)
    instance.effective_client_groups = _apply_dynamic_client_groups(instance)


def resourcegroup(cls):
    if is_document(cls):
        mongo_signals.pre_save.connect(
            _apply_effective_groups,
            sender=cls
        )
    else:
        django_signals.pre_save.connect(
            _apply_effective_groups,
            sender=cls
        )
    return cls
