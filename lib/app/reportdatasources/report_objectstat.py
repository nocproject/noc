# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseReportDatasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import six
from collections import defaultdict
# Third-party modules
import cachetools
from django.db.models import Q as d_Q
from pymongo import ReadPreference
# NOC modules
from noc.lib.nosql import get_db
from noc.lib.nosql import Q as m_Q
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.profile import Profile
from noc.sa.models.objectstatus import ObjectStatus
from noc.sa.models.authprofile import AuthProfile
from noc.sa.models.objectcapabilities import ObjectCapabilities
from noc.inv.models.capability import Capability
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link


class IsolatorClass(object):
    """
    BaseClass for isolated set.
    Every Isolated Class split objects set by facets function.
    Function format is: `num_name`. index parameter - index subset in isolated set.
    """
    name = None

    @cachetools.func.ttl_cache(maxsize=20, ttl=600)
    def get_stat(self, num, value):
        # print("%s a %s, %s" % (self.name, num, value))
        if hasattr(self, "_%s_%s" % (num, self.name)):
            a = getattr(self, "_%s_%s" % (num, self.name))
            return a(value)
        else:
            return self.default(num, value)

    def default(self, num, index):
        """
        Last metthod
        :param num:
        :param index:
        :return:
        """
        raise NotImplementedError()


class AttributeIsolator(IsolatorClass):
    name = "attribute"

    OP_ATTR_MAP = {
        "2": {"1": False,
              "2": True},
        "7": {"1": str(Profile.get_by_name("Generic.Host").id),
              "2": str(Profile.get_by_name("Generic.Host").id),
              "ne": ["2"]},
        "13020": {"1": False,
                  "2": True,
                  "model": ManagedObjectProfile},
        "1403": {"5": "S",
                 "model": AuthProfile}
    }

    fields = [n.name for n in ManagedObject._meta._fields()]

    def default(self, num, index):
        return self.f_attribute(num, index)

    def f_attribute(self, num, value):
        """
        Islated object by atribute number
        :param num: Attribute number
        :param value: Attribute value
        :return:
        """
        # print "Attr a %s, %s" % (num, value)
        if "0" in num:
            # Cross link
            num1, num2 = num.split("0", 1)
            ff2 = [n.name for n in self.OP_ATTR_MAP[num]["model"]._meta._fields()][int(num2)]
            field = "%s__%s" % (self.fields[int(num1)], ff2)
        else:
            field = self.fields[int(num)]

        if value in self.OP_ATTR_MAP[num].get("ne", []):
            return ~d_Q(**{field: self.OP_ATTR_MAP[num][value]})
        else:
            return d_Q(**{field: self.OP_ATTR_MAP[num][value]})


class CapabilitiesIsolator(IsolatorClass):
    name = "has"
    default_set = set(ManagedObject.objects.filter().values_list("id", flat=True))

    @staticmethod
    def _2_has(index):
        c = ObjectCapabilities.objects.filter(m_Q(
            caps__match={
                "capability": Capability.objects.get(name="SNMP").id,
                "value": "true" == "true"
            }, read_preference=ReadPreference.SECONDARY_PREFERRED
        )).values_list("object").as_pymongo()
        return set(e["_id"] for e in c)

    def _3_has(self, index):
        # Has links, index - link count
        d = self.f_has_links(3, index)
        if index == "0":
            return self.default_set - set(d.iterkeys())
        elif index == "1":
            return set(d.iterkeys())
        elif index == "2":
            return set(dd for dd in six.iterkeys(d) if d[dd] == 1)
        elif index == "3":
            return set(dd for dd in six.iterkeys(d) if d[dd] == 2)
        elif index == "4":
            return set(dd for dd in six.iterkeys(d) if d[dd] >= 3)

    def _4_has(self, index):
        # Set has physical ifaces.
        # Index 0 - not physical ifaces
        pipeline = [{"$match": {"type": "physical"}},
                    {"$group": {"_id": "", "ifaces": {"$addToSet": "$managed_object"}}}]
        c = next(Interface.objects.aggregate(*pipeline))
        c = set(c["ifaces"])
        if index == "0":
            return self.default_set - c
        elif index == "1":
            return c

    def _5_has(self, index):
        # Set has Network Caps
        # Index 0 - not Netrwork Caps
        c = ObjectCapabilities.objects.filter(m_Q(
            caps__capability__in=[cp.id for cp in Capability.objects.filter(
                name__startswith="Network |",
                read_preference=ReadPreference.SECONDARY_PREFERRED)]
        )).values_list("object").as_pymongo()
        c = set(e["_id"] for e in c)
        if index == "0":
            return self.default_set - c
        elif index == "1":
            return c

    def f_has(self, num, value):
        """
        Caps
        :param num:
        :param value:
        :return:
        """
        # print("Has a %s, %s" % (num, value))
        if hasattr(self, "_%d_has" % num):
            a = getattr(self, "_%d_has" % num)
            return a(value)
        raise NotImplementedError()

    @staticmethod
    def f_has_links(num, value):
        # Has links.
        pipeline = [
            {"$unwind": "$interfaces"},
            {"$lookup": {"from": "noc.interfaces",
                         "localField": "interfaces",
                         "foreignField": "_id", "as": "int"}},
            {"$group": {"_id": "",
                        "count": {"$push": "$int.managed_object"}}}
        ]
        c = next(Link.objects.aggregate(*pipeline))
        # c = next(links)
        d = defaultdict(int)
        for ll in c["count"]:
            if not ll:
                continue
            d[ll[0]] += 1
        # c = set(i[0] for i in c["count"] if i)
        return d


class StatusIsolator(IsolatorClass):
    name = "is"

    def _1_is(self, index):
        # Status - Is Managed
        return d_Q(**{"is_managed": index == "2"})

    def _2_is(self, index):
        # Status - Monitoring
        if index == "1":
            # Is Monitoring = Is managed and not Generic Profile
            return d_Q(**{"is_managed": True}) & d_Q(object_profile__enable_ping=True)
        elif index == "2":
            # Is Not Monitoring = Is not managed + Is managed and not ping
            return set(ManagedObject.objects.filter(d_Q(**{"is_managed": False})).values_list(
                "id", flat=True)).union(set(ManagedObject.objects.filter(
                    d_Q(**{"is_managed": True}) &
                    d_Q(object_profile__enable_ping=False)).values_list("id", flat=True)))

    def _3_is(self, index):
        # Status - Is Availability
        return set(ObjectStatus.objects.filter(
            status=bool(int(index) - 1),
            read_preference=ReadPreference.SECONDARY_PREFERRED).values_list("object"))

    def _4_is(self, index):
        # Is Problem perhaps
        # Suggests SNMP Problems
        return self.is_p("1", "0", inverse=index == "0")

    def _5_is(self, index):
        if index == "1":
            # Is topology, not mac
            return set(ManagedObject.objects.filter(
                d_Q(**{"is_managed": True}) &
                d_Q(object_profile__enable_box_discovery_lldp=False) &
                d_Q(object_profile__enable_box_discovery_lacp=False) &
                d_Q(object_profile__enable_box_discovery_cdp=False) &
                d_Q(object_profile__enable_box_discovery_stp=False)
            ).values_list("id", flat=True))

        elif index == "2":
            # Is topology, not mac
            return set(ManagedObject.objects.filter(
                d_Q(**{"is_managed": True}) &
                d_Q(object_profile__enable_box_discovery=True) & (
                    d_Q(object_profile__enable_box_discovery_lldp=True) |
                    d_Q(object_profile__enable_box_discovery_lacp=True) |
                    d_Q(object_profile__enable_box_discovery_cdp=True) |
                    d_Q(object_profile__enable_box_discovery_stp=True))).values_list("id", flat=True))
            # return self.f_attribute("13020", value)

    def f_is(self, num, value):
        """

        :param num:
        :param value:
        :return:
        """
        # print "Is a %s, %s" % (num, value)
        if hasattr(self, "_%d_is" % num):
            a = getattr(self, "_%d_is" % num)
            return a(value)
        raise NotImplementedError()

    # @todo split to CLI porblem, SNMP (Access Problem) ... etc
    def is_p(self, num, value, inverse=False):
        """
        Problem match
        :param discovery: Discovery name
        :param problem: Problem text
        :return:
        """
        match = {"problems": {"$exists": True}}
        if num == "1":
            # SNMP Problem
            match = {"problems": {"$exists": True}, "problems.suggest_snmp.": {
                "$regex": "Failed to guess SNMP community", "$options": "i"}}
        if num == "2":
            # CLI Problem
            match = {"$and": [{"problems.profile.": {"$ne": "Cannot fetch snmp data, check device for SNMP access"}},
                              {"problems.profile.": {"$ne": "Cannot detect profile"}},
                              {"problems.version.": {"$regex": "/Remote error code \d+/"}}]}

        c = set(int(r["_id"].rsplit("-")[-1]) for r in get_db()["noc.joblog"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).find(match))
        if inverse:
            return set(ManagedObject.objects.filter().values_list("id", flat=True)) - c
        else:
            return c


class ProblemIsolator(IsolatorClass):
    name = "isp"
    common_filter = set(ManagedObject.objects.filter().values_list("id", flat=True))

    def _0_isp(self, index):
        # Common Problem
        match = {"problems": {"$exists": True}}
        c = set(int(r["_id"].rsplit("-")[-1]) for r in get_db()["noc.joblog"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).find(match))
        if index == "0":
            return self.common_filter - c
        else:
            return c

    def _1_isp(self, index):
        # SNMP Problem
        match = {"$or": [
            {"problems.suggest_snmp.": {"$regex": "Failed to guess SNMP community", "$options": "i"}},
            {"problems.profile.": "Cannot fetch snmp data, check device for SNMP access"}]
        }
        c = set(int(r["_id"].rsplit("-")[-1]) for r in get_db()["noc.joblog"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).find(match))
        if index == "0":
            return self.common_filter - c
        else:
            return c

    def _2_isp(self, index):
        # CLI Problem
        match = {"$and": [{"problems.profile.": {"$ne": "Cannot fetch snmp data, check device for SNMP access"}},
                          {"problems.profile.": {"$ne": "Cannot detect profile"}},
                          {"$or": [{"problems.version.": {"$regex": "Remote error code \d+"}},
                                   {"problems.suggest_cli.": {"$regex": "Failed to guess CLI credentials",
                                                              "$options": "i"}}]}
                          ]}
        c = set(int(r["_id"].rsplit("-")[-1]) for r in get_db()["noc.joblog"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).find(match))
        if index == "0":
            return self.common_filter - c
        return c

    def _3_isp(self, index):
        # Profiles detect problems
        match = {"$or": [{"problems.suggest_snmp.": {"$regex": "Failed to guess SNMP community", "$options": "i"}},
                         {"problems.profile.": "Cannot fetch snmp data, check device for SNMP access"},
                         {"problems.profile.": "Cannot detect profile"}]}
        c = set(int(r["_id"].rsplit("-")[-1]) for r in get_db()["noc.joblog"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).find(match))
        if index == "0":
            return self.common_filter - c
        return c

    def _4_isp(self, index):
        # Undefined profiles
        match = {"problems.profile.": {"$regex": "Not find profile for OID"}}
        c = set(int(r["_id"].rsplit("-")[-1]) for r in get_db()["noc.joblog"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).find(match))
        if index == "0":
            return self.common_filter - c
        return c
