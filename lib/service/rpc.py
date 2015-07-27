# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RPC Wrapper
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import itertools


class RPCHub(object):
    def __init__(self, service):
        self._service = service
        self._aliases = {}

    def alias(self, name, service, pool=None, version=1):
        """
        Register RPC service alias
        """
        self._aliases[name] = RPCServiceWrapper(
            self._service,
            service, pool, version
        )

    def __getattr__(self, item):
        i = self._aliases.get(item)
        if i:
            return i
        else:
            return self.__dict__[item]


class RPCServiceWrapper(object):
    def __init__(self, service, name, pool, version):
        self._service = service
        self._topic = "/v%s/%s/" % (version, name)
        if pool:
            self._topic += "%s/" % pool
        self._topic = self._topic[1:-1].replace("/", "-")
        self._tid = itertools.count()
        self._methods = {}

    def __getattr__(self, item):
        if item.startswith("_"):
            return self.__dict__[item]
        else:
            mw = self._methods.get(item)
            if not mw:
                mw =  RPCMethodWrapper(self, item)
                self._methods[item] = mw
            return mw


class RPCMethodWrapper(object):
    def __init__(self, service_wrapper, name):
        self._service_wrapper = service_wrapper
        self._name = name

    def __call__(self, *args, **kwargs):
        tid = self._service_wrapper._tid.next()
        self._service_wrapper._service.publish(
            topic=self._service_wrapper._topic,
            msg={
                "id": tid,
                "method": self._name,
                "params": args
            }
        )
        # @todo: Return Future
