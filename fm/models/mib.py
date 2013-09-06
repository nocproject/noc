# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIB model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import subprocess
import re
import imp
import datetime
import os
## NOC modules
import noc.lib.nosql as nosql
from noc.settings import config
from noc.lib.fileutils import temporary_file, safe_rewrite
from error import (MIBNotFoundException, MIBRequiredException,
                   OIDCollision)
from mibpreference import MIBPreference
from mibalias import MIBAlias
from syntaxalias import SyntaxAlias
from oidalias import OIDAlias
from noc.lib.validators import is_oid
from noc.lib.escape import fm_unescape, fm_escape
from noc.lib.snmputils import render_tc

## Regular expression patterns
rx_module_not_found = re.compile(r"{module-not-found}.*`([^']+)'")
rx_tailing_numbers = re.compile(r"^(\S+?)((?:\.\d+)*)$")



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

    MIBRequiredException = MIBRequiredException

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
        # Build SMIPATH variable for smidump
        # to exclude locally installed MIBs
        smipath = ["share/mibs", "local/share/mibs"]
        # Pass MIB through smilint to detect missed modules
        f = subprocess.Popen(
            [config.get("path", "smilint"), "-m", path],
            stderr=subprocess.PIPE,
            env={"SMIPATH": ":".join(smipath)}).stderr
        for l in f:
            match = rx_module_not_found.search(l.strip())
            if match:
                raise MIBRequiredException("Uploaded MIB",
                                           match.group(1))
        # Convert MIB to python module and load
        with temporary_file() as p:
            subprocess.check_call(
                [config.get("path", "smidump"), "-k", "-q",
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
            # Promote preferable alias
            o.name = ba
            o.aliases = [a for a in o.aliases if a != ba]
            o.save()

    @classmethod
    def resolve_vars(cls, vars):
        """
        Resolve FM key -> value dict according to MIBs

        :param cls:
        :param vars:
        :return:
        """
        r = {}
        for k in vars:
            if not is_oid(k):
                # Nothing to resolve
                continue
            v = fm_unescape(vars[k])
            rk, syntax = cls.get_name_and_syntax(k)
            rv = v
            if syntax:
                # Format value according to syntax
                if syntax["base_type"] == "Enumeration":
                    # Expand enumerated type
                    try:
                        rv = syntax["enum_map"][str(v)]
                    except KeyError:
                        pass
                elif syntax["base_type"] == "Bits":
                    # @todo: Fix ugly hack
                    if v.startswith("="):
                        xv = int(v[1:], 16)
                    else:
                        xv = 0
                        for c in v:
                            xv = (xv << 8) + ord(c)
                    # Decode
                    b_map = syntax.get("enum_map", {})
                    b = []
                    n = 0
                    while xv:
                        if xv & 1:
                            x = str(n)
                            if x in b_map:
                                b = [b_map[x]] + b
                            else:
                                b = ["%X" % (1 << n)]
                        n += 1
                        xv >>= 1
                    rv = "(%s)" % ",".join(b)
                else:
                    # Render according to TC
                    rv = render_tc(
                        v,
                        syntax["base_type"],
                        syntax.get("display_hint", None)
                    )
                    try:
                        unicode(rv, "utf8")
                    except:
                        # Escape invalid UTF8
                        rv = fm_escape(rv)
            else:
                try:
                    unicode(rv, "utf8")
                except:
                    # escape invalid UTF8
                    rv = fm_escape(rv)
            if is_oid(v):
                # Resolve OID in value
                rv = MIB.get_name(v)
            if rk != k or rv != v:
                r[rk] = rv
        return r


## Avoid circular references
from mibdata import MIBData