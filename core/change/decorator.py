# ----------------------------------------------------------------------
# @change decorator and worker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from logging import getLogger
from typing import Optional, List, Tuple

# NOC modules
from noc.models import is_document, get_model_id
from .policy import change_tracker
from .model import ChangeField
from .change import on_change

logger = getLogger(__name__)


def get_datastreams(instance, changed_fields=None) -> Optional[List[Tuple[str, str]]]:
    if not hasattr(instance, "iter_changed_datastream"):
        return None
    return [item for item in instance.iter_changed_datastream(changed_fields=changed_fields or {})]


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
    signals.post_delete.connect(_on_document_delete, sender=model)


def _track_model(model):
    """
    Setup model change tracking
    :param model:
    :return:
    """
    from django.db.models import signals

    logger.debug("[%s] Tracking changes", get_model_id(model))
    signals.post_save.connect(_on_model_change, sender=model)
    signals.post_delete.connect(_on_model_delete, sender=model)


def _on_document_change(sender, document, created=False, *args, **kwargs):
    def get_changed(field_name: str) -> Optional[ChangeField]:
        """
        Return changed field with new and old value
        :param field_name:
        :return:
        """
        key = None
        ov = document.initial_data[field_name] if hasattr(document, "initial_data") else None
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
    change_list = [
        (
            op,
            model_id,
            document.id,
            [{"field": cf.field, "old": cf.old, "new": cf.new} for cf in changed_fields],
            datetime.datetime.now(),
        )
    ]
    on_change(change_list)
    logger.debug("[%s|%s] Change detected: %s;%s", model_id, document.id, op, changed_fields)
    change_tracker.register(
        op=op,
        model=model_id,
        id=str(document.id),
        fields=changed_fields,
        datastreams=get_datastreams(document, {cf.field: cf.old for cf in changed_fields or []}),
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
    )
    change_list = [
        (
            op,
            model_id,
            document.id,
            [{"field": None, "old": None, "new": None}],
            datetime.datetime.now(),
        )
    ]
    on_change(change_list)
    if not hasattr(document, "get_changed_instance"):
        return
    document = document.get_changed_instance()
    change_tracker.register(
        op="update",
        model=get_model_id(document),
        id=str(document.id),
        fields=None,
        datastreams=get_datastreams(document),
    )


def _on_model_change(sender, instance, created=False, *args, **kwargs):
    def get_changed(field_name: str) -> Optional[ChangeField]:
        """
        Return changed field with new and old value
        :param field_name:
        :return:
        """
        ov = instance.initial_data[field_name]
        if hasattr(ov, "pk"):
            ov = str(ov.pk)
        nv = getattr(instance, field_name)
        if hasattr(nv, "pk"):
            nv = str(nv.pk)
        if str(ov or None) == str(nv or None):
            return None
        return ChangeField(field=field_name, old=ov, new=nv)

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
    change_list = [
        (
            op,
            model_id,
            instance.id,
            [{"field": cf.field, "old": cf.old, "new": cf.new} for cf in changed_fields],
            datetime.datetime.now(),
        )
    ]
    on_change(change_list)
    logger.debug("[%s|%s] Change detected: %s; %s", model_id, instance.id, op, changed_fields)
    change_tracker.register(
        op=op,
        model=model_id,
        id=str(instance.id),
        fields=changed_fields,
        datastreams=get_datastreams(instance, {cf.field: cf.old for cf in changed_fields or []}),
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
    )
    change_list = [
        (
            op,
            model_id,
            instance.id,
            [{"field": None, "old": None, "new": None}],
            datetime.datetime.now(),
        )
    ]
    on_change(change_list)
    if not hasattr(instance, "get_changed_instance"):
        return
    instance = instance.get_changed_instance()
    change_tracker.register(
        op="update",
        model=get_model_id(instance),
        id=str(instance.id),
        fields=None,
        datastreams=get_datastreams(instance),
    )


def save_initial_state(model):
    """
    Декоратор для сохранения начального состояния полей документа MongoDB.

    :param model: Модель MongoDB
    :return: Модель с подключенным отслеживанием начального состояния
    """
    from mongoengine import signals as mongo_signals

    if not hasattr(model, "get_by_id"):
        raise ValueError("[%s] Missed .get_by_id, save_initial_state()", get_model_id(model))

    mongo_signals.pre_save.connect(_on_pre_save, sender=model, weak=False)
    return model


def _on_pre_save(sender, document, **kwargs):
    """
    Обработчик сигнала pre_save для сохранения начального состояния документа.

    :param sender: Модель, отправившая сигнал
    :param document: Экземпляр документа
    """
    if not hasattr(document, "initial_data"):
        document.initial_data = {}

    if document.id:
        try:
            existing_document = sender.objects.get(id=document.id)
            document.initial_data = existing_document.to_mongo().to_dict()
            logger.debug(
                "[%s|%s] Initial state saved, _on_pre_save(): %s",
                get_model_id(document),
                document.id,
                document.initial_data,
            )
        except sender.DoesNotExist:
            logger.warning(
                f"Document with id {document.id} does not exist. Skipping initial state saving."
            )
    else:
        document.initial_data = {}
