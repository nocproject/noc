# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# @datastream decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from django.db.models import signals as django_signals
from mongoengine import signals as mongo_signals
# NOC modules
from noc.core.model.decorator import is_document
from .change import register_changes


def datastream(cls):
    """
    Class decorator to track model changes to datastream

    Usage

    @datastream
    class MyModel(Model):
        ...
        def iter_changed_datastream(self):
           yield <datastream name>, <object id>
           ...
           yield <datastream name>, <object id>
    """
    if hasattr(cls, "iter_changed_datastream"):
        if is_document(cls):
            mongo_signals.post_save.connect(_on_document_change, sender=cls)
            mongo_signals.pre_delete.connect(_on_document_change, sender=cls)
        else:
            django_signals.post_save.connect(_on_model_change, sender=cls)
            django_signals.pre_delete.connect(_on_model_change, sender=cls)
    return cls


def _on_model_change(sender, instance, *args, **kwargs):
    _on_change(instance)


def _on_document_change(sender, document, *args, **kwargs):
    _on_change(document)


def _on_change(obj):
    r = list(obj.iter_changed_datastream())
    if r:
        register_changes(r)
