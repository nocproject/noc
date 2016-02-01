# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Activator API
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python module
import socket
## Third-party modules
import tornado.gen
import tornado.httpclient
## NOC modules
from noc.core.service.api import API, APIError, api, executor
from noc.core.script.loader import loader
from noc.core.ioloop.snmp import snmp_get, SNMPError


class ActivatorAPI(API):
    """
    Monitoring API
    """
    name = "activator"

    @api
    @executor("script")
    def script(self, name, credentials,
               capabilities=None,
               version=None,
               args=None,
               timeout=None):
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
        """
        script_class = loader.get_script(name)
        if not script_class:
            raise APIError("Invalid script: %s" % name)
        script = script_class(
            service=self.service,
            credentials=credentials,
            args=args,
            capabilities=capabilities,
            version=version,
            timeout=timeout,
            name=name
        )
        try:
            result = script.run()
        except script.ScriptError, why:
            raise APIError("Script error: %s" % why.__doc__)
        return result

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
        self.logger.debug("SNMP GET %s %s", address, oid)
        try:
            result = yield snmp_get(
                address=address,
                oids=oid,
                community=community,
                tos=self.service.config.tos,
                ioloop=self.service.ioloop
            )
            self.logger.debug("SNMP GET %s %s returns %s",
                              address, oid, result)
        except SNMPError, why:
            result = None
            self.logger.debug("SNMP GET %s %s returns error %s",
                              address, oid, why)
        raise tornado.gen.Return(result)

    @api
    @tornado.gen.coroutine
    def http_get(self, url):
        """
        Perform HTTP/HTTPS get and return result
        :param url: Request URL
        :returns" Result as a string, or None in case of errors
        """
        self.logger.debug("HTTP GET %s", url)
        client = tornado.httpclient.AsyncHTTPClient()
        result = None
        try:
            response = yield client.fetch(
                url,
                follow_redirects=True,
                validate_cert=False
            )
            result = response.body
        except (tornado.httpclient.HTTPError, socket.error) as e:
            self.logger.debug("HTTP GET %s failed: %s", e)
        raise tornado.gen.Return(result)
