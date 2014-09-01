## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Solutions utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
from collections import defaultdict
## Django modules
from django.core import exceptions
from django.utils.importlib import import_module
## NOC modules
from noc.settings import config


_CCACHE = {}  # path -> callable


def get_solution(path):
    """
    Returns callable referenced by path
    """
    if callable(path):
        return path
    if path in _CCACHE:
        return _CCACHE[path]
    try:
        m, c = path.rsplit(".", 1)
    except ValueError:
        raise exceptions.ImproperlyConfigured("%s isn't valid solution name" % path)
    try:
        mod = import_module(m)
    except ImportError, e:
        raise exceptions.ImproperlyConfigured("Error loading solution '%s': %s" % (path, e))
    try:
        c = getattr(mod, c)
    except AttributeError:
        raise exceptions.ImproperlyConfigured("Solution '%s' doesn't define '%s' callable" % (path, c))
    _CCACHE[path] = c
    return c


def get_solution_from_config(section, name):
    return get_solution(config.get(section, name))


def init_solutions():
    """
    Initialize solutions and load modules
    """
    from noc.main.models import CustomField
    CustomField.install_fields()
    for sn in config.options("solutions"):
        if config.getboolean("solutions", sn):
            load_solution(sn)


def load_solution(name):
    """
    Load and initialize solution by name
    """
    __import__("noc.solutions.%s" % name, {}, {}, "")


def read_solutions_configs(config, name):
    cn = os.path.splitext(name)[0]
    # Update config with solution's one
    for sn in config.options("solutions"):
        if config.getboolean("solutions", sn):
            v, s = sn.split(".", 1)
            c = os.path.join("solutions", v, s, "etc", cn)
            config.read([c + ".defaults", c + ".conf"])


def solutions_roots():
    """
    Generator returning active solutions roots
    """
    for sn in config.options("solutions"):
        if config.getboolean("solutions", sn):
            vendor, name = sn.split(".", 1)
            yield os.path.join("solutions", vendor, name)


##
## Solutions API
##
def _get_alarm_class_keys(ac):
    """
    Get list of alarm class keys
    """
    from noc.fm.models.alarmclass import AlarmClass
    if not isinstance(ac, (list, tuple)):
        return _get_alarm_class_keys([ac])
    r = []
    for c in ac:
        if isinstance(c, AlarmClass):
            r += [c.id]
        else:
            c = AlarmClass.objects.filter(name=c).first()
            if not c:
                raise KeyError("Invalid alarm class '%s'" % c)
            r += [c.id]
    return r


def _get_event_class_keys(ec):
    """
    Get list of alarm class keys
    """
    from noc.fm.models.eventclass import EventClass
    if not isinstance(ec, (list, tuple)):
        return _get_event_class_keys([ec])
    r = []
    for c in ec:
        if isinstance(c, EventClass):
            r += [c.id]
        else:
            c = EventClass.objects.filter(name=c).first()
            if not c:
                raise KeyError("Invalid alarm class '%s'" % c)
            r += [c.id]
    return r


def _update_handlers_list(ht, keys, handlers, status, config=None):
    def get_handlers_list(handlers):
        def normalize(h):
            if callable(h):
                return "%s.%s" % (h.__module__, h.__name__)
            else:
                return h

        if not isinstance(handlers, (list, tuple)):
            return get_handlers_list([handlers])
        return [normalize(h) for h in handlers]

    hl = get_handlers_list(handlers)
    for k in keys:
        h = ht[k]
        # Remove previous occurences
        h = [x for x in h if x[0] not in hl]
        # Append new occurences
        h += [(x, status, config) for x in hl]
        ht[k] = h


def _get_effective_handlers(ht, key, handlers):
    hr = ht[key]
    disabled = set(x[0] for x in hr if not x[1])
    h = [x for x in handlers if x not in disabled]
    h += [x[0] for x in hr if x[1]]
    return h


def register_event_handler(ec, handlers):
    """
    Register additional event class handler
    :param event class: Scalar or list of event class or event class names
    """
    _update_handlers_list(
        _event_class_handlers,
        _get_event_class_keys(ec),
        handlers,
        True
    )

def unregister_event_handler(ec, handlers):
    """
    Unregister event class handler
    """
    _update_handlers_list(
        _event_class_handlers,
        _get_event_class_keys(ec),
        handlers,
        False
    )


def register_alarm_handler(ac, handlers):
    """
    Register additional event class handler
    """
    _update_handlers_list(
        _alarm_class_handlers,
        _get_alarm_class_keys(ac),
        handlers,
        True
    )


def unregister_alarm_handler(ac, handlers):
    """
    Unregister event class handler
    """
    _update_handlers_list(
        _alarm_class_handlers,
        _get_alarm_class_keys(ac),
        handlers,
        False
    )


def register_alarm_job(ac, jobs, config=None):
    """
    Register additional alarm job
    """
    _update_handlers_list(
        _alarm_job_handlers,
        _get_alarm_class_keys(ac),
        jobs,
        True,
        config
    )


def unregister_alarm_job(ac, jobs):
    """
    Unregister alarm job
    """
    _update_handlers_list(
        _alarm_job_handlers,
        _get_alarm_class_keys(ac),
        jobs,
        False
    )


def get_event_class_handlers(event_class):
    """
    Get effective event class handlers
    """
    return _get_effective_handlers(
        _event_class_handlers,
        event_class.id,
        event_class.handlers
    )


def get_alarm_class_handlers(alarm_class):
    """
    Get effective event class handlers
    """
    return _get_effective_handlers(
        _alarm_class_handlers,
        alarm_class.id,
        alarm_class.handlers
    )


def get_alarm_jobs(alarm_class):
    """
    Get effective event class handlers
    """
    from noc.fm.models.alarmclassjob import AlarmClassJob
    hr = _alarm_job_handlers[alarm_class.id]
    disabled = set(x[0] for x in hr if not x[1])
    jobs = [j for j in alarm_class.jobs if j.job not in disabled]
    jobs += [AlarmClassJob(job=j[0], **j[2]) for j in hr if j[1]]
    return jobs


def get_model_id(object):
    if isinstance(object._meta, dict):
        # Document
        return u"%s.%s" % (object.__module__.split(".")[1],
                           object.__class__.__name__)
    else:
        # Model
        return u"%s.%s" % (object._meta.app_label,
                           object._meta.object_name)


def register_probe_config(model, handlers):
    """
    Register .get_probe_config() extensions
    """
    if not isinstance(model, basestring):
        model = get_model_id(model)
    if not isinstance(handlers, (list, tuple)):
        handlers = [handlers]
    _probe_config_handlers[model] += [get_solution(h) for h in handlers]


def get_probe_config(object, config):
    """
    Get effective probe config extensions
    """
    model = get_model_id(object)
    for h in _probe_config_handlers[model]:
        try:
            return h(object, config)
        except ValueError:
            pass
    raise ValueError()


# event class key -> [(handler, status, None)]
_event_class_handlers = defaultdict(list)
# alarm class key -> [(handler, status, None)]
_alarm_class_handlers = defaultdict(list)
# alarm job key -> [(handler, status, config)]
_alarm_job_handlers = defaultdict(list)
# model -> []
_probe_config_handlers = defaultdict(list)