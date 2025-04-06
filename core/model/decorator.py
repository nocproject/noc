# ----------------------------------------------------------------------
# Various model decorators
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from functools import partial

# Third-party modules
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
from django.db import connection
from mongoengine.fields import ListField, EmbeddedDocumentListField

# NOC modules
from noc.models import get_model, get_model_id
from noc.core.model.fields import ObjectIDArrayField


def is_document(klass):
    """
    Check klass is Document instance
    :param klass:
    :return:
    """
    return isinstance(klass._meta, dict)


def _get_field_snapshot(sender, instance):
    def g(field):
        n = getattr(field, "raw_name", field.attname)
        nv = instance.__dict__.get(n)
        if nv:
            # Resolve references when necessary
            return getattr(instance, n)
        return nv

    def dg(field):
        nv = instance._data.get(field)
        if nv:
            # Resolve references when necessary
            return getattr(instance, field)
        return nv

    if is_document(sender):
        return {name: dg(name) for name in sender._fields}
    return {f.name: g(f) for f in sender._meta.local_fields}


def _on_model_save_handler(sender, instance, *args, **kwargs):
    if hasattr(instance, "initial_data"):
        ns = _get_field_snapshot(sender, instance)
        instance.changed_fields = set(
            f for f in instance.initial_data if instance.initial_data[f] != ns.get(f)
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
            from mongoengine import signals as mongo_signals

            mongo_signals.post_save.connect(_on_document_save_handler, sender=cls)
        else:
            from django.db.models import signals as django_signals

            django_signals.post_save.connect(_on_model_save_handler, sender=cls)
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
            from mongoengine import signals as mongo_signals

            mongo_signals.pre_delete.connect(_on_document_delete_handler, sender=cls)
        else:
            from django.db.models import signals as django_signals

            django_signals.pre_delete.connect(_on_model_delete_handler, sender=cls)
    return cls


def _on_init_handler(sender, instance=None, *args, **kwargs):
    if not instance:
        # If mongo document instance
        instance = kwargs.get("document")
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
    if is_document(cls):
        from mongoengine import signals as mongo_signals

        mongo_signals.post_init.connect(_on_init_handler, sender=cls)
    else:
        from django.db.models import signals as django_signals

        django_signals.post_init.connect(_on_init_handler, sender=cls)
    return cls


def on_delete_check(check=None, clean=None, delete=None, ignore=None, clean_lazy_labels=None):
    """
    Class decorator to check and process constraints before
    trying to delete documents


    @on_delete_check(
        # Raise ValueError if related documents contain any records
        check=[
            ("sa.ManagedObject", "platform"),
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
        ],
        # Ignore checks
        ignore=[
            ("model", "field")
        ]
    )

    :return:
    """

    def on_delete_handler(sender, instance=None, *args, **kwargs):
        if not instance:
            # If mongo document instance
            instance = kwargs.get("document")
        # Run on_before_delete if defined
        if hasattr(instance, "on_before_delete"):
            instance.on_before_delete()
        # Raise value error when referred
        for model, model_id, field in iter_models("check"):
            for ro in iter_related(instance, model, field):
                raise ValueError(f"Referred from model {model_id}: {str(ro)} (id={ro.id})")
        # Clean related
        for model, model_id, field in iter_models("clean"):
            ids = []
            for ro in iter_related(instance, model, field):
                ids.append(ro.id)
            #
            if not ids:
                continue
            remove_id = instance.name if setup["is_label"] else instance.id
            if is_document(model) and is_list(model, field):
                # Simple Array or EmbeddedDocument Array
                model.objects.filter(**{"id__in": ids}).update(**{f"pull__{field}": remove_id})
            elif is_list(model, field):
                # Django Array field
                cursor = connection.cursor()
                cursor.execute(
                    f"""
                UPDATE {model._meta.db_table}
                SET {field}=array_remove({field}, %s)
                WHERE id=ANY (%s)""",
                    [str(remove_id), ids],
                )
            else:
                model.objects.filter(**{"id__in": ids}).update(**{field: None})

        # Delete related
        for model, model_id, field in iter_models("delete"):
            for ro in iter_related(instance, model, field):
                ro.delete()
        # Delete autogenerated lazy labels
        for ll in iter_lazy_labels(instance):
            ll.delete()

    def is_list(model, field) -> bool:
        """
        Detect field is array
        :param model:
        :param field:
        :return:
        """
        if "__" in field:
            field, _ = field.split("__", 1)
        if is_document(model):
            field = model._fields[field]
        else:
            field = model._meta.get_field(field)
        if isinstance(
            field, (ListField, EmbeddedDocumentListField, ArrayField, ObjectIDArrayField)
        ):
            return True
        return False

    def iter_lazy_labels(instance):
        model = get_model("main.Label")
        category = cfg.get("clean_lazy_labels")
        if not (hasattr(instance, "iter_lazy_labels") or category):
            return
        for ll in model.objects.filter(name__startswith=f"noc::{category}::{instance.name}::"):
            yield ll

    def get_related_query(o, model, field):
        """
        Prepare query for request related objects
        :param o:
        :param model:
        :param field:
        :return:
        """
        if setup["is_label"] and is_document(model):
            return {f"{field}__contains": o.name}
        elif setup["is_label"]:
            return {f"{field}__contains": [o.name]}
        if not setup["is_document"]:
            # If checked Django model
            return {field: o.pk}
        # Replace dot notation
        field = field.replace(".", "__")
        if (
            not is_document(model)
            and "__" in field
            and isinstance(model._meta.get_field(field.split("__")[0]), JSONField)
        ):
            # Check Django JSON field
            m_field, json_field = field.split("__")
            return {f"{m_field}__contains": [{json_field: str(o.id)}]}
        return {field: str(o.pk)}

    def iter_related(object, model, field):
        qs = get_related_query(object, model, field)
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
        if cfg["check"] or cfg["clean"] or cfg["delete"] or cfg["clean_lazy_labels"]:
            if is_document(cls):
                from mongoengine import signals as mongo_signals

                mongo_signals.pre_delete.connect(on_delete_handler, sender=cls, weak=False)
                setup["is_document"] = True
            else:
                from django.db.models import signals as django_signals

                django_signals.pre_delete.connect(
                    on_delete_handler,
                    sender=cls,
                    weak=False,  # Cannot use weak reference due to lost of internal scope
                )
        setup["is_label"] = get_model_id(cls) == "main.Label"
        cls._on_delete = cfg
        return cls

    cfg = {
        "check": check or [],
        "clean": clean or [],
        "delete": delete or [],
        "ignore": ignore or [],
        "clean_lazy_labels": clean_lazy_labels or None,
    }
    setup = {"is_document": False, "is_label": False}
    return decorator


def tree(cls=None, *, field="parent"):
    """Class decorator checking cycling"""

    if cls is None:
        return partial(tree, field=field)

    def tree_recursion_check_handler(
        sender, instance=None, document=None, parent_field=field, *args, **kwargs
    ):
        instance = instance or document
        parent = getattr(instance, parent_field, None)
        seen = {instance.id}
        while parent:
            parent_id = getattr(parent, "id", None)
            if parent_id in seen:
                raise instance._ValidationError(f"[{instance}] Parent cycle link")
            seen.add(parent_id)
            parent = getattr(parent, parent_field, None)

    if hasattr(cls, field):
        if is_document(cls):
            from mongoengine import signals as mongo_signals
            from mongoengine.errors import ValidationError

            mongo_signals.pre_save.connect(tree_recursion_check_handler, sender=cls, weak=False)
        else:
            from django.db.models import signals as django_signals
            from django.core.exceptions import ValidationError

            django_signals.pre_save.connect(tree_recursion_check_handler, sender=cls, weak=False)

        cls._ValidationError = ValidationError

    return cls
