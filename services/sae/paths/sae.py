# ---------------------------------------------------------------------
# SAE API
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.core.service.jsonrpcapi import JSONRPCAPI, APIError, api
from noc.core.script.loader import loader
from noc.core.script.scheme import CLI_PROTOCOLS, HTTP_PROTOCOLS, PROTOCOLS, BEEF
from noc.sa.models.managedobject import (
    ManagedObject,
    CREDENTIAL_CACHE_VERSION,
)  # noqa Do not delete
from noc.sa.models.profile import Profile
from noc.inv.models.vendor import Vendor
from noc.inv.models.capability import Capability
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.main.models.template import Template
from noc.main.models.extstorage import ExtStorage
from noc.wf.models.state import State
from noc.core.wf.interaction import Interaction
from noc.core.cache.decorator import cachedmethod
from noc.core.dcs.base import ResolutionError
from noc.config import config
from noc.core.perf import metrics

# Increase whenever new field added or removed
CREDENTIALS_CACHE_VERSION = 3

router = APIRouter()


class SAEAPI(JSONRPCAPI):
    """
    SAE API
    """

    api_name = "api_sae"
    api_description = "Service SAE API"
    openapi_tags = ["JSON-RPC API"]
    url_path = "/api/sae"
    auth_required = False

    RUN_SQL = """
        SELECT
            mo.name, mo.profile,
            mo.vendor, mo.platform, mo.version,
            mo.scheme, mo.address, mo.port,
            mo."user", mo.password, mo.super_password, mo.remote_path,
            mo.snmp_ro, mo.pool, mo.software_image,
            mo.auth_profile_id,
            ap.user, ap.password, ap.super_password,
            ap.snmp_ro, ap.snmp_rw, ap.preferred_profile_credential,
            mo.cli_privilege_policy, mo.snmp_rate_limit,
            mop.cli_privilege_policy, mop.snmp_rate_limit,
            mo.access_preference, mop.access_preference,
            mop.beef_storage, mop.beef_path_template_id,
            mo.caps, mo.diagnostics, mo.state, mo.controller_id,
            mo.snmp_security_level, mo.snmp_username, mo.snmp_auth_proto,
            mo.snmp_auth_key, mo.snmp_priv_proto, mo.snmp_priv_key,
            mo.snmp_ctx_name,
            ap.snmp_security_level, ap.snmp_username, ap.snmp_auth_proto,
            ap.snmp_auth_key, ap.snmp_priv_proto, ap.snmp_priv_key,
            ap.snmp_ctx_name
        FROM
            sa_managedobject mo
            JOIN sa_managedobjectprofile mop ON (mo.object_profile_id = mop.id)
            LEFT JOIN sa_authprofile ap ON (mo.auth_profile_id = ap.id)
        WHERE mo.id = %s
    """

    async def resolve_activator(self, pool):
        sn = f"activator-{pool}"
        for i in range(config.sae.activator_resolution_retries):
            try:
                svc = await self.service.dcs.resolve(
                    sn, timeout=config.sae.activator_resolution_timeout
                )
                return svc
            except ResolutionError as e:
                self.logger.info("Cannot resolve %s: %s", sn, e)
                metrics["error", ("type", "resolve_activator")] += 1
        return None

    async def get_activator_url(self, pool):
        svc = await self.resolve_activator(pool)
        if svc:
            return f"http://{svc}/api/activator/"
        else:
            metrics["error", ("type", "empty_activator_list_response")] += 1
            return None

    @api
    async def script(
        self, object_id, script, args=None, timeout=None, streaming=None, return_metrics=False
    ):
        """
        Execute SA script against ManagedObject
        :param object_id: Managed Object id
        :param script: Script name (Either with or without profile)
        :param args: Dict with input arguments
        :param timeout: Script timeout in seconds
        :param streaming: Send script result to stream
        :param return_metrics: Return execution metrics with result
        """
        # Resolve object data
        data = self.get_object_data(object_id)
        # Find pool name
        pool = self.service.get_pool_name(data["pool_id"])
        if not pool:
            metrics["error", ("type", "pool_not_found")] += 1
            raise APIError("Pool not found")
        # Check script is exists
        script_name = f'{data["profile"]}.{script}'
        if not loader.has_script(script_name):
            metrics["error", ("type", "invalid_scripts_request")] += 1
            raise APIError("Invalid script")
        #
        url = await self.get_activator_url(pool)
        if not url:
            raise APIError(f"No active activators for pool '{pool}'")
        return self.redirect(
            url,
            "script",
            [
                script_name,
                data["credentials"],
                data["capabilities"],
                data["version"],
                args,
                timeout,
                None,  # session
                None,  # session_timeout
                streaming,
                return_metrics,
                data["controller"],
            ],
        )

    @api
    async def get_credentials(self, object_id):
        # Resolve object data
        data = self.get_object_data(object_id)
        # Find pool name
        pool = self.service.get_pool_name(data["pool_id"])
        if not pool:
            metrics["error", ("type", "pool_not_found")] += 1
            raise APIError("Pool not found")
        data["pool"] = pool
        return data

    @cachedmethod(key="cred-%s", version=CREDENTIAL_CACHE_VERSION)
    def get_object_data(self, object_id):
        """
        Worker to resolve credentials
        """
        object_id = int(object_id)
        # Get Object's attributes
        with self.service.get_pg_connect() as connection:
            cursor = connection.cursor()
            cursor.execute(self.RUN_SQL, [object_id])
            data = cursor.fetchall()
        if not data:
            metrics["error", ("type", "object_not_found")] += 1
            raise APIError("Object is not found")
        # Get object credentials
        (
            name,
            profile,
            vendor,
            platform,
            version,
            scheme,
            address,
            port,
            user,
            password,
            super_password,
            remote_path,
            snmp_ro,
            pool_id,
            sw_image,
            auth_profile_id,
            ap_user,
            ap_password,
            ap_super_password,
            ap_snmp_ro,
            ap_snmp_rw,
            ap_preferred_profile_credential,
            privilege_policy,
            o_snmp_rate_limit,
            p_privilege_policy,
            p_snmp_rate_limit,
            o_access_preference,
            p_access_preference,
            beef_storage_id,
            beef_path_template_id,
            caps,
            diagnostics,
            state,
            controller,
            snmp_security_level,
            snmp_username,
            snmp_auth_proto,
            snmp_auth_key,
            snmp_priv_proto,
            snmp_priv_key,
            snmp_ctx_name,
            ap_snmp_security_level,
            ap_snmp_username,
            ap_snmp_auth_proto,
            ap_snmp_auth_key,
            ap_snmp_priv_proto,
            ap_snmp_priv_key,
            ap_snmp_ctx_name,
        ) = data[0]
        # Check object is managed
        state = State.get_by_id(state)
        if not state.is_enabled_interaction(Interaction.ServiceActivation):
            metrics["error", ("type", "object_not_managed")] += 1
            raise APIError("Object is not managed")
        # Build capabilities
        capabilities = {}
        if caps:
            for c in caps:
                cc = Capability.get_by_id(c["capability"])
                if cc and not c.get("scope"):
                    capabilities[cc.name] = c.get("value")
        if auth_profile_id and ap_preferred_profile_credential:
            user = ap_user
            password = ap_password
            super_password = ap_super_password
            snmp_ro = ap_snmp_ro
            snmp_rw = ap_snmp_rw  # noqa just to be
            snmp_security_level = ap_snmp_security_level
            snmp_username = ap_snmp_username
            snmp_auth_proto = ap_snmp_auth_proto
            snmp_auth_key = ap_snmp_auth_key
            snmp_priv_proto = ap_snmp_priv_proto
            snmp_priv_key = ap_snmp_priv_key
            snmp_ctx_name = ap_snmp_ctx_name
        #
        if privilege_policy == "E":
            raise_privileges = True
        elif privilege_policy == "P":
            raise_privileges = p_privilege_policy == "E"
        else:
            raise_privileges = False
        access_preference = o_access_preference
        if o_access_preference == "P":
            access_preference = p_access_preference
        snmp_rate_limit = o_snmp_rate_limit
        if not o_snmp_rate_limit:
            snmp_rate_limit = p_snmp_rate_limit
        # Build credentials
        credentials = {
            "name": name,
            "address": address,
            "user": user,
            "password": password,
            "super_password": super_password,
            "path": remote_path,
            "raise_privileges": raise_privileges,
            "access_preference": access_preference,
            "snmp_rate_limit": snmp_rate_limit,
        }
        if snmp_ro:
            credentials["snmp_ro"] = snmp_ro
            if capabilities.get("SNMP | v2c"):
                credentials["snmp_version"] = "v2c"
            elif capabilities.get("SNMP | v1"):
                credentials["snmp_version"] = "v1"
        # Bild security level SNMPv3
        if snmp_username and snmp_security_level != "Community":
            if capabilities.get("SNMP | v3"):
                credentials["snmp_version"] = "v3"
            credentials["snmp_username"] = snmp_username
            credentials["snmp_ctx_name"] = snmp_ctx_name
            if snmp_security_level == "authNoPriv":
                credentials["snmp_auth_proto"] = snmp_auth_proto
                credentials["snmp_auth_key"] = snmp_auth_key
            elif snmp_security_level == "authPriv":
                credentials["snmp_auth_proto"] = snmp_auth_proto
                credentials["snmp_auth_key"] = snmp_auth_key
                credentials["snmp_priv_proto"] = snmp_priv_proto
                credentials["snmp_priv_key"] = snmp_priv_key
        if scheme in CLI_PROTOCOLS:
            credentials["cli_protocol"] = PROTOCOLS[scheme]
            if port:
                credentials["cli_port"] = port
        elif scheme in HTTP_PROTOCOLS:
            credentials["http_protocol"] = PROTOCOLS[scheme]
            if port:
                credentials["http_port"] = port
        # Build version
        if vendor and platform and version:
            vendor = Vendor.get_by_id(vendor)
            firmware = Firmware.get_by_id(version)
            version = {
                "vendor": vendor.code[0] if vendor.code else vendor.name,
                "platform": Platform.get_by_id(platform).name,
                "version": firmware.version,
            }
            if sw_image:
                version["image"] = sw_image
            # Apply firmware policy discovery settings
            fws = firmware.get_effective_object_settings()
            if o_access_preference == "P" and "access_preference" in fws:
                credentials["access_preference"] = fws["access_preference"]
            if o_access_preference == "P" and "snmp_rate_limit" in fws:
                credentials["snmp_rate_limit"] = fws["snmp_rate_limit"]
        else:
            version = None
        # Beef processing
        if scheme == BEEF and beef_storage_id and beef_path_template_id:
            mo = ManagedObject.get_by_id(object_id)
            tpl = Template.get_by_id(beef_path_template_id)
            beef_path = tpl.render_subject(object=mo)
            if beef_path:
                storage = ExtStorage.get_by_id(beef_storage_id)
                credentials["beef_storage_url"] = storage.url
                credentials["beef_path"] = beef_path
        # Controller processing
        if controller:
            controller = ManagedObject.get_by_id(controller)
        return dict(
            profile=Profile.get_by_id(profile).name,
            pool_id=pool_id,
            credentials=credentials,
            capabilities=capabilities,
            version=version,
            controller=controller.get_controller_credentials() if controller else None,
        )


# Install endpoints
SAEAPI(router)
