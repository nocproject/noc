## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Default metric router
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
from collections import namedtuple
import re
## Django modules
from django.template import Template, Context, TemplateSyntaxError
from django.template.defaultfilters import register
## NOC modules
from noc.pm.router import BaseRouter
from settings import config

logger = logging.getLogger(__name__)

MetricRule = namedtuple("MetricRule", ["n", "rx", "probe", "active"])


class DefaultRouter(BaseRouter):
    _TEMPLATES = {}
    _RULES = []  # List of MetricRule
    CONFIG_SECTION = "pm_router"

    @classmethod
    def route(cls, object, settings):
        """
        Default pm-to-graphite router
        """
        model_id = cls.get_model_id(object)
        logger.debug("Mapping %s %s (%s)",
                     model_id, object, settings.metric_type)
        tpl = cls._TEMPLATES.get(model_id.lower())
        if not tpl:
            logger.debug("No template for model %s. Disabling metric",
                         model_id)
            settings.is_active = False
            return
        settings.is_active = cls.is_active(model_id, object)
        if not settings.is_active:
            logger.debug(
                "Deactivating metric for %s %s (%s)",
                model_id, object, settings.metric_type
            )
            settings.is_active = False
            return
        settings.metric = tpl.render(Context({
            "object": object,
            "model_id": model_id,
            "metric_type": settings.metric_type
        }))
        settings.probe = cls.get_default_probe()
        # Apply rules
        for r in cls._RULES:
            if r.rx.search(settings.metric):
                logger.debug("Apply rule %s", r.n)
                settings.probe = r.probe
                settings.active = r.active
                if not settings.active:
                    logger.debug("Metric disabled by rule %s", r.n)
                    settings.is_active = False
                    return
                break
        logger.debug(
            "Setting metric for %s %s (%s) "
            "to %s (probe %s)",
            model_id, object, settings.metric_type,
            settings.metric, settings.probe
        )

    @classmethod
    def is_active(cls, model_id, object):
        if model_id == "inv.Interface":
            return object.managed_object.is_managed
        elif model_id == "sa.ManagedObject":
            return object.is_managed
        elif model_id in (
                "sa.ManagedObjectProfile", "inv.InterfaceProfile"):
            return False
        else:
            return True

    @classmethod
    def configure(cls):
        rules = {}
        for opt in config.options(cls.CONFIG_SECTION):
            if opt.startswith("map."):
                # Process metric mappings
                _, model_id = opt.split(".", 1)
                v = config.get(cls.CONFIG_SECTION, opt)
                logger.info("Configuring metric mappings %s -> %s",
                            model_id, v)
                try:
                    cls._TEMPLATES[model_id] = Template(v)
                except TemplateSyntaxError, why:
                    logging.error("Template syntax error: %s", why)
            elif opt.startswith("metric."):
                # Process metric rules
                n = int(opt.split(".")[1])
                v = config.get(cls.CONFIG_SECTION, opt)
                try:
                    rx = re.compile(v)
                except re.error, why:
                    logging.error(
                        "Invalid regular expression in rule %s: %s",
                        n, why
                    )
                    continue
                if config.has_option(cls.CONFIG_SECTION, "probe.%s" % n):
                    probe_name = config.get(cls.CONFIG_SECTION, "probe.%s" % n)
                    try:
                        probe = cls.get_probe(probe_name)
                    except:
                        logging.error(
                            "Invalid probe in rule %s: %s",
                            n, probe_name
                        )
                else:
                    probe = cls.get_default_probe()
                if config.has_option(cls.CONFIG_SECTION, "active.%s" % n):
                    active = config.getboolean(cls.CONFIG_SECTION, "active.%s" % n)
                else:
                    active = True
                rules[n] = MetricRule(
                    n=n, rx=rx, probe=probe, active=active)
        # Order rules
        for n in sorted(rules):
            r = rules[n]
            logger.debug(
                "Metric rule %s: %s -> %s (active: %s)",
                n, r.rx.pattern, r.probe.name, r.active
            )
            cls._RULES += [r]


@register.filter(name="dirhash", is_safe=True)
def filter_dirhash2(value, arg=None):
    arg = arg or "4.2"
    width, levels = arg.split(".")
    return ".".join(BaseRouter.dir_hash(
        value, width=int(width), levels=int(levels)))


@register.filter(name="qm", is_safe=True)
def filter_qm(value, arg=None):
    def q(s):
        return s.replace(" ", "_").replace("/", "-").lower()

    level = int(arg) if arg else 0
    if not isinstance(value, basestring):
        value = unicode(value)
    mt = [q(s) for s in value.split(" | ")]
    return ".".join(mt[level:])

DefaultRouter.configure()
