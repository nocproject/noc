# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SAE API
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import tornado.gen
# NOC modules
from noc.core.service.api import API, APIError, api
from noc.core.script.loader import loader
from noc.sa.models.objectcapabilities import ObjectCapabilities
from noc.sa.models.profile import Profile
from noc.inv.models.vendor import Vendor
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.core.cache.decorator import cachedmethod
from noc.core.dcs.base import ResolutionError


class SAEAPI(API):
    """
    SAE API
    """
    name = "sae"

    ACTIVATOR_RESOLUTION_RETRIES = 5
    ACTIVATOR_RESOLUTION_TIMEOUT = 2

    RUN_SQL = """
        SELECT
            name, is_managed, profile,
            vendor, platform, version,
            scheme, address, port, "user",
            password,
            super_password, remote_path,
            snmp_ro, pool,
            auth_profile_id,
            ap.user, ap.password, ap.super_password,
            ap.snmp_ro, ap.snmp_rw
        FROM
            sa_managedobject
        WHERE id = %s
    """

    @tornado.gen.coroutine
    def resolve_activator(self, pool):
        sn = "activator-%s" % pool
        for i in range(self.ACTIVATOR_RESOLUTION_RETRIES):
            try:
                svc = yield self.service.dcs.resolve(
                    sn,
                    timeout=self.ACTIVATOR_RESOLUTION_TIMEOUT
                )
                raise tornado.gen.Return(svc)
            except ResolutionError as e:
                self.logger.info("Cannot resolve %s: %s", sn, e)
        raise tornado.gen.Return(None)

    @tornado.gen.coroutine
    def get_activator_url(self, pool):
        svc = yield self.resolve_activator(pool)
        if svc:
            raise tornado.gen.Return("http://%s/api/activator/" % svc)
        else:
            raise tornado.gen.Return(None)

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
        pool = self.service.get_pool_name(data["pool_id"])
        if not pool:
            raise APIError("Pool not found")
        # Check script is exists
        script_name = "%s.%s" % (data["profile"], script)
        if not loader.has_script(script_name):
            raise APIError("Invalid script")
        #
        url = yield self.get_activator_url(pool)
        if not url:
            raise APIError("No active activators for pool '%s'" % pool)
        self.redirect(
            url,
            "script",
            [script_name, data["credentials"], data["capabilities"],
             data["version"], args, timeout]
        )

    @api
    @tornado.gen.coroutine
    def get_credentials(self, object_id):
        # Resolve object data
        data = yield self.service.get_executor("db").submit(
            self.get_object_data, object_id
        )
        # Find pool name
        pool = self.service.get_pool_name(data["pool_id"])
        if not pool:
            raise APIError("Pool not found")
        data["pool"] = pool
        raise tornado.gen.Return(data)

    @cachedmethod(
        key="cred-%s"
    )
    def get_object_data(self, object_id):
        """
        Worker to resolve credentials
        """
        object_id = int(object_id)
        # Get Object's attributes
        with self.service.get_pg_connect() as connection:
            cursor = connection.cursor()
            cursor.execute(self.RUN_SQL, [object_id, object_id])
            data = cursor.fetchall()
        if not data:
            raise APIError("Object is not found")
        (name, is_managed, profile,
         vendor, platform, version,
         scheme, address, port, user, password,
         super_password, remote_path,
         snmp_ro, pool_id,
         auth_profile_id,
         ap_user, ap_password, ap_super_password,
         ap_snmp_ro, ap_snmp_rw) = data[0]
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
            "name": name,
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
        elif scheme in (3, 4):
            credentials["http_protocol"] = "https" if scheme == 4 else "http"
            if port:
                credentials["http_port"] = port
        # Build version
        if vendor and platform and version:
            version = {
                "vendor": Vendor.get_by_id(vendor).code,
                "platform": Platform.get_by_id(platform).name,
                "version": Firmware.get_by_id(version).version
            }
        else:
            version = None
        # Build capabilities
        capabilities = ObjectCapabilities.get_capabilities(object_id)
        return dict(
            profile=Profile.get_by_id(profile).name,
            pool_id=pool_id,
            credentials=credentials,
            capabilities=capabilities,
            version=version
        )
