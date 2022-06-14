# ----------------------------------------------------------------------
# Various model decorators
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.models import get_model
from noc.core.comp import smart_text
from django.db.models import JSONField


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
            # Resolve references when neccessary
            return getattr(instance, n)
        return nv

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
        # Raise value error when referred
        for model, model_id, field in iter_models("check"):
            for ro in iter_related(instance, model, field):
                raise ValueError(
                    "Referred from model %s: %s (id=%s)" % (model_id, smart_text(ro), ro.id)
                )
        # Clean related
        for model, model_id, field in iter_models("clean"):
            for ro in iter_related(instance, model, field):
                if is_document(ro) and "__" in field:
                    # EmbeddedDocument Array
                    field, e_field = field.split("__")
                    # ro.objects.update(**{f"pull__{field}": instance.id})
                    setattr(
                        ro,
                        field,
                        [
                            ed
                            for ed in getattr(ro, field, [])
                            if getattr(ed, e_field, None) != instance
                        ],
                    )
                else:
                    setattr(ro, field, None)
                ro.save()
        # Delete related
        for model, model_id, field in iter_models("delete"):
            for ro in iter_related(instance, model, field):
                ro.delete()
        # Delete autogenerated lazy labels
        for ll in iter_lazy_labels(instance):
            ll.delete()

    def iter_lazy_labels(instance):
        from noc.main.models.label import MATCH_OPS

        model = get_model("main.Label")
        category = cfg.get("clean_lazy_labels")
        if not (hasattr(instance, "iter_lazy_labels") or category):
            return
        for ops in MATCH_OPS:
            ll = model.objects.filter(name=f"noc::{category}::{instance.name}::{ops}").first()
            if not ll:
                continue
            yield ll

    def iter_related(object, model, field):
        if setup["is_document"]:
            field = field.replace(".", "__")
            if (
                not is_document(model)
                and "__" in field
                and isinstance(model._meta.get_field(field.split("__")[0]), JSONField)
            ):
                # JSON field
                m_field, json_field = field.split("__")
                qs = {f"{m_field}__contains": [{json_field: str(object.id)}]}
            else:
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

        cls._on_delete = cfg
        return cls

    cfg = {
        "check": check or [],
        "clean": clean or [],
        "delete": delete or [],
        "ignore": ignore or [],
        "clean_lazy_labels": clean_lazy_labels or None,
    }
    setup = {"is_document": False}
    return decorator


def tree(field="parent"):
    """
    Class decorator checking cycling.

    """

    def _before_save_handler(sender, instance=None, document=None, field=field, *args, **kwargs):
        instance = instance or document
        parent = getattr(instance, field, None)
        seen = {instance.id}
        while parent:
            parent_id = getattr(parent, "id", None)
            if parent_id in seen:
                raise instance._ValidationError(f"[{instance}] Parent cycle link")
            seen.add(parent_id)
            parent = getattr(parent, field, None)

    def decorator(cls):
        if hasattr(cls, field):

            if is_document(cls):
                from mongoengine import signals as mongo_signals
                from mongoengine.errors import ValidationError

                mongo_signals.pre_save.connect(_before_save_handler, sender=cls, weak=False)
            else:
                from django.db.models import signals as django_signals
                from django.core.exceptions import ValidationError

                django_signals.pre_save.connect(_before_save_handler, sender=cls, weak=False)

            cls._ValidationError = ValidationError

        return cls

    return decorator
