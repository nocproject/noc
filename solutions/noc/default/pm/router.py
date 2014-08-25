## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Default metric router
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.pm.router import BaseRouter


class DefaultRouter(BaseRouter):
    @classmethod
    @BaseRouter.model_handler("sa.ManagedObject")
    def route_mo(cls, object, settings):
        """
        Metric:
        object.XXXX.YYYY.<object name>.<metric type>
        """
        settings.metric = ".".join(["object"] +
                                   cls.dir_hash(object, width=4) +
                                   [cls.q_type(object.name)] +
                                   [cls.q_type(settings.metric_type)])
        settings.is_active = object.is_managed
        settings.probe = cls.get_default_probe()

    @classmethod
    @BaseRouter.model_handler("inv.Interface")
    def route_iface(cls, object, settings):
        """
        Metric:
        object.XXXX.YYYY.<object name>.interface.<name>.<metric type>
        """
        mo = object.managed_object
        settings.metric = ".".join(["object"] +
                                   cls.dir_hash(mo, width=4) +
                                   [cls.q_type(mo.name)] +
                                   ["interface",
                                    cls.q_type(object.name),
                                    cls.q_type(settings.metric_type)])
        settings.is_active = mo.is_managed
        settings.probe = cls.get_default_probe()
