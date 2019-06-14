# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Various django hacks
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.apps import apps
from django.apps.config import AppConfig
# NOC modules
from noc.models import get_model


def ensure_pending_models():
    """
    Django's ForeignKey with string rel resolves when
    appropriate model class being imported.

    :return:
    """
    for app, model in apps._pending_lookups:
        get_model("%s.%s" % (app, model))  # Ensure model loading


def tuck_up_pants(cls):
    """
    Decorator to implicit initialization of django models registry.
    Must be applied to every django model
    :param cls:
    :return:
    """
    assert not hasattr(cls, "_on_delete")
    label = cls._meta.app_label
    app_name = "noc.%s" % label
    # Fake up apps.populate
    app_config = apps.app_configs.get(label)
    if not app_config:
        app_config = AppConfig.create(app_name)
        apps.app_configs[label] = app_config
    # Fake up registry ready flag
    apps.apps_ready = True
    apps.models_ready = True
    apps.clear_cache()
    # Fake app AppConfig.import_models
    app_config.models = apps.all_models[label]
    # Tests should check all models has tucked pants
    cls._tucked_pants = True
    return cls
