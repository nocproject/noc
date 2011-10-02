# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various serializers
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import logging

JSON_TYPE = None
try:
    import cjson
    JSON_TYPE = "cjson"
except ImportError:
    from django.utils import simplejson
    from django.utils.simplejson.encoder import JSONEncoder
    from django.utils.simplejson.decoder import JSONDecoder
    simplejson_encoder = JSONEncoder
    simplejson_decoder = JSONDecoder
    JSON_TYPE = "django_simplejson"


def _simplejson_encode(obj):
    return simplejson_encoder(ensure_ascii=False).encode(obj)


def _simplejson_decode(s):
    return simplejson_decoder(encoding="utf-8").decode(s)

## Install handlers
logging.info("Using JSON library: %s" % JSON_TYPE)
if JSON_TYPE == "cjson":
    json_encode = cjson.encode
    json_decode = cjson.decode
elif JSON_TYPE == "django_simplejson":
    json_encode = _simplejson_encode
    json_decode = _simplejson_decode
