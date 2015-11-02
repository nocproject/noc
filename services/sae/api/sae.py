# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SAE API
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from django.db import connection
from django.db import transaction
import tornado.gen
## NOC modules
from noc.core.service.api import API, APIError, api
from noc.core.script.loader import loader
from noc.core.service.rpc import RPCError
from noc.sa.models.objectcapabilities import ObjectCapabilities


class SAEAPI(API):
    """
    Monitoring API
    """
    name = "sae"

    @api
    @tornado.gen.coroutine
    def script(self, object_id, script, args=None, timeout=None):
        """
        Execute SA script against ManagedObject
        :param object: Managed Object id
        :param script: Script name (Eighter with or without profile)
        :param args: Dict with input arguments
        :param timeout: Script timeout in seconds
        """
        object_id = int(object_id)
        # Get Object's attributes
        with transaction.autocommit():
            cursor = connection.cursor()
            cursor.execute("""
                SELECT
                    name, is_managed, profile_name,
                    scheme, address, port, "user", password,
                    super_password, remote_path,
                    snmp_ro, pool
                FROM sa_managedobject
                WHERE id=%s
            """, [object_id])
            data = cursor.fetchall()
            if not data:
                raise APIError("Object is not found")
            (name, is_managed, profile_name,
             scheme, address, port, user, password,
             super_password, remote_path,
             snmp_ro, pool_id) = data[0]
            cursor.execute("""
                SELECT key, value
                FROM sa_managedobjectattribute
                WHERE managed_object_id=%s
            """, [object_id])
            attributes = dict(cursor.fetchall())
        # Check object is managed
        if not is_managed:
            raise APIError("Object is not managed")
        # Find pool name
        pool = self.service.get_pool_name(pool_id)
        if not pool:
            raise APIError("Pool not found")
        # Check script is exists
        script_name = "%s.%s" % (profile_name, script)
        if not loader.has_script(script_name):
            raise APIError("Invalid script")
        # Build credentials
        credentials = {
            "address": address,
            "user": user,
            "password": password,
            "super_password": super_password,
            "path": remote_path
        }
        if snmp_ro:
            credentials["snmp_version"] = "v2c"
            credentials["snmp_ro"] = snmp_ro
        if scheme in (1, 2):
            credentials["cli_protocol"] = {
                1: "telnet",
                2: "ssh"
            }[scheme]
            if port:
                credentials["cli_port"] = port
        # Build version
        if ("vendor" in attributes and "platform" in attributes
            and "version" in attributes):
            version = {
                "vendor": attributes["vendor"],
                "platform": attributes["platform"],
                "version": attributes["version"]
            }
        else:
            version = None
        # Build capabilities
        oc = ObjectCapabilities.objects.filter(object=object_id).first()
        if oc:
            capabilities = {}
            for c in oc.caps:
                v = c.local_value if c.local_value is not None else c.discovered_value
                if v is None:
                    continue
                capabilities[c.capability.name] = v
        else:
            capabilities = {}
        # Pass call to activator
        activator = self.service.get_activator(pool)
        script_name = "%s.%s" % (profile_name, script)
        try:
            result = yield activator.script(
                script_name, credentials, capabilities, version, timeout
            )
        except RPCError, why:
            raise APIError("RPC Error: %s" % why)
        raise tornado.gen.Return(result)
