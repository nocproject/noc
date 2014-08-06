## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface Classification Rules models
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.lib.nosql import (Document, EmbeddedDocument, StringField,
    ListField, EmbeddedDocumentField, BooleanField, ForeignKeyField,
    IntField, PlainReferenceField)
from noc.lib.ip import IP
from noc.main.models import PrefixTable
from interfaceprofile import InterfaceProfile
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.vc.models.vcfilter import VCFilter


class InterfaceClassificationMatch(EmbeddedDocument):
    # Field name
    field = StringField(choices=[
        ("name", "name"),
        ("description", "description"),
        ("ip", "ip"),
        ("tagged", "tagged vlan"),
        ("untagged", "untagged vlan")
    ])
    # Operation
    op = StringField(choices=[
        ("eq", "Equals"),
        ("regexp", "RegExp"),
        ("in", "in")
    ])
    #
    value = StringField()
    # "ip in"
    prefix_table = ForeignKeyField(PrefixTable, required=False)
    # *vlan in
    vc_filter = ForeignKeyField(VCFilter, required=False)
    description = StringField(required=False)

    def __unicode__(self):
        if self.prefix_table:
            v = self.prefix_table.name
        elif self.vc_filter:
            v = self.vc_filter.name
        else:
            v = self.value
        return "%s %s %s" % (self.field, self.op, v)

    def compile(self, f_name):
        a = getattr(self, "compile_%s_%s" % (self.field, self.op), None)
        if a:
            return a(f_name)
        else:
            raise SyntaxError("%s %s is not implemented" % (
                self.field, self.op))

    # name
    def compile_name_eq(self, f_name):
        return "\n".join([
            "def %s(iface):" % f_name,
            "    return iface.name.lower() == %s" % repr(self.value.lower())
        ])

    def compile_name_regexp(self, f_name):
        return "\n".join([
            "rx_%s = re.compile(%s, re.IGNORECASE)" % (f_name, repr(self.value)),
            "def %s(iface):" % f_name,
            "    return bool(rx_%s.search(iface.name))" % f_name
        ])

    # description
    def compile_description_eq(self, f_name):
        return "\n".join([
            "def %s(iface):" % f_name,
            "    return iface.description.lower() == %s" % repr(self.value.lower())
        ])

    def compile_description_regexp(self, f_name):
        return "\n".join([
            "rx_%s = re.compile(%s, re.IGNORECASE)" % (f_name, repr(self.value1)),
            "def %s(iface):" % f_name,
            "    return iface.description and bool(rx_%s.search(iface.description))" % f_name
        ])
    # IP
    def compile_ip_eq(self, f_name):
        v = IP.prefix(self.value)
        r = [
            "def %s(iface):" % f_name,
            "    a = [si.ipv%(afi)s_addresses for si in iface.subinterface_set.filter(enabled_afi='IPv%(afi)s')]" % {"afi": v.afi},
            "    a = sum(a, [])",
        ]
        if "/" in self.value:
            # Compare prefixes
            r += [
                "    return any(x for x in a if x == %r)" % v.prefix
            ]
        else:
            # Compare addresses
            v = v.prefix.split("/")[0]
            r += [
                "    return any(x for x in a if x.split('/')[0] == %r)" % v
            ]
        return "\n".join(r)

    def compile_ip_in(self, f_name):
        r = [
            "pt_%s = PrefixTable.objects.get(id=%s)" % (f_name, self.prefix_table.id),
            "def %s(iface):" % f_name,
            "    for si in iface.subinterface_set.filter(enabled_afi='IPv4'):",
            "        for a in si.ipv4_addresses:",
            "            if a in pt_%s:" % f_name,
            "                return True",
            "    for si in iface.subinterface_set.filter(enabled_afi='IPv6'):",
            "        for a in si.ipv6_addresses:",
            "            if a in pt_%s:" % f_name,
            "                return True",
            "    return False"
        ]
        return "\n".join(r)

    ## Untagged
    def compile_untagged_eq(self, f_name):
        vlan = int(self.value)
        if vlan < 1 or vlan > 4096:
            raise SyntaxError("Invalid VLAN")
        r = [
            "def %s(iface):" % f_name,
            "    return bool(iface.subinterface_set.filter(enabled_afi='BRIDGE', untagged_vlan=%d).count())" % vlan
        ]
        return "\n".join(r)

    def compile_untagged_in(self, f_name):
        r = [
            "vcf_%s = VCFilter.objects.get(id=%s)" % (f_name, self.vc_filter.id),
            "def %s(iface):" % f_name,
            "    for si in iface.subinterface_set.filter(enabled_afi='BRIDGE'):",
            "        if si.untagged_vlan and vcf_%s.check(si.untagged_vlan):" % f_name,
            "            return True",
            "    return False"
        ]
        return "\n".join(r)

    ## Tagged
    def compile_tagged_eq(self, f_name):
        vlan = int(self.value)
        if vlan < 1 or vlan > 4096:
            raise SyntaxError("Invalid VLAN")
        r = [
            "def %s(iface):" % f_name,
            "    return bool(iface.subinterface_set.filter(enabled_afi='BRIDGE', tagged_vlans=%d).count())" % vlan
        ]
        return "\n".join(r)

    def compile_tagged_in(self, f_name):
        r = [
            "vcf_%s = VCFilter.objects.get(id=%s)" % (f_name, self.vc_filter.id),
            "def %s(iface):" % f_name,
            "    for si in iface.subinterface_set.filter(enabled_afi='BRIDGE'):",
            "        if si.tagged_vlans:",
            "            if any(vlan for vlan in si.tagged_vlans if vcf_%s.check(vlan)):" % f_name,
            "                return True",
            "    return False"
        ]
        return "\n".join(r)


class InterfaceClassificationRule(Document):
    meta = {
        "collection": "noc.inv.interfaceclassificationrules",
        "allow_inheritance": False
    }
    name = StringField(required=False)
    is_active = BooleanField(default=True)
    description = StringField(required=False)
    order = IntField()
    selector = ForeignKeyField(ManagedObjectSelector, required=False)
    match = ListField(
        EmbeddedDocumentField(InterfaceClassificationMatch),
        required=False)
    profile = PlainReferenceField(InterfaceProfile,
        default=InterfaceProfile.get_default_profile)

    def __unicode__(self):
        r = [unicode(x) for x in self.match]
        return "%s -> %s" % (", ".join(r), self.profile.name)

    @property
    def match_expr(self):
        """
        Stringified match expression
        """
        if not len(self.match):
            return u"any"
        elif len(self.match) == 1:
            return unicode(self.match[0])
        else:
            return u" AND ".join(u"(%s)" % unicode(m) for m in self.match)

    @classmethod
    def get_classificator_code(cls):
        r = ["import re"]
        mf = [
            "gsc = {}",
            "def classify(interface):",
            "    def in_selector(o, s):",
            "        if s in s_cache:",
            "            return s_cache[s]",
            "        if s in gsc:",
            "            selector = gsc[s]",
            "        else:",
            "            selector = ManagedObjectSelector.objects.get(id=s)",
            "            gsc[s] = selector",
            "        r = o in selector",
            "        s_cache[s] = r",
            "        return r",
            "    s_cache = {}",
            "    mo = interface.managed_object"
        ]
        for rule in cls.objects.filter(is_active=True).order_by("order"):
            rid = str(rule.id)
            lmn = []
            for i, m in enumerate(rule.match):
                mn = "match_%s_%d" % (rid, i)
                r += [m.compile(mn)]
                lmn += ["%s(interface)" % mn]
            if lmn:
                mf += [
                    "    if in_selector(mo, %d) and %s:" % (rule.selector.id, " and ".join(lmn)),
                    "        return %r" % rule.profile.name
                ]
            else:
                mf += ["    return %r" % rule.profile.name]
        r += mf
        return "\n".join(r)

    @classmethod
    def get_classificator(cls):
        code = cls.get_classificator_code() + "\nhandlers[0] = classify\n"
        # Hack to retrieve reference
        handlers = {}
        # Compile code
        exec code in {
            "re": re,
            "PrefixTable": PrefixTable,
            "VCFilter": VCFilter,
            "ManagedObjectSelector": ManagedObjectSelector,
            "handlers": handlers
        }
        return handlers[0]
