# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

def deep_copy(t):
    """
    Returns copy of dict *t*, follows nested dict structures
    """
    r = {}
    for k, v in t.iteritems():
        if isinstance(v, dict):
            r[k] = deep_copy(v)
        else:
            r[k] = v
    return r


def deep_merge(t, d):
    """
    Merge contents of dicts *t* and *d*, including nested dicts,
    and returns merged dict. Values from *d* override values from *t*
    """
    def _merge(x, y):
        for k, v in y.iteritems():
            if isinstance(v, dict):
                x[k] = x.get(k, {})
                _merge(x[k], v)
            else:
                x[k] = v

    if not isinstance(t, dict) or not isinstance(d, dict):
        raise ValueError("dict required")
    r = deep_copy(t)
    _merge(r, d)
    return r


def get_model_id(object):
    """
    Returns object's model id
    """
    if isinstance(object._meta, dict):
        # Document
        return u"%s.%s" % (object.__module__.split(".")[1],
                           object.__class__.__name__)
    else:
        # Model
        return u"%s.%s" % (object._meta.app_label,
                           object._meta.object_name)
