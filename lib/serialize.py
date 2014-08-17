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
    JSON_TYPE = "django_simplejson"


## Install handlers
logging.info("Using JSON library: %s" % JSON_TYPE)
if JSON_TYPE == "cjson":
    json_encode = cjson.encode
    json_decode = cjson.decode
elif JSON_TYPE == "django_simplejson":
    json_encode = simplejson.dumps
    json_decode = simplejson.loads
else:
    raise ValueError("Cannot detect proper JSON handler")

##
## Pickle
##
try:
    import cPickle as pickle
except ImportError:
    import pickle
