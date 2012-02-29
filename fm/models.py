# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FM module database models
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
import imp
import subprocess
import os
import datetime
import re
import hashlib
## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.template import Template, Context
## NOC modules
from noc.sa.models import ManagedObject, ManagedObjectSelector
from noc.main.models import TimePattern, NotificationGroup, PyRule, Style, User
from noc.main.models import Template as NOCTemplate
from noc.settings import config
from noc.lib.fileutils import safe_rewrite
import noc.lib.nosql as nosql
from noc.lib.fileutils import temporary_file
from noc.lib.escape import json_escape as jq
from noc.lib.dateutils import total_seconds


##
## Exceptions
##
class MIBRequiredException(Exception):
    def __init__(self, mib, requires_mib):
        super(MIBRequiredException, self).__init__()
        self.mib = mib
        self.requires_mib = requires_mib

    def __str__(self):
        return "%s requires %s" % (self.mib, self.requires_mib)


class MIBNotFoundException(Exception):
    def __init__(self, mib):
        super(MIBNotFoundException, self).__init__()
        self.mib = mib

    def __str__(self):
        return "MIB not found: %s" % self.mib


class InvalidTypedef(Exception):
    pass


class OIDCollision(Exception):
    def __init__(self, oid, name1, name2, msg=None):
        self.oid = oid
        self.name1 = name1
        self.name2 = name2
        self.msg = msg

    def __str__(self):
        s = "Cannot resolve OID %s collision between %s and %s" % (
            self.oid, self.name1, self.name2)
        if self.msg:
            s += ". %s" % self.msg
        return s


##
## Regular expressions
##
rx_module_not_found = re.compile(r"{module-not-found}.*`([^']+)'")
rx_py_id = re.compile("[^0-9a-zA-Z]+")
rx_mibentry = re.compile(r"^((\d+\.){5,}\d+)|(\S+::\S+)$")
rx_mib_name = re.compile(r"^(\S+::\S+?)(.\d+)?$")
rx_tailing_numbers = re.compile(r"^(\S+?)((?:\.\d+)*)$")
rx_rule_name_quote = re.compile("[^a-zA-Z0-9]+")


def rulename_quote(s):
    """
    Convert arbitrary string to pyrule name
    
    >>> rulename_quote("Unknown | Default")
    'Unknown_Default'
    """
    return rx_rule_name_quote.sub("_", s)


##
## MIB Processing
##
class OIDAlias(nosql.Document):
    meta = {
        "collection": "noc.oidaliases",
        "allow_inheritance": False
    }
    
    rewrite_oid = nosql.StringField(unique=True)
    to_oid = nosql.StringField()
    is_builtin = nosql.BooleanField(default=False)
    description = nosql.StringField(required=False)
    
    ## Lookup cache
    cache = None
    
    def __unicode__(self):
        return u"%s -> %s" % (self.rewrite_oid, self.to_oid)

    @classmethod
    def rewrite(cls, oid):
        """
        Rewrite OID with alias if any
        """
        if cls.cache is None:
            # Initialize cache
            cls.cache = dict([(a.rewrite_oid, a.to_oid.split("."))
                for a in cls.objects.all()])
        # Lookup
        l_oid = oid.split(".")
        rest = []
        while l_oid:
            c_oid = ".".join(l_oid)
            try:
                a_oid = cls.cache[c_oid]
                # Found
                return ".".join(a_oid + rest)
            except KeyError:
                rest = [l_oid.pop()] + rest
        # Not found
        return oid


class SyntaxAlias(nosql.Document):
    meta = {
        "collection": "noc.syntaxaliases",
        "allow_inheritance": False
    }
    name = nosql.StringField(unique=True, required=True)
    syntax = nosql.DictField(required=False)
    is_builtin = nosql.BooleanField(default=False)
    # Lookup cache
    cache = None

    def __unicode__(self):
        return self.name

    @classmethod
    def rewrite(cls, name, syntax):
        if cls.cache is None:
            cls.cache = dict([(o.name, o.syntax) for o in cls.objects.all()])
        return cls.cache.get(name, syntax)


class MIBPreference(nosql.Document):
    meta = {
        "collection": "noc.mibpreferences",
        "allow_inheritance": False
    }
    mib = nosql.StringField(required=True, unique=True)
    preference = nosql.IntField(required=True,
                                unique=True)  # The less is the better
    is_builtin = nosql.BooleanField(required=True, default=False)

    def __unicode__(self):
        return u"%s(%d)" % (self.mib, self.preference)


class MIB(nosql.Document):
    meta = {
        "collection": "noc.mibs",
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True, unique=True)
    description = nosql.StringField(required=False)
    last_updated = nosql.DateTimeField(required=True)
    depends_on = nosql.ListField(nosql.StringField())
    # TC definitions: name -> SYNTAX
    typedefs = nosql.DictField(required=False)
    # Compiled MIB version
    version = nosql.IntField(required=False, default=0)

    def __unicode__(self):
        return self.name

    @classmethod
    def parse_syntax(cls, syntax):
        """
        Process part of smidump output and convert to syntax structure
        """
        if "base_type" in syntax:
            # Already compiled
            return syntax
        s = {}
        if "basetype" in syntax:
            s["base_type"] = syntax["basetype"]
        elif "base_type" in syntax:
            s["base_type"] = syntax["base_type"]
        if "name" in syntax and "module" in syntax:
            if syntax["module"] == "":
                # Empty module -> builitin types
                s["base_type"] = syntax["name"]
            else:
                # Resolve references
                mib = MIB.objects.filter(name=syntax["module"]).first()
                if mib is None:
                    raise MIBNotFoundException(syntax["module"])
                if not mib.typedefs or syntax["name"] not in mib.typedefs:
                    return {}
                td = mib.typedefs[syntax["name"]]
                for k in ["base_type", "display_hint", "enum_map"]:
                    if k in td:
                        s[k] = td[k]
        if s["base_type"] in ("Enumeration", "Bits"):
            enum_map = s.get("enum_map", {})
            for k in syntax:
                sk = syntax[k]
                if type(sk) != dict:
                    continue
                if "nodetype" in sk and sk["nodetype"] == "namednumber":
                    enum_map[sk["number"]] = k
            s["enum_map"] = enum_map
        if "format" in syntax:
            s["display_hint"] = syntax["format"]
        return s

    @classmethod
    def load(cls, path, force=False):
        """
        Load MIB from file
        :param path: MIB path
        :param force: Load anyways
        :return: MIB object
        """
        if not os.path.exists(path):
            raise ValueError("File not found: %s" % path)
        # Build SMIPATH variable for smidump to exclude locally installed MIBs
        smipath = ["share/mibs", "local/share/mibs"]
        # Pass MIB through smilint to detect missed modules
        f = subprocess.Popen([config.get("path", "smilint"), "-m", path],
            stderr=subprocess.PIPE,
            env={"SMIPATH": ":".join(smipath)}).stderr
        for l in f:
            match = rx_module_not_found.search(l.strip())
            if match:
                raise MIBRequiredException("Uploaded MIB", match.group(1))
        # Convert MIB to python module and load
        with temporary_file() as p:
            subprocess.check_call([config.get("path", "smidump"), "-k", "-q",
                                   "-f", "python", "-o", p, path],
                env={"SMIPATH": ":".join(smipath)})
            # Add coding string
            with open(p) as f:
                data = unicode(f.read(), "ascii", "ignore").encode("ascii")
            with open(p, "w") as f:
                f.write(data)
            m = imp.load_source("mib", p)
        mib_name = m.MIB["moduleName"]
        # Check module dependencies
        depends_on = {}  # MIB Name -> Object ID
        if "imports" in m.MIB:
            for i in m.MIB["imports"]:
                if "module" not in i:
                    continue
                rm = i["module"]
                if rm in depends_on:
                    continue
                md = MIB.objects.filter(name=rm).first()
                if md is None:
                    raise MIBRequiredException(mib_name, rm)
                depends_on[rm] = md
        # Get MIB latest revision date
        try:
            last_updated = datetime.datetime.strptime(
                sorted([x["date"] for x in m.MIB[mib_name]["revisions"]])[-1],
                "%Y-%m-%d %H:%M")
        except:
            last_updated = datetime.datetime(year=1970, month=1, day=1)
        # Extract MIB typedefs
        typedefs = {}
        if "typedefs" in m.MIB:
            for t in m.MIB["typedefs"]:
                typedefs[t] = cls.parse_syntax(m.MIB["typedefs"][t])
        # Check mib already uploaded
        mib_description = m.MIB[mib_name].get("description", None)
        mib = MIB.objects.filter(name=mib_name).first()
        if force and mib:
            # Delete mib to forceful update
            MIBData.objects.filter(mib=mib.id).delete()
            mib.clean()
            mib.delete()
            mib = None
        if mib is not None:
            # Skip same version
            if mib.last_updated >= last_updated:
                return mib
            mib.description = mib_description
            mib.last_updated = last_updated
            mib.depends_on = sorted(depends_on)
            mib.typedefs = typedefs
            mib.save()
            # Delete all MIB Data
            mib.clean()
        else:
            # Create MIB
            mib = MIB(name=mib_name, description=mib_description,
                      last_updated=last_updated,
                      depends_on=sorted(depends_on),
                      typedefs=typedefs)
            mib.save()
        # Upload MIB data
        data = []
        for i in ["nodes", "notifications"]:
            if i in m.MIB:
                data += [
                    {
                    "name": "%s::%s" % (mib_name, node),
                    "oid": v["oid"],
                    "description": v.get("description"),
                    "syntax": v["syntax"]["type"] if "syntax" in v else None
                } for node, v in m.MIB[i].items()]
        mib.load_data(data)
        # Save MIB to cache if not uploaded from cache
        lcd = os.path.join("local", "share", "mibs")
        if not os.path.isdir(lcd):  # Ensure directory exists
            os.makedirs(os.path.join("local", "share", "mibs"))
        local_cache_path = os.path.join(lcd, "%s.mib" % mib_name)
        cache_path = os.path.join("share", "mibs", "%s.mib" % mib_name)
        if ((os.path.exists(local_cache_path) and
             os.path.samefile(path, local_cache_path)) or
            (os.path.exists(cache_path) and
             os.path.samefile(path, cache_path))):
            return mib
        with open(path) as f:
            data = f.read()
        safe_rewrite(local_cache_path, data)
        return mib

    def load_data(self, data):
        """
        Load mib data from list of {oid:, name:, description:, syntax:}
        :param data:
        :return:
        """
        # Get MIB preference
        mp = MIBPreference.objects.filter(mib=self.name).first()
        mib_preference = mp.preference if mp else None
        prefs = {}  # MIB Preferences cache
        # Load data
        for v in data:
            oid = v["oid"]
            oid_name = v["name"]
            description = v.get("description", None)
            o = MIBData.objects.filter(oid=oid).first()
            if o is not None:
                if o.name == oid_name:
                    # Same oid, same name: duplicated declaration.
                    # Silently skip
                    continue
                # Try to resolve collision
                if not mib_preference:
                    # No preference for target MIB
                    raise OIDCollision(oid, oid_name, o.name,
                                    "No preference for %s" % self.name)
                o_mib = o.name.split("::")[0]
                if o_mib not in prefs:
                    mp = MIBPreference.objects.filter(
                        mib=o_mib).first()
                    if not mp:
                        # No preference for destination MIB
                        raise OIDCollision(oid, oid_name, o.name,
                                        "No preference for %s" % o_mib)
                    prefs[o_mib] = mp.preference  # Add to cache
                o_preference = prefs[o_mib]
                if mib_preference == o_preference:
                    # Equal preferences, collision
                    raise OIDCollision(oid, oid_name, o.name,
                                       "Equal preferences")
                if mib_preference < o_preference:
                    # Replace existing
                    o.aliases = sorted(o.aliases + [o.name])
                    o.name = oid_name
                    o.mib = self.id
                    if description:
                        o.description = description
                    syntax = v.get("syntax")
                    if syntax:
                        o.syntax = MIB.parse_syntax(syntax)
                    o.save()
                else:
                    # Append to aliases
                    if oid_name not in o.aliases:
                        o.aliases = sorted(o.aliases + [oid_name])
                        o.save()
            else:
                # No OID collision found, save
                syntax = v.get("syntax")
                if syntax:
                    syntax = MIB.parse_syntax(syntax)
                MIBData(mib=self.id,
                        oid=oid,
                        name=oid_name,
                        description=description,
                        syntax=syntax).save()

    @classmethod
    def get_oid(cls, name):
        """
        Get OID by name
        """
        tail = ""
        match = rx_tailing_numbers.match(name)
        if match:
            name, tail = match.groups()
        # Search by primary name
        d = MIBData.objects.filter(name=name).first()
        if not d:
            # Search by aliases
            d = MIBData.objects.filter(aliases=name).first()
        if d:
            return d.oid + tail
        return None

    @classmethod
    def get_name(cls, oid):
        """
        Get longest match name by OID
        """
        oid = OIDAlias.rewrite(oid)
        l_oid = oid.split(".")
        rest = []
        while l_oid:
            c_oid = ".".join(l_oid)
            d = MIBData.objects.filter(oid=c_oid).first()
            if d:
                return MIBAlias.rewrite(".".join([d.name] + rest))
            else:
                rest = [l_oid.pop()] + rest
        return oid

    @classmethod
    def get_name_and_syntax(cls, oid):
        """
        :return: (name, syntax)
        """
        oid = OIDAlias.rewrite(oid)
        l_oid = oid.split(".")
        rest = []
        while l_oid:
            c_oid = ".".join(l_oid)
            d = MIBData.objects.filter(oid=c_oid).first()
            if d:
                name = d.name
                if rest:
                    name += "." + ".".join(reversed(rest))
                return (MIBAlias.rewrite(name),
                        SyntaxAlias.rewrite(name, d.syntax))
            else:
                rest += [l_oid.pop()]
        return oid, None

    @property
    def depended_by(self):
        return MIB.objects.filter(depends_on=self.name)

    def clean(self):
        """
        Gracefully wipe out MIB data
        """
        # Delete data without aliases
        MIBData.objects.filter(mib=self.id, aliases=[]).delete()
        # Dereference aliases
        prefs = {}  # MIB -> Preference
        for o in MIBData.objects.filter(mib=self.id, aliases__ne=[]):
            if not o.aliases:  # NO aliases
                o.delete()
                continue
            if len(o.aliases) == 1:  # Only one alias
                ba = o.aliases[0]
            else:
                # Find preferable alias
                ba = None
                lp = None
                for a in o.aliases:
                    am = a.split("::")[0]
                    # Find MIB preference
                    if am not in prefs:
                        p = MIBPreference(mib=am).first()
                        if p is None:
                            raise Exception("No preference for %s" % am)
                        prefs[am] = p.preference
                    p = prefs[am]
                    if lp is None or p < lp:
                        # Better
                        ba = a
                        lp = p
            # Promote preferrable alias
            o.name = ba
            o.aliases = [a for a in o.aliases if a != ba]
            o.save()


class MIBData(nosql.Document):
    meta = {
        "collection": "noc.mibdata",
        "allow_inheritance": False,
        "indexes": ["oid", "name", "mib", "aliases"]
    }
    mib = nosql.PlainReferenceField(MIB)
    oid = nosql.StringField(required=True, unique=True)
    name = nosql.StringField(required=True)
    description = nosql.StringField(required=False)
    syntax = nosql.DictField(required=False)
    aliases = nosql.ListField(nosql.StringField(), default=[])

    def __unicode__(self):
        return self.name


class MIBAlias(nosql.Document):
    """
    MIB Aliases
    """
    meta = {
        "collection": "noc.mibaliases",
        "allow_inheritance": False
    }
    rewrite_mib = nosql.StringField(unique=True)
    to_mib = nosql.StringField()
    is_builtin = nosql.BooleanField(default=False)

    ## Lookup cache
    cache = None

    def __unicode__(self):
        return u"%s -> %s" % (self.rewrite_mib, self.to_mib)

    @classmethod
    def rewrite(cls, name):
        """
        Rewrite OID with alias if any
        """
        if cls.cache is None:
            # Initialize cache
            cls.cache = dict([(a.rewrite_mib, a.to_mib)
                for a in cls.objects.all()])
        # Lookup
        if "::" in name:
            mib, rest = name.split("::", 1)
            return "%s::%s" % (cls.cache.get(mib, mib), rest)
        return cls.cache.get(name, name)


##
## Alarms and Events
##
class AlarmSeverity(nosql.Document):
    """
    Alarm severities
    """
    meta = {
        "collection": "noc.alarmseverities",
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True, unique=True)
    is_builtin = nosql.BooleanField(default=False)
    description = nosql.StringField(required=False)
    severity = nosql.IntField(required=True)
    style = nosql.ForeignKeyField(Style)

    def __unicode__(self):
        return self.name

    @classmethod
    def get_severity(cls, severity):
        """
        Returns Alarm Severity instance corresponding to numeric value
        """
        s = cls.objects.filter(severity__lte=severity).order_by("-severity").first()
        if not s:
            s = cls.objects.order_by("severity").first()
        return s


class AlarmClassVar(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True)
    description = nosql.StringField(required=False)
    default = nosql.StringField(required=False)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (self.name == other.name and
                self.description == other.description and
                self.default == other.default)


class DataSource(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = nosql.StringField()
    datasource = nosql.StringField()
    search = nosql.DictField()

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (self.name == other.name and
                self.datasource == other.datasource and
                self.search == other.search)


class AlarmRootCauseCondition(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    
    name = nosql.StringField(required=True)
    root = nosql.PlainReferenceField("AlarmClass")
    window = nosql.IntField(required=True)
    condition = nosql.StringField(default="True")
    match_condition = nosql.DictField(required=True)
    
    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (self.name == other.name and
                ((self.root is None and other.root is None) or
                    (self.root and other.root and self.root.id == other.root.id)) and
                self.window == other.window and
                self.condition == other.condition and
                self.match_condition == other.match_condition)


class AlarmClassCategory(nosql.Document):
    meta = {
        "collection": "noc.alartmclasscategories",  # @todo: Fix bug
        "allow_inheritance": False
    }
    name = nosql.StringField()
    parent = nosql.ObjectIdField(required=False)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if " | " in self.name:
            p_name = " | ".join(self.name.split(" | ")[:-1])
            p = AlarmClassCategory.objects.filter(name=p_name).first()
            if not p:
                p = AlarmClassCategory(name=p_name)
                p.save()
            self.parent = p.id
        else:
            self.parent = None
        super(AlarmClassCategory, self).save(*args, **kwargs)


class AlarmClass(nosql.Document):
    """
    Alarm class
    """
    meta = {
        "collection": "noc.alarmclasses",
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True, unique=True)
    is_builtin = nosql.BooleanField(default=False)
    description = nosql.StringField(required=False)
    # Create or not create separate Alarm
    # if is_unique is True and there is active alarm
    # Do not create separate alarm if is_unique set
    is_unique = nosql.BooleanField(default=False)
    # List of var names to be used as discriminator key
    discriminator = nosql.ListField(nosql.StringField())
    # Can alarm status be cleared by user
    user_clearable = nosql.BooleanField(default=True)
    # Default alarm severity
    default_severity = nosql.PlainReferenceField(AlarmSeverity)
    #
    datasources = nosql.ListField(nosql.EmbeddedDocumentField(DataSource))
    vars = nosql.ListField(nosql.EmbeddedDocumentField(AlarmClassVar))
    # Text messages
    # alarm_class.text -> locale -> {
    #     "subject_template" -> <template>
    #     "body_template" -> <template>
    #     "symptoms" -> <text>
    #     "probable_causes" -> <text>
    #     "recommended_actions" -> <text>
    # }
    text = nosql.DictField(required=True)
    # Flap detection
    flap_condition = nosql.StringField(required=False,
                                       choices=[("none", "none"),
                                                ("count", "count")],
                                       default=None)
    flap_window = nosql.IntField(required=False, default=0)
    flap_threshold = nosql.FloatField(required=False, default=0)
    # RCA
    root_cause = nosql.ListField(nosql.EmbeddedDocumentField(AlarmRootCauseCondition))
    #
    category = nosql.ObjectIdField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        c_name = " | ".join(self.name.split(" | ")[:-1])
        c = AlarmClassCategory.objects.filter(name=c_name).first()
        if not c:
            c = AlarmClassCategory(name=c_name)
            c.save()
        self.category = c.id
        super(AlarmClass, self).save(*args, **kwargs)

    def get_discriminator(self, vars):
        """
        Calculate discriminator hash
        
        :param vars: Dict of vars
        :returns: Discriminator hash
        """
        if vars:
            ds = [str(vars[n]) for n in self.discriminator]
            return hashlib.sha1("\x00".join(ds)).hexdigest()
        else:
            return hashlib.sha1("").hexdigest()


class EventClassVar(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True)
    description = nosql.StringField(required=False)
    type = nosql.StringField(required=True,
                             choices=[(x, x) for x in ("str", "int",
                                      "ipv4_address", "ipv6_address", "ip_address",
                                      "ipv4_prefix", "ipv6_prefix", "ip_prefix",
                                      "mac", "interface_name", "oid")])
    required = nosql.BooleanField(required=True)
    
    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (self.name == other.name and
                self.description == other.description and
                self.type == other.type and
                self.required == other.required)


class EventDispositionRule(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    # Name, unique within event class
    name = nosql.StringField(required=True, default="dispose")
    # Python logical expression to check wrether the rules
    # is applicable or not.
    condition = nosql.StringField(required=True, default="True")
    # What to do with disposed event:
    #    drop - delete and stop disposition
    #    ignore - stop disposition
    #    pyrule - execute pyrule
    #    raise - raise an alarm
    #    clear - clear alarm
    #
    action = nosql.StringField(required=True,
                               choices=[(x, x) for x in
                                    ("drop",
                                    "ignore",
                                    "raise",
                                    "clear")
                                ])
    # Applicable for actions: raise and clear
    alarm_class = nosql.PlainReferenceField(AlarmClass, required=False)
    # Additional condition. Raise or clear action
    # will be performed only if additional events occured during time window
    combo_condition = nosql.StringField(required=False,
                                        default="none",
                                        choices=[(x, x) for x in (
                                            "none",  # Apply action immediately
                                            "frequency",  # Apply when event
                                                          # firing rate exceeds
                                                          # combo_count times
                                                          # during combo_window
                                            "sequence",   # Apply action if event
                                                          # followed by all combo events
                                                          # in strict order
                                            "all",  # Apply action if event
                                                    # followed by all combo events
                                                    # in no specific order
                                            "any"   # Apply action if event
                                                    # followed by any of combo events
                                            )])
    # Time window for combo events in seconds
    combo_window = nosql.IntField(required=False, default=0)
    # Applicable for frequency.
    combo_count = nosql.IntField(required=False, default=0)
    # Applicable for sequence, all and any combo_condition
    combo_event_classes = nosql.ListField(nosql.PlainReferenceField("EventClass"),
                                          required=False,
                                          default=[])
    # event var name -> alarm var name mappings
    # try to use direct mapping if not set explicitly
    var_mapping = nosql.DictField(required=False)
    # Stop event disposition if True or continue with next rule
    stop_disposition = nosql.BooleanField(required=False, default=True)

    def __unicode__(self):
        return "%s: %s" % (self.action, self.alarm_class.name)

    def __eq__(self, other):
        for a in ["name", "condition", "action", "pyrule", "window",
                  "var_mapping", "stop_disposition"]:
            if hasattr(self, a) != hasattr(other, a):
                return False
            if hasattr(self, a) and getattr(self, a) != getattr(other, a):
                return False
        if (self.alarm_class is None and other.alarm_class is None):
            return True
        if (self.alarm_class is None or
            other.alarm_class is None or
            self.alarm_class.name != other.alarm_class.name):
            return False
        return True


class EventSuppressionRule(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = nosql.StringField()
    condition = nosql.StringField(required=True, default="True")
    event_class = nosql.PlainReferenceField("EventClass", required=True)
    match_condition = nosql.DictField(required=True, default={})
    window = nosql.IntField(required=True, default=3600)
    suppress = nosql.BooleanField(required=True, default=True)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (self.name == other.name and self.condition == other.condition and
                self.event_class.id == other.event_class.id and
                self.match_condition == other.match_condition and
                self.window == other.window and self.suppress == other.suppress)


class EventClassCategory(nosql.Document):
    meta = {
        "collection": "noc.eventclasscategories",
        "allow_inheritance": False
    }
    name = nosql.StringField()
    parent = nosql.ObjectIdField(required=False)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if " | " in self.name:
            p_name = " | ".join(self.name.split(" | ")[:-1])
            p = EventClassCategory.objects.filter(name=p_name).first()
            if not p:
                p = EventClassCategory(name=p_name)
                p.save()
            self.parent = p.id
        else:
            self.parent = None
        super(EventClassCategory, self).save(*args, **kwargs)


class EventClass(nosql.Document):
    """
    Event class
    """
    meta = {
        "collection": "noc.eventclasses",
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True, unique=True)
    is_builtin = nosql.BooleanField(default=False)
    description = nosql.StringField(required=False)
    # Event processing action:
    #     D - Drop
    #     L - Log as processed, do not move to archive
    #     A - Log as processed, move to archive
    action = nosql.StringField(required=True, choices=[("D", "Drop"),
                                                        ("L", "Log"),
                                                        ("A", "Log & Archive")])
    vars = nosql.ListField(nosql.EmbeddedDocumentField(EventClassVar))
    # Text messages
    # alarm_class.text -> locale -> {
    #     "subject_template" -> <template>
    #     "body_template" -> <template>
    #     "symptoms" -> <text>
    #     "probable_causes" -> <text>
    #     "recommended_actions" -> <text>
    # }
    text = nosql.DictField(required=True)

    disposition = nosql.ListField(nosql.EmbeddedDocumentField(EventDispositionRule))
    repeat_suppression = nosql.ListField(nosql.EmbeddedDocumentField(EventSuppressionRule))
    #
    category = nosql.ObjectIdField()
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        c_name = " | ".join(self.name.split(" | ")[:-1])
        c = EventClassCategory.objects.filter(name=c_name).first()
        if not c:
            c = EventClassCategory(name=c_name)
            c.save()
        self.category = c.id
        super(EventClass, self).save(*args, **kwargs)
    
    @property
    def display_action(self):
        return {
            "D": "Drop",
            "L": "Log",
            "A": "Log and Archive"
        }[self.action]

    @property
    def conditional_pyrule_name(self):
        return ("fm_dc_" + rulename_quote(self.name)).lower()


##
## Classification rules
##
class EventClassificationRuleVar(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True)
    value = nosql.StringField(required=False)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (self.name == other.name and
                self.value == other.value)


class EventClassificationRuleCategory(nosql.Document):
    meta = {
        "collection": "noc.eventclassificationrulecategories",
        "allow_inheritance": False
    }
    name = nosql.StringField()
    parent = nosql.ObjectIdField(required=False)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if " | " in self.name:
            p_name = " | ".join(self.name.split(" | ")[:-1])
            p = EventClassificationRuleCategory.objects.filter(name=p_name).first()
            if not p:
                p = EventClassificationRuleCategory(name=p_name)
                p.save()
            self.parent = p.id
        else:
            self.parent = None
        super(EventClassificationRuleCategory, self).save(*args, **kwargs)


class EventClassificationPattern(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    key_re = nosql.StringField(required=True)
    value_re = nosql.StringField(required=True)
    
    def __unicode__(self):
        return u"'%s' : '%s'" % (self.key_re, self.value_re)

    def __eq__(self, other):
        return self.key_re == other.key_re and self.value_re == other.value_re


class EventClassificationRule(nosql.Document):
    """
    Classification rules
    """
    meta = {
        "collection": "noc.eventclassificationrules",
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True, unique=True)
    is_builtin = nosql.BooleanField(required=True)
    description = nosql.StringField(required=False)
    event_class = nosql.PlainReferenceField(EventClass, required=True)
    preference = nosql.IntField(required=True, default=1000)
    patterns = nosql.ListField(nosql.EmbeddedDocumentField(EventClassificationPattern))
    datasources = nosql.ListField(nosql.EmbeddedDocumentField(DataSource))
    vars = nosql.ListField(nosql.EmbeddedDocumentField(EventClassificationRuleVar))
    #
    category = nosql.ObjectIdField()
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        c_name = " | ".join(self.name.split(" | ")[:-1])
        c = EventClassificationRuleCategory.objects.filter(name=c_name).first()
        if not c:
            c = EventClassificationRuleCategory(name=c_name)
            c.save()
        self.category = c.id
        super(EventClassificationRule, self).save(*args, **kwargs)

    @property
    def short_name(self):
        return self.name.split(" | ")[-1]

    def to_json(self):
        r = ["{"]
        r += ["    \"name\": \"%s\"," % jq(self.name)]
        r += ["    \"description\": \"%s\"," % jq(self.description)]
        r += ["    \"event_class__name\": \"%s\"," % jq(self.event_class.name)]
        r += ["    \"preference\": %d," % self.preference]
        # Dump datasources
        if self.datasources:
            r += ["    \"datasources\": ["]
            jds = []
            for ds in self.datasources:
                x = ["        \"name\": \"%s\"" % jq(ds.name)]
                x += ["        \"datasource\": \"%s\"" % jq(ds.datasource)]
                ss = []
                for k in sorted(ds.search):
                    ss += ["            \"%s\": \"%s\"" % (jq(k), jq(ds.search[k]))]
                x += ["            \"search\": {"]
                x += [",\n".join(ss)]
                x += ["            }"]
                jds += ["        {", ",\n".join(x), "        }"]
            r += [",\n\n".join(jds)]
            r += ["    ],"]
        # Dump vars
        if self.vars:
            r += ["    \"vars\": ["]
            vars = []
            for v in self.vars:
                vd = ["        {"]
                vd += ["            \"name\": \"%s\"" % jq(v.name)]
                vd += ["            \"value\": \"%s\"" % jq(v.value)]
                vd += ["        }"]
                vars += ["\n".join(vd)]
            r += [",\n\n".join(vars)]
            r += ["    ],"]
        # Dump patterns
        r += ["    \"patterns\": ["]
        patterns = []
        for p in self.patterns:
            pt = []
            pt += ["        {"]
            pt += ["            \"key_re\": \"%s\"," % jq(p.key_re)]
            pt += ["            \"value_re\": \"%s\"" % jq(p.value_re)]
            pt += ["        }"]
            patterns += ["\n".join(pt)]
        r += [",\n".join(patterns)]
        r += ["    ]"]
        r += ["}"]
        return "\n".join(r)


class CloneClassificationRule(nosql.Document):
    """
    Classification rules cloning
    """
    meta = {
        "collection": "noc.cloneclassificationrules",
        "allow_inheritance": False
    }

    name = nosql.StringField(unique=True)
    re = nosql.StringField(default="^.*$")
    key_re = nosql.StringField(default="^.*$")
    value_re = nosql.StringField(default="^.*$")
    is_builtin = nosql.BooleanField(default=False)
    rewrite_from = nosql.StringField()
    rewrite_to = nosql.StringField()

    def __unicode__(self):
        return self.name

##
## Events.
## Events are divided to 4 statuses:
##     New
##     Active
##     Failed
##     Archived
##
EVENT_STATUS_NAME = {
    "N": "New",
    "F": "Failed",
    "A": "Active",
    "S": "Archived"
}


class EventLog(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False,
    }
    timestamp = nosql.DateTimeField()
    from_status = nosql.StringField(max_length=1,
                                    regex=r"^[NFAS]$", required=True)
    to_status = nosql.StringField(max_length=1,
                                  regex=r"^[NFAS]$", required=True)
    message = nosql.StringField()

    def __unicode__(self):
        return u"%s [%s -> %s]: %s" % (self.timestamp, self.from_status,
                                       self.to_status, self.message)


class NewEvent(nosql.Document):
    """
    Raw unclassified event as written by SAE
    """
    meta = {
        "collection": "noc.events.new",
        "allow_inheritance": False,
        "indexes": ["timestamp"]
    }
    status = "N"
    # Fields
    timestamp = nosql.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject, required=True)
    raw_vars = nosql.RawDictField(required=True)
    log = nosql.ListField(nosql.EmbeddedDocumentField(EventLog))

    def __unicode__(self):
        return unicode(self.id)
    
    def mark_as_failed(self, version, traceback):
        """
        Move event into noc.events.failed
        """
        message = "Failed to classify on NOC version %s" % version
        log = self.log + [EventLog(timestamp=datetime.datetime.now(),
                                   from_status="N", to_status="F",
                                   message=message)]
        e = FailedEvent(id=self.id, timestamp=self.timestamp,
                        managed_object=self.managed_object,
                        raw_vars=self.raw_vars, version=version,
                        traceback=traceback, log=log)
        e.save()
        self.delete()
        return e
    
    @property
    def source(self):
        """
        Event source or None
        """
        if self.raw_vars and "source" in self.raw_vars:
            return self.raw_vars["source"]
        return None
    
    def log_message(self, message):
        self.log += [EventLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        self.save()


class FailedEvent(nosql.Document):
    """
    Events that caused noc-classifier traceback
    """
    meta = {
        "collection": "noc.events.failed",
        "allow_inheritance": False
    }
    status = "F"
    # Fields
    timestamp = nosql.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject, required=True)
    raw_vars = nosql.RawDictField(required=True)
    version = nosql.StringField(required=True)  # NOC version caused traceback
    traceback = nosql.StringField()
    log = nosql.ListField(nosql.EmbeddedDocumentField(EventLog))
    
    def __unicode__(self):
        return unicode(self.id)
    
    def mark_as_new(self, message=None):
        """
        Move to unclassified queue
        """
        if message is None:
            message = "Reclassification requested"
        log = self.log + [EventLog(timestamp=datetime.datetime.now(),
                                   from_status="F", to_status="N",
                                   message=message)]
        e = NewEvent(id=self.id, timestamp=self.timestamp,
                     managed_object=self.managed_object, raw_vars=self.raw_vars,
                     log=log)
        e.save()
        self.delete()
        return e

    def log_message(self, message):
        self.log += [EventLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        self.save()


class ActiveEvent(nosql.Document):
    """
    Event in the Active state
    """
    meta = {
        "collection": "noc.events.active",
        "allow_inheritance": False,
        "indexes": ["timestamp", "discriminator", "alarms"]
    }
    status = "A"
    # Fields
    timestamp = nosql.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject, required=True)
    event_class = nosql.PlainReferenceField(EventClass, required=True)
    start_timestamp = nosql.DateTimeField(required=True)
    repeats = nosql.IntField(required=True)
    raw_vars = nosql.RawDictField()
    resolved_vars = nosql.RawDictField()
    vars = nosql.DictField()
    log = nosql.ListField(nosql.EmbeddedDocumentField(EventLog))
    discriminator = nosql.StringField(required=False)
    alarms = nosql.ListField(nosql.ObjectIdField())

    def __unicode__(self):
        return u"%s" % self.id

    def mark_as_new(self, message=None):
        """
        Move to new queue
        """
        if message is None:
            message = "Reclassification requested"
        log = self.log + [EventLog(timestamp=datetime.datetime.now(),
                                   from_status="A", to_status="N",
                                   message=message)]
        e = NewEvent(id=self.id, timestamp=self.timestamp,
                     managed_object=self.managed_object, raw_vars=self.raw_vars,
                     log=log)
        e.save()
        self.delete()
        return e

    def mark_as_failed(self, version, traceback):
        """
        Move event into noc.events.failed
        """
        message = "Failed to classify on NOC version %s" % version
        log = self.log + [EventLog(timestamp=datetime.datetime.now(),
                                   from_status="N", to_status="F",
                                   message=message)]
        e = FailedEvent(id=self.id, timestamp=self.timestamp,
                        managed_object=self.managed_object,
                        raw_vars=self.raw_vars, version=version,
                        traceback=traceback, log=log)
        e.save()
        self.delete()
        return e

    def mark_as_archived(self, message):
        log = self.log + [EventLog(timestamp=datetime.datetime.now(),
                                   from_status="A", to_status="S",
                                   message=message)]
        e = ArchivedEvent(
            id=self.id,
            timestamp=self.timestamp,
            managed_object=self.managed_object,
            event_class=self.event_class,
            start_timestamp=self.start_timestamp,
            repeats=self.repeats,
            raw_vars=self.raw_vars,
            resolved_vars=self.resolved_vars,
            vars=self.vars,
            log=log,
            alarms=self.alarms
        )
        e.save()
        self.delete()
        return e

    def drop(self):
        """
        Mark event to be dropped. Only for use from event trigger pyrule.
        All further operations on event may lead to unpredictable results.
        Event actually deleted by noc-classifier
        """
        self.id = None

    @property
    def to_drop(self):
        """
        Check event marked to be dropped
        """
        return self.id is None

    def log_message(self, message):
        self.log += [EventLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        self.save()

    def log_suppression(self, timestamp):
        """
        Increate repeat count and update timestamp, if required
        """
        self.repeats += 1
        if timestamp > self.timestamp:
            self.timestamp = timestamp
        self.save()

    @property
    def duration(self):
        """
        Logged event duration in seconds
        """
        return total_seconds(self.timestamp - self.start_timestamp)

    def dispose_event(self):
        EventDispositionQueue(timestamp=datetime.datetime.now(),
                              event_id=self.id).save()

    def get_template_vars(self):
        """
        Prepare template variables
        """
        vars = self.vars.copy()
        vars.update({"event": self})
        return vars
        
    def get_translated_subject(self, lang):
        s = get_translated_template(lang, self.event_class.text,
                                    "subject_template",
                                    self.get_template_vars())
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s
    
    def get_translated_body(self, lang):
        return get_translated_template(lang, self.event_class.text,
                                       "body_template",
                                       self.get_template_vars())
    
    def get_translated_symptoms(self, lang):
        return get_translated_text(lang, self.event_class.text, "symptoms")

    def get_translated_probable_causes(self, lang):
        return get_translated_text(lang, self.event_class.text, "probable_causes")

    def get_translated_recommended_actions(self, lang):
        return get_translated_text(lang, self.event_class.text, "recommended_actions")

    @property
    def managed_object_id(self):
        """
        Hack to return managed_object.id without SQL lookup
        """
        o = self._data["managed_object"]
        if type(o) in (int, long):
            return o
        return o.id


class ArchivedEvent(nosql.Document):
    """
    """
    meta = {
        "collection": "noc.events.archive",
        "allow_inheritance": True,
        "indexes": ["timestamp", "alarms"]
    }
    status = "S"

    timestamp = nosql.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject, required=True)
    event_class = nosql.PlainReferenceField(EventClass, required=True)
    start_timestamp = nosql.DateTimeField(required=True)
    repeats = nosql.IntField(required=True)
    raw_vars = nosql.RawDictField()
    resolved_vars = nosql.RawDictField()
    vars = nosql.DictField()
    log = nosql.ListField(nosql.EmbeddedDocumentField(EventLog))
    alarms = nosql.ListField(nosql.ObjectIdField())

    def __unicode__(self):
        return u"%s" % self.id

    @property
    def duration(self):
        """
        Logged event duration in seconds
        """
        return total_seconds(self.timestamp - self.start_timestamp)

    def get_template_vars(self):
        """
        Prepare template variables
        """
        vars = self.vars.copy()
        vars.update({"event": self})
        return vars

    def get_translated_subject(self, lang):
        s = get_translated_template(lang, self.event_class.text,
                                    "subject_template",
                                    self.get_template_vars())
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s
    
    def get_translated_body(self, lang):
        return get_translated_template(lang, self.event_class.text,
                                       "body_template",
                                       self.get_template_vars())
    
    def get_translated_symptoms(self, lang):
        return get_translated_text(lang, self.event_class.text, "symptoms")

    def get_translated_probable_causes(self, lang):
        return get_translated_text(lang, self.event_class.text, "probable_causes")

    def get_translated_recommended_actions(self, lang):
        return get_translated_text(lang, self.event_class.text, "recommended_actions")


class AlarmLog(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    timestamp = nosql.DateTimeField()
    from_status = nosql.StringField(max_length=1,
                                    regex=r"^[AC]$", required=True)
    to_status = nosql.StringField(max_length=1,
                                  regex=r"^[AC]$", required=True)
    message = nosql.StringField()

    def __unicode__(self):
        return u"%s [%s -> %s]: %s" % (self.timestamp, self.from_status,
                                       self.to_status, self.message)

    
class ActiveAlarm(nosql.Document):
    meta = {
        "collection": "noc.alarms.active",
        "allow_inheritance": False,
        "indexes": ["timestamp", "discriminator", "root", "-severity"]
    }
    status = "A"
    
    timestamp = nosql.DateTimeField(required=True)
    last_update = nosql.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject)
    alarm_class = nosql.PlainReferenceField(AlarmClass)
    severity = nosql.IntField(required=True)
    vars = nosql.DictField()
    # Calculated alarm discriminator
    # Has meaning only for alarms with is_unique flag set
    # Calculated as sha1("value1\x00....\x00valueN").hexdigest()
    discriminator = nosql.StringField(required=False)
    log = nosql.ListField(nosql.EmbeddedDocumentField(AlarmLog))
    # Responsible person
    owner = nosql.ForeignKeyField(User, required=False)
    # List of subscribers
    subscribers = nosql.ListField(nosql.ForeignKeyField(User))
    #
    custom_subject = nosql.StringField(required=False)
    custom_style = nosql.ForeignKeyField(Style, required=False)
    # RCA
    # Reference to root cause (Active Alarm or Archived Alarm instance)
    root = nosql.ObjectIdField(required=False)

    def __unicode__(self):
        return u"%s" % self.id

    def save(self, *args, **kwargs):
        if not self.last_update:
            self.last_update = self.timestamp
        return super(ActiveAlarm, self).save(*args, **kwargs)

    def change_severity(self, user="", delta=None, severity=None):
        """
        Change alarm severity
        """
        if isinstance(user, User):
            user = user.username
        if delta:
            self.severity = max(0, self.severity + delta)
            if delta > 0:
                self.log_message("%s has increased event severity by %s" % (user, delta))
            else:
                self.log_message("%s has decreased event severity by %s" % (user, delta))
        elif severity:
            self.severity = severity.severity
            self.log_message("%s has changed severity to %s" % (user, severity.name))
        self.save()

    def log_message(self, message):
        self.log += [AlarmLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        self.save()

    def contribute_event(self, e):
        # Update timestamp
        if e.timestamp < self.timestamp:
            self.timestamp = e.timestamp
        else:
            self.last_update = max(self.last_update, e.timestamp)
        self.save()
        if self.id not in e.alarms:
            e.alarms += [self.id]
            e.save()

    def clear_alarm(self, message):
        ts = datetime.datetime.now()
        log = self.log + [AlarmLog(timestamp=ts, from_status="A",
                                   to_status="C", message=message)]
        a = ArchivedAlarm(id=self.id,
                          timestamp=self.timestamp,
                          clear_timestamp=ts,
                          managed_object=self.managed_object,
                          alarm_class=self.alarm_class,
                          severity=self.severity,
                          vars=self.vars,
                          log=log,
                          root=self.root
                          )
        a.save()
        self.delete()
        return a

    def get_template_vars(self):
        """
        Prepare template variables
        """
        vars = self.vars.copy()
        vars.update({"alarm": self})
        return vars

    def get_translated_subject(self, lang):
        s = get_translated_template(lang, self.alarm_class.text,
                                    "subject_template",
                                    self.get_template_vars())
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s
    
    def get_translated_body(self, lang):
        return get_translated_template(lang, self.alarm_class.text,
                                       "body_template",
                                       self.get_template_vars())
    
    def get_translated_symptoms(self, lang):
        return get_translated_text(lang, self.alarm_class.text, "symptoms")

    def get_translated_probable_causes(self, lang):
        return get_translated_text(lang, self.alarm_class.text, "probable_causes")

    def get_translated_recommended_actions(self, lang):
        return get_translated_text(lang, self.alarm_class.text, "recommended_actions")

    def change_owner(self, user):
        """
        Change alarm's owner
        """
        self.owner = user
        self.save()

    def subscribe(self, user):
        """
        Change alarm's subscribers
        """
        if user.id not in self.subscribers:
            self.subscribers += [user.id]
            self.save()
    
    def unsubscribe(self, user):
        if self.is_subscribed(user):
            self.subscribers = [u.id for u in self.subscribers if u != user.id]
            self.save()
    
    def is_owner(self, user):
        return self.owner == user
    
    def is_subscribed(self, user):
        return user.id in self.subscribers
    
    @property
    def is_unassigned(self):
        return self.owner is None
    
    @property
    def duration(self):
        dt = datetime.datetime.now() - self.timestamp
        return dt.days * 86400 + dt.seconds
    
    @property
    def display_duration(self):
        duration = datetime.datetime.now() - self.timestamp
        secs = duration.seconds % 60
        mins = (duration.seconds / 60) % 60
        hours = (duration.seconds / 3600) % 24
        days = duration.days
        r = "%02d:%02d:%02d" % (hours, mins, secs)
        if days:
            r = "%dd %s" % (days, r)
        return r
    
    @property
    def effective_style(self):
        if self.custom_style:
            return self.custom_style
        else:
            return AlarmSeverity.get_severity(self.severity).style

    def set_root(self, root_alarm):
        """
        Set root cause
        """
        if self.root:
            return
        if self.id == root_alarm.id:
            raise Exception("Cannot set self as root cause")
        # Detect loop
        root = root_alarm
        while root:
            root = root.root
            if root == self.id:
                return
        # Set root
        self.root = root_alarm.id
        self.log_message("Alarm %s has been marked as root cause" % root_alarm.id)
        # self.save()  Saved by log_message
        root_alarm.log_message("Alarm %s has meen marked as child" % self.id)


class ArchivedAlarm(nosql.Document):
    meta = {
        "collection": "noc.alarms.archived",
        "allow_inheritance": False,
        "indexes": ["root"]
    }
    status = "C"
    
    timestamp = nosql.DateTimeField(required=True)
    clear_timestamp = nosql.DateTimeField(required=True)
    managed_object = nosql.ForeignKeyField(ManagedObject)
    alarm_class = nosql.PlainReferenceField(AlarmClass)
    severity = nosql.IntField(required=True)
    vars = nosql.DictField()
    log = nosql.ListField(nosql.EmbeddedDocumentField(AlarmLog))
    # RCA
    # Reference to root cause (Active Alarm or Archived Alarm instance)
    root = nosql.ObjectIdField(required=False)
    
    def __unicode__(self):
        return u"%s" % self.id

    def log_message(self, message):
        self.log += [AlarmLog(timestamp=datetime.datetime.now(),
                     from_status=self.status, to_status=self.status,
                     message=message)]
        self.save()

    def get_template_vars(self):
        """
        Prepare template variables
        """
        vars = self.vars.copy()
        vars.update({"event": self})
        return vars

    def get_translated_subject(self, lang):
        s = get_translated_template(lang, self.alarm_class.text,
                                    "subject_template",
                                    self.get_template_vars())
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s

    def get_translated_body(self, lang):
        return get_translated_template(lang, self.alarm_class.text,
                                       "body_template",
                                       self.get_template_vars())
    
    def get_translated_symptoms(self, lang):
        return get_translated_text(lang, self.alarm_class.text, "symptoms")

    def get_translated_probable_causes(self, lang):
        return get_translated_text(lang, self.alarm_class.text, "probable_causes")

    def get_translated_recommended_actions(self, lang):
        return get_translated_text(lang, self.alarm_class.text, "recommended_actions")

    @property
    def duration(self):
        dt = self.clear_timestamp - self.timestamp
        return dt.days * 86400 + dt.seconds
    
    @property
    def display_duration(self):
        duration = self.clear_timestamp - self.timestamp
        secs = duration.seconds % 60
        mins = (duration.seconds / 60) % 60
        hours = (duration.seconds / 3600) % 24
        days = duration.days
        if days:
            return "%dd %02d:%02d:%02d" % (days, hours, mins, secs)
        else:
            return "%02d:%02d:%02d" % (hours, mins, secs)

    @property
    def effective_style(self):
        return AlarmSeverity.get_severity(self.severity).style

    def set_root(self, root_alarm):
        pass


class IgnoreEventRules(models.Model):
    class Meta:
        verbose_name = "Ignore Event Rule"
        verbose_name_plural = "Ignore Event Rules"
        unique_together = [("left_re", "right_re")]

    name = models.CharField("Name", max_length=64, unique=True)
    left_re = models.CharField("Left RE", max_length=256)
    right_re = models.CharField("Right Re", max_length=256)
    is_active = models.BooleanField("Is Active", default=True)
    description = models.TextField("Description", null=True, blank=True)

    def __unicode__(self):
        return u"%s (%s, %s)" % (self.name, self.left_re, self.right_re)


class EventTrigger(models.Model):
    class Meta:
        verbose_name = _("Event Trigger")
        verbose_name_plural = _("Event Triggers")

    name = models.CharField(_("Name"), max_length=64, unique=True)
    is_enabled = models.BooleanField(_("Is Enabled"), default=True)
    event_class_re = models.CharField(_("Event class RE"), max_length=256)
    condition = models.CharField(_("Condition"), max_length=256, default="True")
    time_pattern = models.ForeignKey(TimePattern,
                                     verbose_name=_("Time Pattern"),
                                     null=True, blank=True)
    selector = models.ForeignKey(ManagedObjectSelector,
                                 verbose_name=_("Managed Object Selector"),
                                 null=True, blank=True)
    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name=_("Notification Group"),
                                           null=True, blank=True)
    template = models.ForeignKey(NOCTemplate,
                                 verbose_name=_("Template"),
                                 null=True, blank=True)
    pyrule = models.ForeignKey(PyRule,
                               verbose_name=_("pyRule"),
                               null=True, blank=True,
                               limit_choices_to={"interface": "IEventTrigger"})
    
    def __unicode__(self):
        return "%s <<<%s>>>" % (self.event_class_re, self.condition)


class AlarmTrigger(models.Model):
    class Meta:
        verbose_name = _("Alarm Trigger")
        verbose_name_plural = _("Alarm Triggers")

    name = models.CharField(_("Name"), max_length=64, unique=True)
    is_enabled = models.BooleanField(_("Is Enabled"), default=True)
    alarm_class_re = models.CharField(_("Alarm class RE"), max_length=256)
    condition = models.CharField(_("Condition"), max_length=256, default="True")
    time_pattern = models.ForeignKey(TimePattern,
                                     verbose_name=_("Time Pattern"),
                                     null=True, blank=True)
    selector = models.ForeignKey(ManagedObjectSelector,
                                 verbose_name=_("Managed Object Selector"),
                                 null=True, blank=True)
    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name=_("Notification Group"),
                                           null=True, blank=True)
    template = models.ForeignKey(NOCTemplate,
                                 verbose_name=_("Template"),
                                 null=True, blank=True)
    pyrule = models.ForeignKey(PyRule,
                               verbose_name=_("pyRule"),
                               null=True, blank=True,
                               limit_choices_to={"interface": "IAlarmTrigger"})
    
    def __unicode__(self):
        return "%s <<<%s>>>" % (self.alarm_class_re, self.condition)


class EventDispositionQueue(nosql.Document):
    meta = {
        "collection": "noc.events.disposition",
        "allow_inheritance": False,
    }
    timestamp = nosql.DateTimeField(required=True)
    event_id = nosql.ObjectIdField(required=True)

    def __unicode__(self):
        return str(self.event_id)


class Enumeration(nosql.Document):
    meta = {
        "collection": "noc.enumerations",
        "allow_inheritance": False
    }

    name = nosql.StringField(unique=True)
    is_builtin = nosql.BooleanField(default=False)
    values = nosql.DictField()  # value -> [possible combinations]

    def __unicode__(self):
        return self.name

    
##
## Event/Alarm text decoder
##
def get_translated_text(lang, texts, name):
    if lang not in texts:
        # Fallback to "en" when no translation for language
        lang = "en"
    if lang in texts and name not in texts[lang] and lang != "en":
        # Fallback to "en" when not translation for message
        lang = "en"
    try:
        return texts[lang][name]
    except KeyError:
        return "--- UNTRANSLATED MESSAGE ---"


def get_translated_template(lang, texts, name, vars):
    return Template(get_translated_text(lang, texts, name)).render(Context(vars))


def get_event(event_id):
        """
        Get event by event_id
        """
        for ec in (ActiveEvent, ArchivedEvent, FailedEvent, NewEvent):
            e = ec.objects.filter(id=event_id).first()
            if e:
                return e
        return None


def get_alarm(alarm_id):
        """
        Get alarm by alarm_id
        """
        for ac in (ActiveAlarm, ArchivedAlarm):
            a = ac.objects.filter(id=alarm_id).first()
            if a:
                return a
        return None


def get_object_status(managed_object):
    """
    Returns current object status
    
    :param managed_object: Managed Object instance
    :returns: True, if object is up, False, if object is down, None, if object
              is unreachable
    """
    ac = AlarmClass.objects.get(name="NOC | Managed Object | Ping Failed")
    a = ActiveAlarm.objects.filter(managed_object=managed_object.id,
                                   alarm_class=ac.id).first()
    if a is None:
        # No active alarm, object is up
        return True
    elif a.root:
        # Inferred alarm, object status is unknown
        return None
    else:
        return False
