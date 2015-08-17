# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Activator RPC Service
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python services
import cPickle
import time
## NOC modules
from noc.sa.protocols.sae_pb2 import *
from noc.sa.profiles import profile_registry
from noc.sa.script import script_registry


class Service(SAEService):
    def ping(self, controller, request, done):
        """
        Stream ping.
        """
        done(controller, response=PingResponse())

    def script(self, controller, request, done):
        """
        Run script
        """
        def script_callback(script):
            """
            Respond with script result
            """
            if script.result:
                c = ScriptResponse()
                c.result = script.result
                done(controller, response=c)
            else:
                if script.e_timeout:
                    e = Error(code=ERR_TIMEOUT, text="Timed out")
                elif script.e_cancel:
                    e = Error(code=ERR_CANCELLED, text="Cancelled")
                elif script.e_not_supported:
                    e = Error(code=ERR_NOT_SUPPORTED,
                              text="Feature is not supported on this platform")
                elif script.login_error is not None:
                    e = Error(code=ERR_LOGIN_FAILED, text=script.login_error)
                elif script.e_http_error:
                    e = Error(code=ERR_HTTP_ERROR, text=script.e_http_error)
                else:
                    if script.error_traceback:
                        text = script.error_traceback
                    else:
                        text = "Unknown exception"
                    e = Error(code=ERR_SCRIPT_EXCEPTION, text=text)
                done(controller, error=e)

        try:
            profile = profile_registry[request.access_profile.profile]
        except KeyError:
            e = Error(code=ERR_INVALID_PROFILE,
                      text="Invalid profile '%s'" % request.access_profile.profile)
            done(controller, error=e)
            return
        try:
            script_class = script_registry[request.script]
        except KeyError:
            e = Error(code=ERR_INVALID_SCRIPT,
                      text="Invalid script '%s'" % request.script)
            done(controller, error=e)
            return
        # Check profile supports access scheme
        if request.access_profile.scheme not in profile.supported_schemes:
            e = Error(code=ERR_INVALID_SCHEME,
                      text="Access scheme '%s' is not supported for profile '%s'" % (
                        request.access_profile.scheme,
                        request.access_profile.profile))
            done(controller, error=e)
            return
        # Check [activator]/max_scripts limit
        if not self.activator.can_run_script():
            e = Error(code=ERR_OVERLOAD,
                      text="script concurrent session limit reached")
            done(controller, error=e)
            return
        # Deserialize additional arguments
        kwargs = {}
        for a in request.kwargs:
            kwargs[str(a.key)] = cPickle.loads(str(a.value))
        self.activator.run_script(request.object_name, request.script,
            request.access_profile, script_callback, request.timeout,
            **kwargs)

    def get_status(self, controller, request, done):
        status = self.activator.get_status()
        r = StatusResponse()
        r.timestamp = status["timestamp"]
        r.pool = status["pool"]
        r.instance = status["instance"]
        r.state = status["state"]
        r.last_state_change = status["last_state_change"]
        r.max_scripts = status["max_scripts"]
        r.current_scripts = status["current_scripts"]
        r.scripts_processed = status["scripts_processed"]
        r.scripts_failed = status["scripts_failed"]
        for s in status["scripts"]:
            i = r.scripts.add()
            i.script = s["script"]
            i.address = s["address"]
            i.object_name = s["object_name"]
            i.start_time = s["start_time"]
            i.timeout = s["timeout"]
        done(controller, response=r)
