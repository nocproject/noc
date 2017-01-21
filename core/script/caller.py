# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Script caller client
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock
import uuid
## NOC modules
from noc.core.service.client import RPCClient, RPCError
from noc.core.script.loader import loader

CALLING_SERVICE = "MTManager"
DEFAULT_IDLE_TIMEOUT = 60


class Session(object):
    """
    SA session
    """
    _sessions = {}
    _lock = Lock()

    class CallWrapper(object):
        def __init__(self, session, script):
            self.session = session
            self.script = script

        def __call__(self, **kwargs):
            return self.session._call_script(
                self.script, kwargs
            )

    def __init__(self, object, idle_timeout=None):
        self._object = object
        self._id = str(uuid.uuid4())
        self._cache = {}
        self._idle_timeout = idle_timeout or DEFAULT_IDLE_TIMEOUT

    def __del__(self):
        self.close()

    def __getattr__(self, name):
        if name in self._cache:
            return self._cache[name]
        if not loader.has_script("%s.%s" % (
                self._object.profile_name, name)):
            raise AttributeError("Invalid script %s" % name)
        cw = Session.CallWrapper(self, name)
        self._cache[name] = cw
        return cw

    @classmethod
    def _get_service(cls, session, default=None):
        with cls._lock:
            service = cls._sessions.get(session)
            if not service and default:
                cls._sessions[session] = default
                service = default
        return service

    def _call_script(self, script, args, timeout=None):
        # Call SAE
        data = RPCClient(
            "sae",
            calling_service=CALLING_SERVICE
        ).get_credentials(self._object.id)
        # Get hints from session
        service = self._get_service(self._id, data["service"])
        # Call activator
        return RPCClient(
            "activator-%s" % self._object.pool.name,
            calling_service=CALLING_SERVICE,
            hints=[service]
        ).script(
            "%s.%s" % (self._object.profile_name, script),
            data["credentials"],
            data["capabilities"],
            data["version"],
            args,
            timeout
        )

    def close(self):
        service = self._get_service(self._id)
        if service:
            # Close at activator
            RPCClient(
                "activator-%s" % self._object.pool.name,
                calling_service=CALLING_SERVICE,
                hints=[service]
            ).close_session(self._id)
            # Remove from cache
            with self._lock:
                try:
                    del self._sessions[self._id]
                except KeyError:
                    pass


class SessionContext(object):
    def __init__(self, object, idle_timeout=None):
        self._object = object
        self._idle_timeout = idle_timeout or DEFAULT_IDLE_TIMEOUT
        self._session = Session(self._object, self._idle_timeout)
        self._object_scripts = None

    def __enter__(self):
        self._object_scripts = getattr(self._object, "_scripts", None)
        self._object._scripts = self._session
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._object._scripts = self._object_scripts
        self._session.close()

    def __getattr__(self, name):
        if not name.startswith("_"):
            return getattr(self._session, name)
