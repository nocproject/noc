# ----------------------------------------------------------------------
# Profile checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import operator
import re
from collections import defaultdict
from threading import Lock
from typing import Optional, List, Dict, Tuple, Iterable

# Third-party modules
import cachetools
from pymongo import ReadPreference


# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.error import NOCError
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.sa.models.profile import Profile
from noc.sa.models.profilecheckrule import ProfileCheckRule
from noc.core.mib import mib
from noc.core.snmp.version import SNMP_v1, SNMP_v2c

rules_lock = Lock()


class ProfileChecker(object):
    base_logger = logging.getLogger("profilechecker")
    _rules_cache = cachetools.TTLCache(10, ttl=60)
    _re_cache = {}

    def __init__(
        self,
        address: Optional[str] = None,
        pool: Optional[str] = None,
        logger=None,
        snmp_community: Optional[str] = None,
        calling_service: str = "profilechecker",
        snmp_version: Optional[List[int]] = None,
    ):
        self.address = address
        self.pool = pool
        self.logger = PrefixLoggerAdapter(
            logger or self.base_logger, "%s][%s" % (self.pool or "", self.address or "")
        )
        self.result_cache: Dict[Tuple[str, str], str] = {}  # (method, param) -> result
        self.error: Optional[str] = None
        self.snmp_check: Optional[bool] = None
        self.snmp_community = snmp_community
        self.calling_service = calling_service
        self.snmp_version = snmp_version or [SNMP_v2c]
        self.ignoring_snmp = False
        if self.snmp_version is None:
            self.logger.error("SNMP is not supported. Ignoring")
            self.ignoring_snmp = True
        if not self.snmp_community:
            self.logger.error("No SNMP credentials. Ignoring")
            self.ignoring_snmp = True

    def find_profile(self, method: str, param: str, result: str) -> Optional[Profile]:
        """
        Find profile by method
        :param method: Fingerprint getting method
        :param param: Method params
        :param result: Getting params result
        :return:
        """
        r = defaultdict(list)
        d = self.get_rules()
        for k, value in sorted(d.items(), key=lambda x: x[0]):
            for v in value:
                r[v] += value[v]
        if (method, param) not in r:
            self.logger.warning("Not find rule for method: %s %s", method, param)
            return None
        for match_method, value, action, profile, rname in r[(method, param)]:
            if self.is_match(result, match_method, value):
                self.logger.info("Matched profile: %s (%s)", profile, rname)
                # @todo: process MAYBE rule
                return profile

    def get_profile(self) -> Optional[Profile]:
        """
        Returns profile for object, or None when not known
        """
        snmp_result = ""
        http_result = ""
        for ruleset in self.iter_rules():
            for (method, param), actions in ruleset:
                try:
                    result = self.do_check(method, param)
                    if not result:
                        continue
                    if "snmp" in method:
                        snmp_result = result
                    if "http" in method:
                        http_result = result
                    for match_method, value, action, profile, rname in actions:
                        if self.is_match(result, match_method, value):
                            self.logger.info("Matched profile: %s (%s)", profile, rname)
                            # @todo: process MAYBE rule
                            return profile
                except NOCError as e:
                    self.logger.error(e)
                    self.error = str(e)
                    return None
        if snmp_result or http_result:
            self.error = f"Not find profile for OID: {snmp_result} or HTTP string: {http_result}"
        elif not snmp_result:
            self.error = "Cannot fetch snmp data, check device for SNMP access"
        elif not http_result:
            self.error = "Cannot fetch HTTP data, check device for HTTP access"
        self.logger.info("Cannot detect profile: %s", self.error)
        return None

    def get_error(self) -> Optional[str]:
        """
        Get error message
        :return:
        """
        return self.error

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_rules_cache"), lock=lambda _: rules_lock)
    def get_profile_check_rules(cls):
        return list(
            ProfileCheckRule.objects.all()
            .read_preference(ReadPreference.SECONDARY_PREFERRED)
            .order_by("preference")
        )

    def get_rules(self) -> Dict[int, Dict[Tuple[str, str], List[Tuple[str, str, str, str, str]]]]:
        """
        Load ProfileCheckRules and return a list, grouped by preferences
        [{
            (method, param) -> [(
                    match_method,
                    value,
                    action,
                    profile,
                    rule_name
                ), ...]

        }]
        """
        self.logger.info('Compiling "Profile Check rules"')
        d = {}  # preference -> (method, param) -> [rule, ..]
        for r in self.get_profile_check_rules():
            if "snmp" in r.method and self.ignoring_snmp:
                continue
            if r.preference not in d:
                d[r.preference] = {}
            k = (r.method, r.param)
            if k not in d[r.preference]:
                d[r.preference][k] = []
            d[r.preference][k] += [(r.match_method, r.value, r.action, r.profile, r.name)]
        return d

    def iter_rules(
        self,
    ) -> Iterable[List[Tuple[Tuple[str, str], List[Tuple[str, str, str, str, str]]]]]:
        d = self.get_rules()
        for p in sorted(d):
            yield list(d[p].items())

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_re_cache"))
    def get_re(cls, regexp):
        return re.compile(regexp)

    def do_check(self, method: str, param: str) -> Optional[str]:
        """
        Perform check
        """
        self.logger.debug("do_check(%s, %s)", method, param)
        if (method, param) in self.result_cache:
            self.logger.debug("Using cached value")
            return self.result_cache[method, param]
        h = getattr(self, f"check_{method}", None)
        if not h:
            self.logger.error("Invalid check method '%s'. Ignoring", method)
            return None
        result = h(param)
        self.result_cache[method, param] = result
        return result

    def check_snmp_v2c_get(self, param):
        """
        Perform SNMP v2c GET. Param is OID or symbolic name
        """
        try:
            param = mib[param]
        except KeyError:
            self.logger.error("Cannot resolve OID '%s'. Ignoring", param)
            return None
        for v in self.snmp_version:
            if v == SNMP_v1:
                r, message = self.snmp_v1_get(param)
            elif v == SNMP_v2c:
                r, message = self.snmp_v2c_get(param)
            else:
                self.snmp_check = self.snmp_check or False
                raise NOCError(msg="Unsupported SNMP version")
            if not r and not message:
                self.snmp_check = self.snmp_check or False
                return None
            if r:
                self.snmp_check = True
                return r

    def check_http_get(self, param):
        """
        Perform HTTP GET check. Param can be URL path or :<port>/<path>
        """
        url = f"http://{self.address}{param}"
        return self.http_get(url)

    def check_https_get(self, param):
        """
        Perform HTTPS GET check. Param can be URL path or :<port>/<path>
        """
        url = f"https://{self.address}{param}"
        return self.https_get(url)

    def is_match(self, result: str, method: str, value: str) -> bool:
        """
        Returns True when result matches value
        """
        if method == "eq":
            return result == value
        if method == "contains":
            return value in result
        if method == "re":
            return bool(self.get_re(value).search(result))
        self.logger.error("Invalid match method '%s'. Ignoring", method)
        return False

    def snmp_v1_get(self, param):
        """
        Perform SNMP v1 request. May be overridden for testing
        :param param:
        :return:
        """
        self.logger.info("SNMP v1 GET: %s", param)
        try:
            return open_sync_rpc(
                "activator", pool=self.pool, calling_service=self.calling_service
            ).snmp_v1_get(self.address, self.snmp_community, param, 5, True)
        except RPCError as e:
            self.logger.error("RPC Error: %s", e)
            return None

    def snmp_v2c_get(self, param):
        """
        Perform SNMP v2c request. May be overridden for testing
        :param param:
        :return:
        """
        self.logger.info("SNMP v2c GET: %s", param)
        try:
            return open_sync_rpc(
                "activator", pool=self.pool, calling_service=self.calling_service
            ).snmp_v2c_get(self.address, self.snmp_community, param, 5, True)
        except RPCError as e:
            self.logger.error("RPC Error: %s", e)
            return None

    def http_get(self, url):
        """
        Perform HTTP request. May be overridden for testing
        :param url: Request URL
        :return:
        """
        self.logger.info("HTTP Request: %s", url)
        try:
            return open_sync_rpc(
                "activator", pool=self.pool, calling_service=self.calling_service
            ).http_get(url, True)
        except RPCError as e:
            self.logger.error("RPC Error: %s", e)
            return None

    def https_get(self, url):
        """
        Perform HTTP request. May be overridden for testing
        :param url: Request URL
        :return:
        """
        return self.http_get(url)
