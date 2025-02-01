# ---------------------------------------------------------------------
# MIB model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import threading
from typing import Optional, List, Dict, Union
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, DateTimeField, IntField, ListField, DictField
import cachetools

# NOC modules
from noc.core.validators import is_oid
from noc.core.escape import fm_unescape, fm_escape
from noc.core.snmp.util import render_tc
from noc.core.model.decorator import on_delete_check
from noc.core.comp import smart_text
from .error import MIBNotFoundException, OIDCollision
from .mibpreference import MIBPreference
from .mibalias import MIBAlias
from .syntaxalias import SyntaxAlias
from .oidalias import OIDAlias

id_lock = threading.Lock()

# Regular expression patterns
rx_tailing_numbers = re.compile(r"^(\S+?)((?:\.\d+)*)$")

TRY_ENCODINGS = ["utf-8", "big5", "gb2312", "cp1251"]

DEFAULT_PREFERENCE = 999_999


@on_delete_check(check=[("fm.MIBData", "mib")])
class MIB(Document):
    meta = {"collection": "noc.mibs", "strict": False, "auto_create_index": False}
    name = StringField(required=True, unique=True)
    description = StringField(required=False)
    last_updated = DateTimeField(required=True)
    depends_on = ListField(StringField())
    # TC definitions: name -> SYNTAX
    typedefs = DictField(required=False)
    # Compiled MIB version
    version = IntField(required=False, default=0)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["MIB"]:
        return MIB.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return MIB.objects.filter(name=name).first()

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
                mib = MIB.get_by_name(syntax["module"])
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
                if not isinstance(sk, dict):
                    continue
                if "nodetype" in sk and sk["nodetype"] == "namednumber":
                    enum_map[sk["number"]] = k
            s["enum_map"] = enum_map
        if "format" in syntax:
            s["display_hint"] = syntax["format"]
        return s

    def load_data(self, data):
        """
        Load mib data from list of {oid:, name:, description:, syntax:}
        :param data:
        :return:
        """
        # Get MIB preference
        mp = MIBPreference.objects.filter(mib=self.name).first()
        mib_preference = mp.preference if mp else DEFAULT_PREFERENCE
        prefs = {}  # MIB Preferences cache
        # Prefetch existing MIB data
        oids = [v["oid"] for v in data]
        md_cache = {md["oid"]: md for md in MIBData.objects.filter(oid__in=oids)}
        # Load data
        for v in data:
            oid = v["oid"]
            oid_name = v["name"]
            description = v.get("description", None)
            o = md_cache.get(oid)
            if o is not None:
                if o.name == oid_name:
                    # Same oid, same name: duplicated declaration.
                    # Silently skip
                    continue
                # For same MIB - leave first entry
                if oid_name.split("::", 1)[0] == o.name.split("::", 1)[0]:
                    continue
                # Try to resolve collision
                if not mib_preference:
                    # No preference for target MIB
                    raise OIDCollision(oid, oid_name, o.name, "No preference for %s" % self.name)
                o_mib = o.name.split("::")[0]
                if o_mib not in prefs:
                    mp = MIBPreference.objects.filter(mib=o_mib).first()
                    if not mp and mib_preference == DEFAULT_PREFERENCE:
                        # No preference for destination MIB
                        raise OIDCollision(oid, oid_name, o.name, "No preference for %s" % o_mib)
                    elif not mp:
                        prefs[o_mib] = DEFAULT_PREFERENCE
                    else:
                        prefs[o_mib] = mp.preference  # Add to cache
                o_preference = prefs[o_mib]
                if mib_preference == o_preference:
                    # Equal preferences, collision
                    raise OIDCollision(oid, oid_name, o.name, "Equal preferences")
                if mib_preference < o_preference:
                    # Replace existing
                    o.aliases = list(sorted(o.aliases + [o.name]))
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
                MIBData(
                    mib=self.id, oid=oid, name=oid_name, description=description, syntax=syntax
                ).save()

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
        Resolve oid to name and syntax
        :param oid: OID
        :return: (name, syntax)
        """
        oid = OIDAlias.rewrite(oid)
        l_oid = oid.split(".")
        rest = []
        while l_oid:
            c_oid = ".".join(l_oid)
            name, syntax = MIBData.get_name_and_syntax(c_oid)
            if name:
                if rest:
                    name += "." + ".".join(reversed(rest))
                return MIBAlias.rewrite(name), SyntaxAlias.rewrite(name, syntax)
            rest += [l_oid.pop()]
        return oid, None

    @classmethod
    def get_description(cls, name):
        """
        Get longest match description by name
        """
        match = rx_tailing_numbers.match(name)
        if match:
            name, _ = match.groups()
        # Search by primary name
        d = MIBData.objects.filter(name=name).first()
        if not d:
            # Search by aliases
            d = MIBData.objects.filter(aliases=name).first()
        if d:
            return d.description
        else:
            return None

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
    def resolve_vars(cls, vars: Dict[str, bytes], include_raw: bool = False):
        """
        Resolve FM key -> value dict according to MIBs

        :param cls:
        :param vars:
        :param include_raw:
        :return:
        """
        r = {}
        if include_raw:
            r["raw"] = []
        for k in vars:
            if not is_oid(k):
                # Nothing to resolve
                continue
            rr = {"oid": k, "value": vars[k]}
            v = smart_text(fm_unescape(vars[k]))
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
                elif syntax["base_type"] == "ObjectIdentifier":
                    rv = smart_text(v)
                else:
                    # Render according to TC
                    rv = render_tc(v, syntax["base_type"], syntax.get("display_hint", None))
                    try:
                        smart_text(rv, encoding="utf8")
                    except ValueError:
                        # Escape invalid UTF8
                        rv = fm_escape(rv)
            else:
                try:
                    smart_text(rv, encoding="utf8")
                except ValueError:
                    # escape invalid UTF8
                    rv = fm_escape(rv)
            if is_oid(rv):
                # Resolve OID in value
                rv = MIB.get_name(rv)
            if rk != k or rv != v:
                r[rk] = rv
                rr["resolved_oid"] = rk
                rr["resolved_value"] = rv
            if include_raw:
                r["raw"].append(rr)
        return r

    @classmethod
    def guess_encoding(cls, s: bytes, encodings: Optional[List[str]] = None) -> str:
        """
        Try to guess encoding
        :param s:
        :param encodings:
        :return:
        """
        encodings = encodings or TRY_ENCODINGS
        exc = None
        for enc in encodings:
            try:
                return s.decode(enc)
            except UnicodeDecodeError as e:
                exc = e
        raise exc


# Avoid circular references
from .mibdata import MIBData
