# ---------------------------------------------------------------------
# VCFilter model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from threading import Lock
import operator
from collections import defaultdict
from typing import List, Optional, Union, Tuple, FrozenSet, Dict

# Third-party modules
from django.db import models
import cachetools

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check

# from noc.main.models.label import Label
from noc.core.text import ranges_to_list

rx_vc_filter = re.compile(r"^\s*\d+\s*(-\d+\s*)?(,\s*\d+\s*(-\d+)?)*$")
id_lock = Lock()
match_lock = Lock()

MATCHED_SCOPES = {"untagged", "tagged"}


# @Label.match_labels(category="vcfilter")
@on_delete_check(
    check=[
        ("vc.VCBindFilter", "vc_filter"),
        ("vc.VCDomainProvisioningConfig", "vc_filter"),
        ("main.Label", "match_vlanfilter.vlan_filter"),
    ],
    clean_lazy_labels="vcfilter",
)
class VCFilter(NOCModel):
    """
    VC Filter
    """

    class Meta(object):
        verbose_name = "VC Filter"
        verbose_name_plural = "VC Filters"
        db_table = "vc_vcfilter"
        app_label = "vc"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    expression = models.CharField("Expression", max_length=256)
    description = models.TextField("Description", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _match_cache = cachetools.TTLCache(maxsize=50, ttl=120)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        try:
            return VCFilter.objects.get(id=id)
        except VCFilter.DoesNotExist:
            return None

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Check expression before save
        """
        VCFilter.compile(self.expression)
        super().save(*args, **kwargs)

    @classmethod
    def compile(cls, expression):
        """
        Compile VC Filter expression
        """
        if not rx_vc_filter.match(expression):
            raise SyntaxError
        r = []
        for x in expression.split(","):
            x = x.strip()
            if "-" in x:
                f, t = [int(c.strip()) for c in x.split("-")]
            else:
                f = int(x)
                t = f
            if t < f:
                raise SyntaxError
            r += [(f, t)]
        return r

    def get_compiled(self):
        if not hasattr(self, "_compiled_expression"):
            self._compiled_expression = VCFilter.compile(self.expression)
        return self._compiled_expression

    def check(self, vc):
        """
        Check filter matches VC
        """
        for f, t in self.get_compiled():
            if f <= vc <= t:
                return True
        return False

    def to_sql(self, name):
        """
        Compile VCFilter as SQL WHERE statement
        :param name: Field name
        :type name: str or unicode or int or long
        :return: SQL WHERE part
        """
        s = []
        if isinstance(name, str):
            name = '"%s"' % name.replace('"', '""')
        elif isinstance(name, int):
            name = "%d" % name
        else:
            raise ValueError("Invalid type for 'name'")
        for f, t in self.get_compiled():
            if f == t:
                s += ["(%s = %d)" % (name, f)]
            else:
                s += ["(%s BETWEEN %d AND %d)" % (name, f, t)]
        if not s:
            return "TRUE"
        else:
            return "(%s)" % " OR ".join(s)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_match_cache"), lock=lambda _: match_lock)
    def get_matcher(cls) -> Dict[FrozenSet, List["VCFilter"]]:
        r = defaultdict(list)
        for vc in VCFilter.objects.filter():
            r[frozenset(ranges_to_list(vc.expression))] += [vc]
        return r

    @classmethod
    def iter_match_vcfilter(cls, vlan_list: Union[int, List[int]]) -> Tuple["VCFilter", str]:
        if isinstance(vlan_list, int):
            vlan_list = [vlan_list]
        match_expressions = cls.get_matcher()
        vcs = set(vlan_list)
        for expr, vcfilters in match_expressions.items():
            r = vcs.intersection(expr)
            if r and vcs == expr:
                yield from iter((vc, "=") for vc in vcfilters)
            if r and not vcs - expr:
                yield from iter((vc, ">") for vc in vcfilters)
            if r and not expr - vcs:
                yield from iter((vc, "<") for vc in vcfilters)
            if r:
                yield from iter((vc, "&") for vc in vcfilters)

    @classmethod
    def iter_lazy_labels(cls, vcs: List[int], match_scope: Optional[str] = None):
        if match_scope and match_scope not in MATCHED_SCOPES:
            return
        match_scope = match_scope or ""
        if match_scope:
            match_scope += "::"
        for vc, condition in cls.iter_match_vcfilter(vcs):
            yield f"noc::vcfilter::{vc.name}::{match_scope}{condition}"
