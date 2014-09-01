## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Metric router API
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import hashlib
import base64
## NOC modules
from noc.pm.models.metricsettings import MetricSettings
from noc.pm.models.probe import Probe


class BaseRouter(object):
    # model -> route handler
    _MODEL_ROUTE = {}

    @classmethod
    def route(cls, object, settings):
        """
        Accept EffectiveSettings instance and fill
        *metric* and *probe* fields.
        Calls are routed to classmethod annotated by
        @BaseRouter.model_handler(...) functions
        """
        model_id = MetricSettings.get_model_id(object)
        handler = cls._MODEL_ROUTE.get(model_id)
        if handler:
            return handler(cls, object, settings)
        else:
            cls.default_route(object, settings)

    @classmethod
    def model_handler(cls, model_id):
        def decorate(f):
            cls._MODEL_ROUTE[model_id] = f
            return f

        return decorate

    @classmethod
    def default_route(cls, object, settings):
        """
        Default fallback handler, when no model handler found
        """
        raise NotImplementedError()

    @classmethod
    def object_hash(cls, object):
        """
        Return
        """
        key = "%s:%s" % (MetricSettings.get_model_id(object), object.pk)
        return base64.b32encode(hashlib.sha1(key).hexdigest())

    @classmethod
    def dir_hash(cls, object, levels=2, width=2):
        """
        Returns list of hashed dirnames
        :param object: Object to be hashed
        :param levels: Directory levels
        :param width: directory name width
        """
        r = []
        h = cls.object_hash(object)
        for i in range(levels):
            r += [h[:width]]
            h = h[width:]
        return r

    @classmethod
    def get_probe(cls, name):
        return Probe.objects.get(name=name)

    @classmethod
    def get_default_probe(cls):
        dp = getattr(cls, "_default_probe", None)
        if not dp:
            dp = Probe.objects.get(name="default")
            cls._default_probe = dp
        return dp

    @classmethod
    def q_type(cls, metric_type, level=0):
        def q(s):
            return s.replace(" ", "_").replace("/", "-").lower()

        if not isinstance(metric_type, basestring):
            metric_type = metric_type.name
        mt = [q(s) for s in metric_type.split(" | ")]
        return ".".join(mt[level:])
