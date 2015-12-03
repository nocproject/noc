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
from collections import namedtuple
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

    ObjectData = namedtuple(
        "ObjectData",
        ["profile", "pool_id",
         "credentials", "capabilities", "version"]
    )

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
        # Resolve object data
        data = yield self.service.get_executor("db").submit(
            self.get_object_data, object_id
        )
        # Find pool name
        pool = self.service.get_pool_name(data.pool_id)
        if not pool:
            raise APIError("Pool not found")
        # Pass call to activator
        activator = self.service.get_activator(pool)
        # Check script is exists
        script_name = "%s.%s" % (data.profile, script)
        if not loader.has_script(script_name):
            raise APIError("Invalid script")
        # Pass call
        try:
            result = yield activator.script(
                script_name, data.credentials, data.capabilities,
                data.version, timeout
            )
        except RPCError, why:
            raise APIError("RPC Error: %s" % why)
        raise tornado.gen.Return(result)

    @transaction.autocommit
    def get_object_data(self, object_id):
        """
        Worker to resolve
        """
        object_id = int(object_id)
        # Get Object's attributes
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                mo.name, mo.is_managed, mo.profile_name,
                mo.scheme, mo.address, mo.port, mo."user",
                mo.password,
                mo.super_password, mo.remote_path,
                mo.snmp_ro, mo.pool,
                mo.auth_profile_id,
                ap.user, ap.password, ap.super_password,
                ap.snmp_ro, ap.snmp_rw
            FROM
                sa_managedobject mo
                LEFT JOIN sa_authprofile ap
                    ON (mo.auth_profile_id = ap.id)
            WHERE mo.id=%s
        """, [object_id])
        data = cursor.fetchall()
        if not data:
            raise APIError("Object is not found")
        (name, is_managed, profile_name,
         scheme, address, port, user, password,
         super_password, remote_path,
         snmp_ro, pool_id,
         auth_profile_id,
         ap_user, ap_password, ap_super_password,
         ap_snmp_ro, ap_snmp_rw) = data[0]
        # Get attributes
        cursor.execute("""
            SELECT key, value
            FROM sa_managedobjectattribute
            WHERE managed_object_id=%s
        """, [object_id])
        attributes = dict(cursor.fetchall())
        # Check object is managed
        if not is_managed:
            raise APIError("Object is not managed")
        if auth_profile_id:
            user = ap_user
            password = ap_password
            super_password = ap_super_password
            snmp_ro = ap_snmp_ro
            snmp_rw = ap_snmp_rw
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
        return self.ObjectData(
            profile=profile_name,
            pool_id=pool_id,
            credentials=credentials,
            capabilities=capabilities,
            version=version
        )
