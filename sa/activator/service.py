# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Activator RPC Service
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python services
import cPickle
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
                        self.code_to_scheme(request.access_profile.scheme),
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
        self.activator.run_script(request.script, request.access_profile,
                                  script_callback, request.timeout, **kwargs)

    def ping_check(self, controller, request, done):
        """
        Start ping check of addresses
        """
        def ping_check_callback(unreachable):
            u = set(unreachable)
            r = PingCheckResponse()
            for a in request.addresses:
                if a in u:
                    r.unreachable.append(a)
                else:
                    r.reachable.append(a)
            done(controller, response=r)
        self.activator.ping_check([a for a in request.addresses],
                                  ping_check_callback)

    def refresh_object_mappings(self, controller, request, done):
        """
        Request event filter refresh
        """
        self.activator.refresh_object_mappings()
        done(controller, response=RefreshEventFilterResponse())
