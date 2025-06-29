# ---------------------------------------------------------------------
# Activator API
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any, List
from collections import defaultdict

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.core.service.jsonrpcapi import JSONRPCAPI, APIError, api, executor
from noc.core.script.loader import loader
from noc.core.script.base import BaseScript
from noc.core.ioloop.snmp import snmp_get, SNMPError
from noc.core.snmp.version import SNMP_v1, SNMP_v2c
from noc.core.http.async_client import HttpClient
from noc.core.comp import DEFAULT_ENCODING, smart_text
from noc.core.perf import metrics
from noc.core.debug import error_report
from noc.core.checkers.loader import loader as checker_loader
from noc.core.checkers.base import Check, CheckResult
from noc.config import config
from noc.core.jsonutils import iter_chunks
from ..models.streaming import StreamingConfig
from ..models.controller import ControllerConfig

router = APIRouter()


class ActivatorAPI(JSONRPCAPI):
    """
    Monitoring API
    """

    api_name = "api_activator"
    api_description = "Service Activator API"
    openapi_tags = ["JSON-RPC API"]
    url_path = "/api/activator"
    auth_required = False

    HTTP_CLIENT_DEFAULTS = dict(
        connect_timeout=config.activator.http_connect_timeout,
        request_timeout=config.activator.http_request_timeout,
    )

    @api
    @executor("script")
    def script(
        self,
        name: str,
        credentials,
        capabilities=None,
        version=None,
        args: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        session: Optional[str] = None,
        session_idle_timeout: Optional[int] = None,
        streaming: Optional[StreamingConfig] = None,
        return_metrics: bool = False,
        controller: Optional[ControllerConfig] = None,
    ):
        """
        Execute SA script
        Args:
            name: Script name (with profile)
            credentials:
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
                    * snmp_rate_limit (optional) - limit of outgoing snmp requests (float, in requests per second)
            capabilities: Dict of discovered capabilities
            version: Dict of discovered version
            timeout: Script timeout, in seconds
            session: Unique session id to share CLI stream
            session_idle_timeout: Hold CLI stream up to
            session_idle_timeout seconds after script completion
            streaming: Send result to stream for processed on service
            return_metrics: Return execution metrics
            controller: Controller device credential for execute script
        """
        script_class = loader.get_script(name)
        if not script_class:
            metrics["error", ("type", "invalid_script")] += 1
            raise APIError(f"Invalid script: {name}")
        if streaming:
            streaming = StreamingConfig(**streaming)
        if controller:
            controller = ControllerConfig(**controller)
        script = script_class(
            service=self.service,
            credentials=credentials,
            args=args,
            capabilities=capabilities,
            version=version,
            timeout=timeout,
            name=name,
            session=session,
            session_idle_timeout=session_idle_timeout,
            streaming=streaming,
            controller=controller,
        )
        try:
            result = script.run()
        except script.ScriptError as e:
            metrics["error", ("type", "script_error")] += 1
            raise APIError("Script error: %s" % e.__doc__)
        if not streaming or not result:
            if return_metrics:
                return {"metrics": script.apply_metrics({}), "result": result}
            return result
        # Split large result
        for d in iter_chunks(result, max_size=config.msgstream.max_message_size):
            self.service.publish(
                value=d,
                stream=streaming.stream,
                partition=streaming.partition,
                headers={},
            )
        return {"metrics": script.apply_metrics({}), "result": []}

    @staticmethod
    def script_get_label(name: str, credentials, *args, **kwargs):
        return f'{name} {credentials.get("address", "-")}'

    @api
    async def snmp_v1_get(
        self,
        address: str,
        community: str,
        oid: str,
        timeout: Optional[int] = 10,
        return_error: bool = False,
    ):
        """
        Perform SNMP v1 GET and return result
        Args:
            address: IP address
            community: SNMP v2c community
            oid: Resolved oid
            timeout: Timeout request
            return_error:
        Returns:
            Result as a string, or None, when no response
        """
        self.logger.debug("SNMP v1 GET %s %s", address, oid)
        message = ""
        try:
            result = await snmp_get(
                address=address,
                oids=oid,
                community=community,
                version=SNMP_v1,
                tos=config.activator.tos,
                timeout=timeout,
            )
            result = smart_text(result, errors="replace") if result else result
            self.logger.debug("SNMP GET %s %s returns %s", address, oid, result)
        except SNMPError as e:
            metrics["error", ("type", "snmp_v1_error")] += 1
            result, message = None, repr(e)
            self.logger.debug("SNMP GET %s %s returns error %s", address, oid, e)
        except Exception as e:
            result, message = None, str(e)
            self.logger.debug("SNMP GET %s %s returns unknown error %s", address, oid, e)
        if return_error:
            return result, message
        return result

    @staticmethod
    def snmp_v1_get_get_label(address: str, community: str, oid: str):
        return f"{address} {oid}"

    @api
    async def snmp_v2c_get(
        self,
        address: str,
        community: str,
        oid: str,
        timeout: Optional[int] = 10,
        return_error: bool = False,
    ):
        """
        Perform SNMP v2c GET and return result
        Args:
            address: IP address
            community: SNMP v2c community
            oid: Resolved oid
            timeout: Timeout request
            return_error:
        Returns:
            Result as a string, or None, when no response
        """
        self.logger.debug("SNMP v2c GET %s %s", address, oid)
        message = ""
        try:
            result = await snmp_get(
                address=address,
                oids=oid,
                community=community,
                version=SNMP_v2c,
                tos=config.activator.tos,
                timeout=timeout,
            )
            self.logger.debug("SNMP GET %s %s returns %s", address, oid, result)
            result = smart_text(result, errors="replace") if result else result
        except SNMPError as e:
            metrics["error", ("type", "snmp_v2_error")] += 1
            result, message = None, repr(e)
            self.logger.debug("SNMP GET %s %s returns error %s", address, oid, e)
        except Exception as e:
            result, message = None, str(e)
            self.logger.debug("SNMP GET %s %s returns unknown error %s", address, oid, e)
        if return_error:
            return result, message
        return result

    @staticmethod
    def snmp_v2_get_get_label(address: str, community: str, oid: str):
        return f"{address} {oid}"

    @api
    async def snmp_v3_get(
        self,
        address: str,
        username: str,
        oid: str,
        auth_proto: Optional[str] = None,
        auth_key: Optional[str] = None,
        priv_proto: Optional[str] = None,
        priv_key: Optional[str] = None,
        timeout: Optional[int] = 10,
        return_error: bool = False,
    ):
        """
        Perform SNMP v3 GET and return result
        Args:
            address: IP address
            username: SNMP v3 username
            oid: Resolved oid
            auth_proto: SNMPv3 Authentication Protocol
            auth_key: SNMPv3 Authentication Key
            priv_key: SNMPv3 Private Key
            priv_proto: SNMPv3 Private Protocol: DES/AES
            timeout: Timeout request
            return_error:
        Returns:
            Result as a string, or None, when no response
        """
        from gufo.snmp import SnmpSession, SnmpVersion, SnmpError
        from gufo.snmp.user import User, Aes128Key, DesKey, Md5Key, Sha1Key, KeyType

        auth_proto_map = {"SHA": Sha1Key, "MD5": Md5Key}
        priv_proto_map = {"AES": Aes128Key, "DES": DesKey}
        self.logger.debug("SNMP v3 GET %s %s", address, oid)
        message = ""
        if auth_key and auth_proto in auth_proto_map:
            auth_key = auth_proto_map[auth_proto](
                auth_key.encode("utf-8"), key_type=KeyType.Password
            )
        if priv_key and priv_proto in priv_proto_map:
            priv_key = priv_proto_map[priv_proto](
                priv_key.encode("utf-8"), key_type=KeyType.Password
            )
        if auth_key and priv_key:
            user = User(name=username, auth_key=auth_key, priv_key=priv_key)
        elif auth_key:
            user = User(name=username, auth_key=auth_key)
        else:
            user = User(name=username)
        session = SnmpSession(
            addr=address,
            user=user,
            version=SnmpVersion.v3,
            tos=config.activator.tos,
            timeout=int(timeout),
        )
        try:
            await session.refresh()
            result = await session.get(oid)
            self.logger.debug("SNMP GET %s %s returns %s", address, oid, result)
            result = smart_text(result, errors="replace") if result else result
        except (SnmpError, TimeoutError) as e:
            metrics["error", ("type", "snmp_v3_error")] += 1
            result, message = None, repr(e)
            self.logger.debug("SNMP GET %s %s returns error %s", address, oid, e)
        except Exception as e:
            result, message = None, str(e)
            self.logger.debug("SNMP GET %s %s returns unknown error %s", address, oid, e)
        if return_error:
            return result, message
        return result

    @staticmethod
    def snmp_v3_get_get_label(address: str, community: str, oid: str):
        return f"{address} {oid}"

    @api
    async def http_get(self, url, ignore_errors=False):
        """
        Perform HTTP/HTTPS get and return result
        Args:
            url: Request URL
            ignore_errors: Ignore response error and return header and body
        Returns:
            Result as a string, or None in case of errors
        """
        self.logger.debug("HTTP GET %s", url)
        async with HttpClient(
            timeout=config.activator.http_request_timeout,
            validate_cert=config.activator.http_validate_cert,
        ) as client:
            code, headers, body = await client.get(url)
            if 200 <= code <= 299:
                return body.decode(DEFAULT_ENCODING, errors="replace")
            elif ignore_errors:
                metrics["error", ("type", f"http_error_{code}")] += 1
                self.logger.debug("HTTP GET %s failed: %s %s", url, code, body)
                return str(
                    {k: v.decode(DEFAULT_ENCODING, errors="replace") for k, v in headers.items()}
                ) + body.decode(DEFAULT_ENCODING, errors="replace")
            else:
                metrics["error", ("type", f"http_error_{code}")] += 1
                self.logger.debug("HTTP GET %s failed: %s %s", url, code, body)
                return None

    @api
    async def run_checks(self, checks, first_success: bool = False, **kwargs):
        """
        Run numbers of checks, and return result
        Args:
            checks: List of running checks
            first_success: Return first success check
            kwargs: Checker param
        """
        checks = [Check.from_dict(c) for c in checks]
        r: List[CheckResult] = []
        do_checks: Dict[str, List[Check]] = defaultdict(list)
        for check in checks:
            checker = checker_loader[check.name]
            if not checker:
                self.logger.warning("[%s] Unknown check. Skipping", check.name)
                continue
            do_checks[checker.name] += [check]
        for checker, d_checks in do_checks.items():
            checker = checker_loader[checker](**kwargs)
            self.logger.debug("[%s] Run checker", ";".join(f"{c.name}({c.arg0})" for c in d_checks))
            try:
                async for check in checker.iter_result(d_checks):
                    r.append(check)
                    if first_success and check.status:
                        break
            except Exception as e:
                metrics["error", ("type", "checker_error"), ("check", checker.name)] += 1
                # if self.logger.isEnabledFor(logging.DEBUG):
                error_report()
                self.logger.error("[%s] Error when run checker: %s", checker.name, str(e))
        return r

    @staticmethod
    def http_get_get_label(url):
        return f"{url}"

    @api
    @executor("script")
    def close_session(self, session_id):
        BaseScript.close_session(session_id)

    @staticmethod
    def close_session_get_label(session_id):
        return session_id


# Install endpoints
ActivatorAPI(router)
