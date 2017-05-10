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
import itertools
## NOC modules
from noc.core.service.client import open_sync_rpc, RPCError
from noc.core.script.loader import loader
from noc.core.service.loader import get_dcs

CALLING_SERVICE = "MTManager"
DEFAULT_IDLE_TIMEOUT = 60


class Session(object):
    """
    SA session
    """
    _sessions = {}
    _lock = Lock()

    def __init__(self, object, idle_timeout=None):
        self._object = object
        self._id = str(uuid.uuid4())
        self._idle_timeout = idle_timeout or DEFAULT_IDLE_TIMEOUT

    def __del__(self):
        self.close()

    def __getattr__(self, name):
        if not loader.has_script("%s.%s" % (
                self._object.profile_name, name)):
            raise AttributeError("Invalid script %s" % name)
        return lambda **kwargs: self._call_script(name, kwargs)

    def __contains__(self, item):
        """
        Check object has script name
        """
        if "." not in item:
            # Normalize to full name
            item = "%s.%s" % (self._object.profile_name, item)
        return loader.has_script(item)

    def __iter__(self):
        return itertools.imap(
                lambda y: y.split(".")[-1],
                itertools.ifilter(
                        lambda x: x.startswith(self._object.profile_name + "."),
                        loader.iter_scripts()
                )
        )

    @classmethod
    def _get_service(cls, session, pool=None):
        with cls._lock:
            svc = cls._sessions.get(session)
        if not pool:
            return svc
        nsvc = get_dcs().resolve_sync("activator-%s" % pool, hint=svc)
        if nsvc:
            if (svc and svc != nsvc) or (not svc):
                with cls._lock:
                    cls._sessions[session] = nsvc
        return nsvc

    def _call_script(self, script, args, timeout=None):
        # Call SAE
        data = open_sync_rpc(
            "sae",
            calling_service=CALLING_SERVICE
        ).get_credentials(self._object.id)
        # Resolve service address
        service = self._get_service(self._id, data["pool"])
        # Call activator
        return open_sync_rpc(
            "activator",
            pool=self._object.pool.name,
            calling_service=CALLING_SERVICE,
            hints=[service]
        ).script(
            "%s.%s" % (self._object.profile_name, script),
            data["credentials"],
            data["capabilities"],
            data["version"],
            args,
            timeout,
            self._id,
            self._idle_timeout
        )

    def close(self):
        service = self._get_service(self._id)
        if service:
            # Close at activator
            # @todo: Use hints
            open_sync_rpc(
                "activator",
                pool=self._object.pool.name,
                calling_service=CALLING_SERVICE
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
