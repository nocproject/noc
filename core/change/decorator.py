# ----------------------------------------------------------------------
# @change decorator and worker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from logging import getLogger

# NOC modules
from noc.models import is_document, get_model_id
from .policy import change_tracker

logger = getLogger(__name__)


def change(model):
    """
    @change decorator to enable generalized change tracking on the model.
    :param model:
    :return:
    """
    if not hasattr(model, "get_by_id"):
        raise ValueError("[%s] Missed .get_by_id", get_model_id(model))
    if is_document(model):
        _track_document(model)
    else:
        _track_model(model)
    return model


def _track_document(model):
    """
    Setup document change tracking
    :param model:
    :return:
    """
    from mongoengine import signals

    logger.debug("[%s] Tracking changes", get_model_id(model))
    signals.post_save.connect(_on_document_change, sender=model)
    signals.pre_delete.connect(_on_document_delete, sender=model)


def _track_model(model):
    """
    Setup model change tracking
    :param model:
    :return:
    """
    from django.db.models import signals

    logger.debug("[%s] Tracking changes", get_model_id(model))
    signals.post_save.connect(_on_model_change, sender=model)
    signals.pre_delete.connect(_on_model_delete, sender=model)


def _on_document_change(sender, document, created=False, *args, **kwargs):
    model_id = get_model_id(document)
    op = "create" if created else "update"
    logger.debug("[%s|%s] Change detected: %s", model_id, document.id, op)
    changed_fields = list(document._changed_fields if not created else [])
    change_tracker.register(
        op=op,
        model=model_id,
        id=str(document.id),
        fields=changed_fields,
    )


def _on_document_delete(sender, document, *args, **kwargs):
    model_id = get_model_id(document)
    op = "delete"
    logger.debug("[%s|%s] Change detected: %s", model_id, document.id, op)
    change_tracker.register(
        op=op,
        model=model_id,
        id=str(document.id),
        fields=None,
    )
    if not hasattr(document, "get_changed_instance"):
        return
    document = document.get_changed_instance()
    change_tracker.register(
        op="update",
        model=get_model_id(document),
        id=str(document.id),
        fields=None,
    )


def _on_model_change(sender, instance, created=False, *args, **kwargs):
    def is_changed(field_name):
        ov = instance.initial_data[field_name]
        if hasattr(ov, "pk"):
            ov = ov.pk
        nv = getattr(instance, field_name)
        if hasattr(nv, "pk"):
            nv = nv.pk
        return str(ov) != str(nv)

    # Check for instance proxying
    if hasattr(instance, "get_changed_instance"):
        instance = instance.get_changed_instance()
        changed_fields = []
    else:
        changed_fields = [
            f_name for f_name in getattr(instance, "initial_data", []) if is_changed(f_name)
        ]
    # Register change
    model_id = get_model_id(instance)
    op = "create" if created else "update"
    logger.debug("[%s|%s] Change detected: %s", model_id, instance.id, op)
    change_tracker.register(
        op=op,
        model=model_id,
        id=str(instance.id),
        fields=changed_fields,
    )


def _on_model_delete(sender, instance, *args, **kwargs):
    model_id = get_model_id(instance)
    op = "delete"
    logger.debug("[%s|%s] Change detected: %s", model_id, instance.id, op)
    change_tracker.register(
        op=op,
        model=model_id,
        id=str(instance.id),
        fields=None,
    )
    if not hasattr(instance, "get_changed_instance"):
        return
    instance = instance.get_changed_instance()
    change_tracker.register(
        op="update",
        model=get_model_id(instance),
        id=str(instance.id),
        fields=None,
    )
