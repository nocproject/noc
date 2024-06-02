# ----------------------------------------------------------------------
# Django tuck-up panting for models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.apps import apps
from django.apps.config import AppConfig
from django.db.models.base import Model, ModelBase


class NOCModelBase(ModelBase):
    def __new__(mcs, name, bases, attrs):
        is_base = name == "NOCModel"
        # Initialize app registry to avoid calling django.setup()
        mcs.make_smoothie()
        if is_base:
            # ModelBase must accept empty bases for NOCModel itself
            # to bypass base class check
            bases = tuple(base for base in bases if base != Model)
        else:
            # NOCModel base class must be replaced to django's Model
            bases = tuple(base if base != NOCModel else Model for base in bases)
        m = super(NOCModelBase, mcs).__new__(mcs, name, bases, attrs)
        # Perform pants tucking: Fake up django's app registry population
        # to shut up their stupid checks.
        # NB: Every hipster may be misused
        if not is_base:
            mcs.tuck_up_pants(m)
        # Exclude non-update fields
        if hasattr(m, "_non_update_fields"):
            m._allow_update_fields = tuple(
                field.name
                for field in m._meta.fields
                if field.name not in m._ignore_on_save and not field.primary_key
            )
        return m

    @classmethod
    def make_smoothie(mcs):
        # Fake up registry ready flag
        apps.apps_ready = True
        apps.models_ready = True
        apps.ready = True
        apps.clear_cache()

    @classmethod
    def tuck_up_pants(mcs, kls):
        """
        implicit initialization of django models registry.
        :param kls:
        :return:
        """
        label = kls._meta.app_label
        app_name = "noc.%s" % label
        # Fake up apps.populate
        app_config = apps.app_configs.get(label)
        if not app_config:
            app_config = AppConfig.create(app_name)
            app_config.apps = apps  # Hipsters have many pants now. Tuck up default pants
            app_config.models = {}
            apps.app_configs[label] = app_config
        # Fake app AppConfig.import_models
        app_config.models = apps.all_models[label]
        # Tests should check all models has tucked pants
        kls._tucked_pants = True
        return kls


class NOCModel(Model, metaclass=NOCModelBase): ...
