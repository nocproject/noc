# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Profile check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import threading
import cachetools
import operator
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.profilecheckrule import ProfileCheckRule
from noc.core.mib import mib
from noc.core.service.client import open_sync_rpc, RPCError

rules_lock = threading.Lock()


class ProfileCheck(DiscoveryCheck):
    """
    Profile discovery
    """
    name = "profile"

    _rules_cache = cachetools.TTLCache(10, ttl=60)

    def handler(self):
        self.logger.info("Checking profile accordance")
        profile = self.get_profile()
        if not profile:
            return  # Cannot detect
        if profile == self.object.profile_name:
            self.logger.info("Profile is correct: %s", profile)
        else:
            self.logger.info(
                "Profile change detected: %s -> %s. Fixing database",
                self.object.profile_name, profile
            )
            self.object.profile_name = profile
            self.object.save()

    def get_profile(self):
        """
        Returns profile for object, or None when not known
        """
        self.result_cache = {}  # (method, param) -> result
        snmp_result = None
        http_result = None
        for ruleset in self.get_rules():
            for (method, param), actions in ruleset:
                result = self.do_check(method, param)
                if not result:
                    continue
                if "snmp" in method:
                    snmp_result = result
                if "http" in method:
                    http_result = result
                for match_method, value, action, profile, rname in actions:
                    if self.is_match(result, match_method, value):
                        self.logger.info("Matched profile: %s (%s)",
                                         profile, rname)
                        # @todo: process MAYBE rule
                        return profile
        self.logger.info("Cannot find profile in \"Profile Check Rules\"")
        if snmp_result:
            self.logger.info("SNMP Result: %s", snmp_result)
        if http_result:
            self.logger.info("HTTP Result: %s", http_result)
        self.set_problem(
            alarm_class="Discovery | Guess | Profile",
            message="Cannot detect profile",
            fatal=True
        )
        self.logger.debug("Result %s" % self.job.problems)
        return None

    @cachetools.cachedmethod(operator.attrgetter("_rules_cache"), lock=lambda _: rules_lock)
    def get_rules(self):
        """
        Load ProfileCheckRules and return a list, groupped by preferences
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
        self.logger.info("Compiling \"Profile Check rules\"")
        d = {}  # preference -> (method, param) -> [rule, ..]
        for r in ProfileCheckRule.objects.all().order_by("preference"):
            if "snmp" in r.method and r.param.startswith("."):
                self.logger.error("Bad SNMP in ruleset \"%s\", Skipping..." % r.name)
                continue
            if r.preference not in d:
                d[r.preference] = {}
            k = (r.method, r.param)
            if k not in d[r.preference]:
                d[r.preference][k] = []
            d[r.preference][k] += [(
                r.match_method,
                r.value,
                r.action,
                r.profile,
                r.name
            )]
        return [d[p].items() for p in sorted(d)]

    def do_check(self, method, param):
        """
        Perform check
        """
        self.logger.debug("do_check(%s, %s)", method, param)
        if (method, param) in self.result_cache:
            self.logger.debug("Using cached value")
            return self.result_cache[method, param]
        h = getattr(self, "check_%s" % method, None)
        if not h:
            self.logger.error("Invalid check method '%s'. Ignoring",
                              method)
            return None
        result = h(param)
        self.result_cache[method, param] = result
        return result

    def check_snmp_v2c_get(self, param):
        """
        Perform SNMP v2c GET. Param is OID or symbolic name
        """
        if hasattr(self.object, "_suggest_snmp") and self.object._suggest_snmp:
            # Use guessed community
            # as defined one may be invalid
            snmp_ro = self.object._suggest_snmp[0]
        else:
            snmp_ro = self.object.credentials.snmp_ro
        if not snmp_ro:
            self.logger.error("No SNMP credentials. Ignoring")
            return None
        try:
            param = mib[param]
        except KeyError:
            self.logger.error("Cannot resolve OID '%s'. Ignoring",
                              param)
            return None
        try:
            return open_sync_rpc(
                "activator",
                pool=self.object.pool.name,
                calling_service="discovery"
            ).snmp_v2c_get(
                self.object.address,
                snmp_ro,
                param
            )
        except RPCError as e:
            self.logger.error("RPC Error: %s", e)
            return None

    def check_http_get(self, param):
        """
        Perform HTTP GET check. Param can be URL path or :<port>/<path>
        """
        url = "http://%s%s" % (self.object.address, param)
        try:
            return open_sync_rpc(
                "activator",
                pool=self.object.pool.name,
                calling_service="discovery"
            ).http_get(url)
        except RPCError as e:
            self.logger.error("RPC Error: %s", e)
            return None

    def check_https_get(self, param):
        """
        Perform HTTPS GET check. Param can be URL path or :<port>/<path>
        """
        url = "https://%s%s" % (self.object.address, param)
        try:
            return open_sync_rpc(
                "activator",
                pool=self.object.pool.name,
                calling_service="discovery"
            ).http_get(url)
        except RPCError as e:
            self.logger.error("RPC Error: %s", e)
            return None

    def is_match(self, result, method, value):
        """
        Returns True when result matches value
        """
        if method == "eq":
            return result == value
        elif method == "contains":
            return value in result
        elif method == "re":
            return bool(re.search(value, result))
        else:
            self.logger.error("Invalid match method '%s'. Ignoring",
                              method)
            return False
