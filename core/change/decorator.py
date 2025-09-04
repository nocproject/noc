# ----------------------------------------------------------------------
# @change decorator and worker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from logging import getLogger
from typing import Optional, List, Tuple
from functools import partial

# NOC modules
from noc.models import is_document, get_model_id
from noc.core.model.decorator import _on_init_handler
from .policy import change_tracker
from .model import ChangeField

logger = getLogger(__name__)


def get_datastreams(instance, changed_fields=None) -> Optional[List[Tuple[str, str]]]:
    if not hasattr(instance, "iter_changed_datastream"):
        return None
    return [item for item in instance.iter_changed_datastream(changed_fields=changed_fields or {})]


def change(model=None, *, audit=True):
    """
    @change decorator to enable generalized change tracking on the model.
    :param model:
    :param audit:
    :return:
    """
    if model is None:
        return partial(change, audit=audit)

    if not hasattr(model, "get_by_id"):
        raise ValueError("[%s] Missed .get_by_id" % get_model_id(model))
    if audit and not hasattr(model, "_flag_audit"):
        model._flag_audit = audit
    if is_document(model):
        _track_document(model)
    else:
        _track_model(model)
    return model


def _track_document(model):
    """
    Setup document change tracking
    """
    from mongoengine import signals

    logger.debug("[%s] Tracking changes", get_model_id(model))
    signals.post_save.connect(_on_document_change, sender=model)
    signals.post_delete.connect(_on_document_delete, sender=model)
    signals.post_init.connect(_on_init_handler, sender=model)


def _track_model(model):
    """
    Setup model change tracking
    """
    from django.db.models import signals

    logger.debug("[%s] Tracking changes", get_model_id(model))
    signals.post_save.connect(_on_model_change, sender=model)
    signals.post_delete.connect(_on_model_delete, sender=model)
    signals.post_init.connect(_on_init_handler, sender=model)


def _on_document_change(sender, document, created=False, *args, **kwargs):
    def get_changed(field_name: str) -> Optional[ChangeField]:
        """
        Return changed field with new and old value
        """
        ov, key = None, None
        if hasattr(document, "initial_data"):
            ov = document.initial_data[field_name]
        if hasattr(ov, "pk"):
            ov = str(ov.pk)
        elif hasattr(ov, "_instance"):
            # Embedded field
            ov = [str(x) for x in ov]
        elif "." in field_name:
            # Dict Field for key - extra_labels["sa"] = labels
            field_name, key = field_name.split(".", 1)
        elif ov:
            ov = str(ov)
        nv = getattr(document, field_name)
        if hasattr(nv, "pk"):
            nv = str(nv.pk)
        elif hasattr(nv, "_instance"):
            # Embedded field
            nv = [str(x) for x in nv]
        elif key:
            # Dict Field for key
            nv = nv.get(key)
        elif nv:
            nv = str(nv)
        if str(ov or None) == str(nv or None):
            return None
        return ChangeField(field=field_name, old=ov, new=nv)

    model_id = get_model_id(document)
    op = "create" if created else "update"
    changed_fields: List[ChangeField] = []
    for f_name in document._changed_fields if not created else []:
        cf = get_changed(f_name)
        if cf:
            changed_fields.append(cf)
    logger.debug("[%s|%s] Change detected: %s;%s", model_id, document.id, op, changed_fields)
    change_tracker.register(
        op=op,
        model=model_id,
        id=str(document.id),
        fields=changed_fields,
        datastreams=get_datastreams(document, {cf.field: cf.old for cf in changed_fields or []}),
        audit=getattr(document, "_flag_audit", False),
    )


def _on_document_delete(sender, document, *args, **kwargs):
    model_id = get_model_id(document)
    op = "delete"
    logger.debug("[%s|%s] Delete detected: %s", model_id, document.id, op)
    change_tracker.register(
        op=op,
        model=model_id,
        id=str(document.id),
        fields=None,
        datastreams=get_datastreams(document),
        audit=getattr(document, "_flag_audit", False),
    )
    if not hasattr(document, "get_changed_instance"):
        return
    document = document.get_changed_instance()
    change_tracker.register(
        op="update",
        model=get_model_id(document),
        id=str(document.id),
        fields=None,
        datastreams=get_datastreams(document),
        audit=getattr(document, "_flag_audit", False),
    )


def _on_model_change(sender, instance, created=False, *args, **kwargs):
    def get_changed(field_name: str) -> Optional[ChangeField]:
        """
        Return changed field with new and old value
        """
        ov = instance.initial_data[field_name]
        ov_label = None
        if hasattr(ov, "pk"):
            ov = str(ov.pk)
        if hasattr(ov, "name"):
            ov_label = ov.name
        nv = getattr(instance, field_name)
        nv_label = None
        if hasattr(nv, "pk"):
            nv = str(nv.pk)
        if hasattr(ov, "name"):
            ov_label = ov.name
        if field_name == "effective_labels" and nv and ov and set(nv).difference(set(ov)):
            return None
        elif str(ov or None) == str(nv or None):
            return None
        return ChangeField(field=field_name, old=ov, old_label=ov_label, new=nv, new_label=nv_label)

    changed_fields: List[ChangeField] = []
    # Check for instance proxying
    if hasattr(instance, "get_changed_instance"):
        instance = instance.get_changed_instance()
    else:
        for f_name in getattr(instance, "initial_data", []):
            cf = get_changed(f_name)
            if cf:
                changed_fields.append(cf)
    # Register change
    model_id = get_model_id(instance)
    op = "create" if created else "update"
    logger.debug("[%s|%s] Change detected: %s; %s", model_id, instance.id, op, changed_fields)
    change_tracker.register(
        op=op,
        model=model_id,
        id=str(instance.id),
        fields=changed_fields,
        datastreams=get_datastreams(instance, {cf.field: cf.old for cf in changed_fields or []}),
        audit=getattr(instance, "_flag_audit", False),
    )


def _on_model_delete(sender, instance, *args, **kwargs):
    model_id = get_model_id(instance)
    op = "delete"
    logger.debug("[%s|%s] Delete detected: %s", model_id, instance.id, op)
    change_tracker.register(
        op=op,
        model=model_id,
        id=str(instance.id),
        fields=None,
        datastreams=get_datastreams(instance),
        audit=getattr(instance, "_flag_audit", False),
    )
    if not hasattr(instance, "get_changed_instance"):
        return
    instance = instance.get_changed_instance()
    change_tracker.register(
        op="update",
        model=get_model_id(instance),
        id=str(instance.id),
        fields=None,
        datastreams=get_datastreams(instance),
        audit=getattr(instance, "_flag_audit", False),
    )
