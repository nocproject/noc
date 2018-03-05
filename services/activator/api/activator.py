# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Activator API
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import tornado.gen
# NOC modules
from noc.core.service.api import API, APIError, api, executor
from noc.core.script.loader import loader
from noc.core.script.base import BaseScript
from noc.core.ioloop.snmp import snmp_get, SNMPError
from noc.core.snmp.version import SNMP_v1, SNMP_v2c
from noc.core.http.client import fetch
from noc.config import config


class ActivatorAPI(API):
    """
    Monitoring API
    """
    name = "activator"

    HTTP_CLIENT_DEFAULTS = dict(
        connect_timeout=config.activator.http_connect_timeout,
        request_timeout=config.activator.http_request_timeout
    )

    @api
    @executor("script")
    def script(self, name, credentials,
               capabilities=None,
               version=None,
               args=None,
               timeout=None,
               session=None,
               session_idle_timeout=None,
               ):
        """
        Execute SA script
        :param name: Script name (with profile)
        :param credentials:
            Dict containing following fields
            * cli_protocol - CLI protocol (telnet, ssh)
            * address - IP address
            * cli_port (optional) - Non-standard CLI port
            * user (optional) - Login as user
            * password (optional) - User password
            * super_password (optional) - Enable password
            * snmp_version (optional) - Use SNMP version (None, v2c)
            * snmp_ro (optional) - Use SNMP R/O community
            * path (optional) - unstructured path
        :param capabilities: Dict of discovered capabilities
        :param version: Dict of discovered version
        :param timeout: Script timeout, in seconds
        :param session: Unique session id to share CLI stream
        :param session_idle_timeout: Hold CLI stream up to
            session_idle_timeout seconds after script completion
        """
        script_class = loader.get_script(name)
        if not script_class:
            self.service.perf_metrics["error", ("type", "invalid_script")] += 1
            raise APIError("Invalid script: %s" % name)
        script = script_class(
            service=self.service,
            credentials=credentials,
            args=args,
            capabilities=capabilities,
            version=version,
            timeout=timeout,
            name=name,
            session=session,
            session_idle_timeout=session_idle_timeout
        )
        try:
            result = script.run()
        except script.ScriptError as e:
            self.service.perf_metrics["error", ("type", "script_error")] += 1
            raise APIError("Script error: %s" % e.__doc__)
        return result

    @staticmethod
    def script_get_label(name, credentials, *args, **kwargs):
        return "%s %s" % (name, credentials.get("address", "-"))

    @api
    @tornado.gen.coroutine
    def snmp_v1_get(self, address, community, oid):
        """
        Perform SNMP v1 GET and return result
        :param address: IP address
        :param community: SNMP v2c community
        :param oid: Resolved oid
        :returns: Result as a string, or None, when no response
        """
        self.logger.debug("SNMP v1 GET %s %s", address, oid)
        try:
            result = yield snmp_get(
                address=address,
                oids=oid,
                community=community,
                version=SNMP_v1,
                tos=config.activator.tos,
                ioloop=self.service.ioloop
            )
            self.logger.debug("SNMP GET %s %s returns %s",
                              address, oid, result)
        except SNMPError as e:
            self.service.perf_metrics["error", ("type", "snmp_v1_error")] += 1
            result = None
            self.logger.debug("SNMP GET %s %s returns error %s",
                              address, oid, e)
        raise tornado.gen.Return(result)

    @staticmethod
    def snmp_v1_get_get_label(address, community, oid):
        return "%s %s" % (address, oid)

    @api
    @tornado.gen.coroutine
    def snmp_v2c_get(self, address, community, oid):
        """
        Perform SNMP v2c GET and return result
        :param address: IP address
        :param community: SNMP v2c community
        :param oid: Resolved oid
        :returns: Result as a string, or None, when no response
        """
        self.logger.debug("SNMP v2c GET %s %s", address, oid)
        try:
            result = yield snmp_get(
                address=address,
                oids=oid,
                community=community,
                version=SNMP_v2c,
                tos=config.activator.tos,
                ioloop=self.service.ioloop
            )
            self.logger.debug("SNMP GET %s %s returns %s",
                              address, oid, result)
        except SNMPError as e:
            self.service.perf_metrics["error", ("type", "snmp_v2_error")] += 1
            result = None
            self.logger.debug("SNMP GET %s %s returns error %s",
                              address, oid, e)
        raise tornado.gen.Return(result)

    @staticmethod
    def snmp_v2_get_get_label(address, community, oid):
        return "%s %s" % (address, oid)

    @api
    @tornado.gen.coroutine
    def http_get(self, url):
        """
        Perform HTTP/HTTPS get and return result
        :param url: Request URL
        :returns" Result as a string, or None in case of errors
        """
        self.logger.debug("HTTP GET %s", url)
        code, header, body = yield fetch(
            url,
            request_timeout=config.activator.http_request_timeout,
            follow_redirects=True,
            validate_cert=config.activator.http_validate_cert,
            eof_mark="</html>"
        )
        if 200 <= code <= 299:
            raise tornado.gen.Return(body)
        else:
            self.service.perf_metrics["error", ("type", "http_error_%s" % code)] += 1
            self.logger.debug("HTTP GET %s failed: %s %s", url, code, body)
            raise tornado.gen.Return(None)

    @staticmethod
    def http_get_get_label(url):
        return "%s" % url

    @api
    @executor("script")
    def close_session(self, session_id):
        BaseScript.close_session(session_id)

    @staticmethod
    def close_session_get_label(session_id):
        return session_id
