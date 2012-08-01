# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test models
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from unittest import TestCase
## Django modules
from django.db import models as django_models


class LoadModuleNamesTest(TestCase):
    def check_get_absolute_url(self, model):
        """
        Check all models with .tags field have .get_absolute_url()
        :param model:
        :return:
        """
        failures = []
        if hasattr(model, "tags"):
            if not hasattr(model, "get_absolute_url"):
                failures += [
                    "%s has tags but no .get_absolute_url() defined" % model.__name__]
            elif not callable(getattr(model, "get_absolute_url")):
                failures += [
                    "%s.get_absolute_url is not callable" % model.name]
        return failures

    def check_orm(self, model):
        """
        Check basic ORM operations
        :param model:
        :return:
        """
        if hasattr(model, "objects"):
            try:
                model.objects.all()
            except Exception, why:
                return [str(why)]
        return []

    def check_model(self, model):
        """
        Check single model
        :param model:
        :return:
        """
        failures = []
        failures += self.check_get_absolute_url(model)
        failures += self.check_orm(model)
        return failures

    def test_models(self):
        """
        Test models.py
        :return:
        """
        from noc.settings import INSTALLED_APPS

        model_classes = set()
        # Search for models
        for app in INSTALLED_APPS:
            if app.startswith("noc."):
                models = app + ".models"
                module = __import__(models, {}, {}, "*")
                for n in dir(module):
                    obj = getattr(module, n)
                    try:
                        if issubclass(obj, django_models.Model):
                            model_classes.add(obj)
                    except:
                        pass
            # Check models
        failures = []
        for model in model_classes:
            failures += self.check_model(model)
        assert len(failures) == 0, "%d errors in models:\n\t" % len(
            failures) + "\n\t".join(failures)
        