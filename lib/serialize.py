# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various serializers
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import logging

try:
    import cjson
    USE_CJSON = True
except ImportError:
    from django.utils import simplejson
    USE_SIMPLEJSON = True
    simplejson_encoder = simplejson.encoder.JSONEncoder
    simplejson_decoder = simplejson.decoder.JSONDecoder


def _simplejson_encode(obj):
    return simplejson_encoder(ensure_ascii=False).encode(obj)


def _simplejson_decode(s):
    return simplejson_decoder(encoding="utf-8").decode(s)

## Install handlers
if USE_CJSON:
    logging.info("Using cjson")
    json_encode = cjson.encode
    json_decode = cjson.decode
elif USE_SIMPLEJSON:
    logging.info("Using simplejson")
    json_encode = _simplejson_encode
    json_decode = _simplejson_decode
