# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RPC Wrapper
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import itertools
import uuid
import json
import logging
## Third-party modules
import tornado.concurrent
import tornado.gen
## NOC modules
from noc.lib.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


class RPCProxy(object):
    """
    API Proxy
    """
    def __init__(self, service, topic):
        self._logger = PrefixLoggerAdapter(logger, topic)
        self._service = service
        self._topic = topic
        self._client_id = str(uuid.uuid4())
        self._tid = itertools.count()
        self._transactions = {}
        self._methods = {}
        self._service.connect_writer()
        self._reply_to = "rpc.%s#ephemeral" % self._client_id
        self._service.subscribe(
            self._reply_to,
            "rpc#ephemeral",
            self.on_response
        )

    def __del__(self):
        self.close()

    def close(self):
        pass

    def __getattr__(self, item):
        if item.startswith("_"):
            return self.__dict__[item]
        else:
            mw = self._methods.get(item)
            if not mw:
                mw = RPCMethod(self, item)
                self._methods[item] = mw
            return mw

    def _call(self, method, *args, **kwargs):
        tid = self._tid.next()
        msg = {
            "id": tid,
            "method": method,
            "params": list(args)
        }
        if "_async" not in kwargs:
            # Set response address
            msg["from"] = self._reply_to
        self._logger.debug("RPC Request: %s", msg)
        self._service.publish(self._topic, msg)
        f = tornado.concurrent.Future()
        if "_async" in kwargs:
            f.set_result(None)
        else:
            self._transactions[tid] = f
        return f

    def on_response(self, message):
        self._logger.debug("RPC Response: %s", message.body)
        try:
            msg = json.loads(message.body)
        except ValueError, why:
            self._logger.error(
                "Failed to decode RPC response: %s", why)
            return True
        tid = msg.get("id")
        try:
            f = self._transactions.pop(tid)
        except KeyError:
            self._logger.error(
                "Invalid transaction id %s", tid
            )
            return True
        error = msg.get("error")
        if error:
            f.set_exception(error)
        else:
            f.set_result(msg.get("result"))
        return True


class RPCMethod(object):
    """
    API Method wrapper
    """
    def __init__(self, proxy, name):
        self._proxy = proxy
        self._name = name

    def __call__(self, *args, **kwargs):
        return self._proxy._call(self._name, *args, **kwargs)
