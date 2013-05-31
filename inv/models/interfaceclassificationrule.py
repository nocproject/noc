## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface Classification Rules models
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.lib.nosql import Document, EmbeddedDocument, StringField,\
    ListField, EmbeddedDocumentField, BooleanField, ForeignKeyField,\
    IntField, PlainReferenceField
from noc.lib.ip import IP
from noc.main.models import PrefixTable
from interfaceprofile import InterfaceProfile


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
        ("regexp", "RegExp"),
        ("eq", "Equals"),
        ("contains", "Contains"),
        ("in", "in"),
        ("between", "Between")
    ])
    #
    value1 = StringField()
    # "between"
    value2 = StringField(required=False)
    # "ip in"
    prefix_table = ForeignKeyField(PrefixTable, required=False)

    def __unicode__(self):
        if self.op == "between":
            return "%s between %s and %s" % (
                self.field, self.value1, self.value2)
        else:
            return "%s %s %s" % (self.field, self.op, self.value1)

    def check_single_value(self):
        if not self.value1:
            raise SyntaxError("value1 is not set")
        if self.value2:
            raise SyntaxError("value2 is set")

    def compile(self, f_name):
        a =  getattr(self, "compile_%s_%s" % (self.field, self.op), None)
        if a:
            return a(f_name)
        else:
            raise SyntaxError("%s %s is not implemented" % (
                self.field, self.op))

    # name
    def compile_name_eq(self, f_name):
        self.check_single_value()
        return "\n".join([
            "def %s(iface):" % f_name,
            "    return iface.name == %s" % repr(self.value1)
        ])

    def compile_name_contains(self, f_name):
        self.check_single_value()
        return "\n".join([
            "def %s(iface):" % f_name,
            "    return %s in iface.name.lower()" % repr(self.value1.lower())
        ])

    def compile_name_regex(self, f_name):
        self.check_single_value()
        return "\n".join([
            "rx_%s = re.compile(%s)" % (f_name, repr(self.value1)),
            "def %s(iface):" % f_name,
            "    return bool(rx_%s.search(iface.name))" % f_name
        ])

    # description
    def compile_description_eq(self, f_name):
        self.check_single_value()
        return "\n".join([
            "def %s(iface):" % f_name,
            "    return iface.description == %s" % repr(self.value1)
        ])

    def compile_description_contains(self, f_name):
        self.check_single_value()
        return "\n".join([
            "def %s(iface):" % f_name,
            "    return iface.description and %s in iface.description.lower()" % repr(self.value1.lower())
        ])

    def compile_description_regex(self, f_name):
        self.check_single_value()
        return "\n".join([
            "rx_%s = re.compile(%s)" % (f_name, repr(self.value1)),
            "def %s(iface):" % f_name,
            "    return iface.description and bool(rx_%s.search(iface.description))" % f_name
        ])
    # IP
    def compile_ip_eq(self, f_name):
        self.check_single_value()
        v = IP.prefix(self.value1)
        r = [
            "def %s(iface):" % f_name,
            "    a = [si.ipv%(afi)s_addresses for si in iface.subinterface_set.filter(enabled_afi='IPv%(afi)s')]" % {"afi": v.afi},
            "    a = sum(a, [])",
        ]
        if "/" in self.value1:
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
        self.check_single_value()
        if "/" not in self.value1:
            raise SyntaxError("'%s' must be prefix" % self.value1)
        v = IP.prefix(self.value1)
        r = [
            "def %s(iface):" % f_name,
            "    a = [si.ipv%(afi)s_addresses for si in iface.subinterface_set.filter(enabled_afi='IPv%(afi)s')]" % {"afi": v.afi},
            "    a = sum(a, [])",
            "    v = IP.prefix(%r)" % v.prefix,
            "    return any(x for x in a if IP.prefix(x) in v)"
        ]
        return "\n".join(r)

    ## Untagged
    def compile_untagged_eq(self, f_name):
        self.check_single_value()
        vlan = int(self.value1)
        if vlan < 1 or vlan > 4096:
            raise SyntaxError("Invalid VLAN")
        r = [
            "def %s(iface):" % f_name,
            "    for si in iface.subinterface_set.filter(enabled_afi='BRIDGE'):",
            "        if si.untagged_vlan = %d:" % vlan,
            "            return True",
            "    return False"
        ]
        return "\n".join(r)

    def compile_untagged_between(self, f_name):
        pass

    def compile_untagged_in(self, f_name):
        pass


class InterfaceClassificationRule(Document):
    meta = {
        "collection": "noc.inv.interfaceclassificationrules",
        "allow_inheritance": False
    }
    name = StringField(required=False)
    is_active = BooleanField(default=True)
    description = StringField(required=False)
    order = IntField()
    match = ListField(
        EmbeddedDocumentField(InterfaceClassificationMatch),
        required=False)
    profile = PlainReferenceField(InterfaceProfile,
        default=InterfaceProfile.get_default_profile)

    def __unicode__(self):
        r = [unicode(x) for x in self.match]
        return "%s -> %s" % (", ".join(r), self.profile_name)

    @classmethod
    def get_classificator_code(cls):
        r = ["import re"]
        mf = ["def classify(cls, interface):"]
        for rule in cls.objects.filter(is_active=True).order_by("order"):
            rid = str(rule.id)
            lmn = []
            for i, m in enumerate(rule.match):
                mn = "match_%s_%d" % (rid, i)
                r += [m.compile(mn)]
                lmn += ["%s(interface)" % mn]
            if lmn:
                mf += [
                    "    if %s:" % " and ".join(lmn),
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
        exec code in {"re": re, "IP": IP, "handlers": handlers}
        return handlers[0]
