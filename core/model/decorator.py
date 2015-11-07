# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various model decorators
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db.models import signals as django_signals


def _on_save_handler(sender, instance, *args, **kwargs):
    if hasattr(instance, "initial_data"):
        instance.changed_fields = set(
            f for f in instance.initial_data
            if getattr(instance, f) != instance.initial_data.get(f)
        )
    else:
        instance.changed_fields = set()
    instance.on_save()


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
        django_signals.post_save.connect(
            _on_save_handler,
            sender=cls
        )
    return cls


def _on_delete_handler(sender, instance, *args, **kwargs):
    instance.on_delete()


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
        django_signals.pre_delete.connect(
            _on_delete_handler,
            sender=cls
        )
    return cls


def _on_init_handler(sender, instance, *args, **kwargs):
    d = dict(
        (f.name, getattr(instance, f.attname))
        for f in sender._meta.local_fields
    )
    instance.initial_data = d


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
