# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Tagged Models Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport
from noc.settings import INSTALLED_APPS
from django.db import models as django_models
##
##
##
class ReportTaggedModels(SimpleReport):
    title="Tagged Models"
    def get_data(self,**kwargs):
        data=[]
        for app in INSTALLED_APPS:
            if app.startswith("noc."):
                models=app+".models"
                module=__import__(models,{},{},"*")
                for n in dir(module):
                    obj=getattr(module,n)
                    try:
                        if issubclass(obj,django_models.Model) and hasattr(obj,"tags"):
                            data+=[[app[4:],obj._meta.verbose_name]]
                    except:
                        pass
        return self.from_dataset(title=self.title,columns=["Module","Model"],data=data)
