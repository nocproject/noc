# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Script caller and session manager
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import uuid
# NOC modules
from noc.core.service.client import open_sync_rpc
from noc.core.service.loader import get_dcs
from noc.core.dcs.error import ResolutionError
from noc.core.service.error import RPCNoService
from noc.config import config

CALLING_SERVICE = config.script.calling_service
DEFAULT_IDLE_TIMEOUT = config.script.caller_timeout


class ScriptCaller(object):
    def __init__(self, obj, name):
        if "." in name:
            self.name = name.split(".")[-1]
        else:
            self.name = name
        self.object_id = obj.id

    def __call__(self, **kwargs):
        smap = getattr(SessionContext._sessions, "smap", None)
        if smap:
            session = smap.get(self.object_id)
            if session:
                # Session call
                return session(self.name, kwargs)
        # Direct call
        return open_sync_rpc(
            "sae",
            calling_service=config.script.calling_service
        ).script(
            self.object_id,
            self.name,
            kwargs,  # params
            None  # timeout
        )


class Session(object):
    def __init__(self, object_id, idle_timeout=None):
        self._object_id = object_id
        self._idle_timeout = idle_timeout or config.script.caller_timeout
        self._id = str(uuid.uuid4())
        self._hints = [None]
        self._pool = None

    def _get_hints(self):
        """
        Get activator address
        :param pool:
        :return:
        """
        try:
            svc = get_dcs().resolve_sync(
                "activator-%s" % self._pool,
                hint=self._hints[0]
            )
            self._hints[0] = svc
        except ResolutionError:
            raise RPCNoService("activator-%s" % self._pool)

    def __call__(self, name, args, timeout=None):
        # Call SAE for credentials
        data = open_sync_rpc(
            "sae",
            calling_service=CALLING_SERVICE
        ).get_credentials(self._object_id)
        self._pool = data["pool"]
        # Get activator hints
        self._get_hints()
        # Call activator
        return open_sync_rpc(
            "activator",
            pool=data["pool"],
            calling_service=CALLING_SERVICE,
            hints=self._hints
        ).script(
            "%s.%s" % (data["profile"], name),
            data["credentials"],
            data["capabilities"],
            data["version"],
            args,
            timeout,
            self._id,
            self._idle_timeout
        )

    def close(self):
        if not self._hints[0]:
            return  # Not open
        open_sync_rpc(
            "activator",
            pool=self._pool,
            calling_service=CALLING_SERVICE,
            hints=self._hints
        ).close_session(self._id)


class SessionContext(object):
    # Thread-local storage holding session context for threads
    _sessions = threading.local()

    def __init__(self, object, idle_timeout=None):
        self._object_id = object.id
        self._idle_timeout = idle_timeout

    def __enter__(self):
        # Store previous context for object, if nested
        smap = getattr(self._sessions, "smap", None)
        if not smap:
            # Create dictionary in TLS
            smap = {}
            self._sessions.smap = smap
        self._prev_context = smap.get(self._object_id)
        # Put current context
        smap[self._object_id] = Session(self._object_id, self._idle_timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        session = self._sessions.smap.pop(self._object_id)
        if self._prev_context:
            # Restore previous context
            self._sessions.smap[self._object_id] = self._prev_context
        session.close()
