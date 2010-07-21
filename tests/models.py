# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test models
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from unittest import TestCase
from django.db import models as django_models
import types
##
## Load MODULE_NAME from __init__.py
##
class LoadModuleNamesTest(TestCase):
    ##
    ## Check all models with .tags field have .get_absolute_url()
    ##
    def check_get_absolute_url(self,model):
        failures=[]
        if hasattr(model,"tags"):
            if not hasattr(model,"get_absolute_url"):
                failures+=["%s has tags but no .get_absolute_url() defined"%model.__name__]
            elif not callable(getattr(model,"get_absolute_url")):
                failures+=["%s.get_absolute_url is not callable"%model.name]
        return failures
    ##
    ## Check single model
    ##
    def check_model(self,model):
        failures=[]
        failures+=self.check_get_absolute_url(model)
        return failures
    ##
    ## Test models.py
    ##
    def test_models(self):
        from noc.settings import INSTALLED_APPS
        model_classes=set()
        # Search for models
        for app in INSTALLED_APPS:
            if app.startswith("noc."):
                models=app+".models"
                module=__import__(models,{},{},"*")
                for n in dir(module):
                    obj=getattr(module,n)
                    try:
                        if issubclass(obj,django_models.Model):
                            model_classes.add(obj)
                    except:
                        pass
        # Check models
        failures=[]
        for model in model_classes:
            failures+=self.check_model(model)
        assert len(failures)==0,"%d errors in models:\n\t"%len(failures)+"\n\t".join(failures)
        