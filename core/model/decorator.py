# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Various model decorators
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db.models import signals as django_signals
from mongoengine import signals as mongo_signals
# NOC modules
from models import get_model


def is_document(klass):
    """
    Check klass is Document instance
    :param cls:
    :return:
    """
    return isinstance(klass._meta, dict)


def _get_field_snapshot(sender, instance):
    def g(field):
        n = getattr(field, "raw_name", field.attname)
        return getattr(instance, n)

    return dict(
        (f.name, g(f))
        for f in sender._meta.local_fields
    )


def _on_model_save_handler(sender, instance, *args, **kwargs):
    if hasattr(instance, "initial_data"):
        ns = _get_field_snapshot(sender, instance)
        instance.changed_fields = set(
            f for f in instance.initial_data
            if instance.initial_data[f] != ns.get(f)
        )
    else:
        instance.changed_fields = set()
    instance.on_save()


def _on_document_save_handler(sender, document, *args, **kwargs):
    document.on_save()


def on_save(cls):
    """
    Class decorator connecting django's post_save signal
    to models's on_save method. When used in conjuction with
    @on_init decorator, *changed_field* attribute is available

    Usage

    @on_save
    class MyModel(Model):
        ...
        def on_save(self):
           ...
    """
    if hasattr(cls, "on_save"):
        if is_document(cls):
            mongo_signals.post_save.connect(
                _on_document_save_handler,
                sender=cls
            )
        else:
            django_signals.post_save.connect(
                _on_model_save_handler,
                sender=cls
            )
    return cls


def _on_model_delete_handler(sender, instance, *args, **kwargs):
    instance.on_delete()


def _on_document_delete_handler(sender, document, *args, **kwargs):
    document.on_delete()


def on_delete(cls):
    """
    Class decorator connecting django's post_save signal
    to models's on_delete method.

    Usage

    @on_delete
    class MyModel(Model):
        ...
        def on_delete(self):
           ...
    """
    if hasattr(cls, "on_delete"):
        if is_document(cls):
            mongo_signals.pre_delete.connect(
                _on_document_delete_handler,
                sender=cls
            )
        else:
            django_signals.pre_delete.connect(
                _on_model_delete_handler,
                sender=cls
            )
    return cls


def _on_init_handler(sender, instance, *args, **kwargs):
    instance.initial_data = _get_field_snapshot(sender, instance)


def on_init(cls):
    """
    Class decorator storing initial model data into
    .initial_data attribute.

    @on_init
    class MyModel(Model):
        ...
        def my_method(self):
           ...
           print self.initial_data
           ...
    """
    django_signals.post_init.connect(
        _on_init_handler,
        sender=cls
    )
    return cls


def on_delete_check(check=None, clean=None, delete=None):
    """
    Class decorator to check and process constraints before
    trying to delete documents


    @on_delete_check(
        # Raise ValueError if related documents contain any records
        check=[
            ("sa.ManagedObjectSelector", "managed_object"),
            ....
        ],
        # Replace model.field value with None
        clean=[
            ("model", "field"),
            ...
        ],
        # Remove records referred by deleted one
        delete=[
            ("model", "field")
        ]
    )

    :return:
    """
    def on_delete_handler(sender, instance=None, *args, **kwargs):
        if not instance:
            # If mongo document instance
            instance = kwargs.get("document")
        # Raise value error when referred
        for model, model_id, field in iter_models("check"):
            for ro in iter_related(instance, model, field):
                raise ValueError(
                    "Referred from model %s: %s (id=%s)" % (
                        model_id,
                        unicode(ro),
                        ro.id
                    ))
        # Clean related
        for model, model_id, field in iter_models("clean"):
            for ro in iter_related(instance, model, field):
                setattr(ro, field, None)
                ro.save()
        # Delete related
        for model, model_id, field in iter_models("delete"):
            for ro in iter_related(instance, model, field):
                ro.delete()

    def iter_related(object, model, field):
        if setup["is_document"]:
            qs = {field: str(object.id)}
        else:
            qs = {field: object.pk}
        for ro in model.objects.filter(**qs):
            yield ro

    def iter_models(name):
        nn = "_%s" % name
        c = cfg.get(nn)
        if c is None:
            c = [(get_model(x[0]), x[0], x[1]) for x in cfg[name]]
            cfg[nn] = c
        for model, model_id, field in c:
            yield model, model_id, field

    def decorator(cls):
        if is_document(cls):
            mongo_signals.pre_delete.connect(
                on_delete_handler,
                sender=cls,
                weak=False
            )
            setup["is_document"] = True
        else:
            django_signals.pre_delete.connect(
                on_delete_handler,
                sender=cls,
                weak=False  # Cannot use weak reference due to lost of internal scope
            )
        return cls

    cfg = {
        "check": check or [],
        "clean": clean or [],
        "delete": delete or []
    }
    setup = {
        "is_document": False
    }
    return decorator
