# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Tagged Models Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models as django_models
from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.settings import INSTALLED_APPS


class ReportTaggedModels(SimpleReport):
    title = _("Tagged Models")

    def get_data(self, **kwargs):
        seen = set()
        for app in INSTALLED_APPS:
            if app.startswith("noc."):
                models = app + ".models"
                module = __import__(models, {}, {}, "*")
                for n in dir(module):
                    obj = getattr(module, n)
                    try:
                        if (issubclass(obj, django_models.Model) and
                                hasattr(obj, "tags")):
                            seen.add(obj)
                    except:
                        pass
        data = sorted((m._meta.app_label, m._meta.verbose_name) for m in seen)
        return self.from_dataset(title=self.title,
                                 columns=["Module", "Model"], data=data)
