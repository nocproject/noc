# ---------------------------------------------------------------------
# Prefix Table models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from typing import Union, List, Tuple, Iterable
from django.db import models

# NOC Modules
from noc.core.model.base import NOCModel
from noc.core.ip import IP
from noc.core.model.fields import CIDRField
from noc.core.model.decorator import on_delete_check
from noc.core.translation import ugettext as _


@on_delete_check(
    check=[("main.Label", "match_prefixfilter__prefix_table")],
    clean_lazy_labels="prefixfilter",
)
class PrefixTable(NOCModel):
    class Meta(object):
        verbose_name = _("Prefix Table")
        verbose_name_plural = _("Prefix Tables")
        db_table = "main_prefixtable"
        app_label = "main"
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=128, unique=True)
    description = models.TextField(_("Description"), null=True, blank=True)

    def __str__(self):
        return self.name

    def match(self, prefix):
        """
        Check the prefix is inside Prefix Table

        :param prefix: Prefix
        :type prefix: str
        :rtype: bool
        """
        p = IP.prefix(prefix)
        return (
            PrefixTablePrefix.objects.filter(table=self, afi=p.afi)
            .extra(where=["%s <<= prefix"], params=[prefix])
            .exists()
        )

    def __contains__(self, other):
        """
        Usage:
        "prefix" in table
        """
        return self.match(other)

    @classmethod
    def iter_match_prefix(
        cls, prefixes: Union[str, List[str]]
    ) -> Iterable[Tuple["PrefixTable", str]]:
        if isinstance(prefixes, str):
            prefixes = [prefixes]
        pp = [IP.prefix(prefix) for prefix in prefixes]
        match_prefixes = PrefixTablePrefix.objects.filter(afi=pp[0].afi).extra(
            where=[" OR ".join(["%s <<= prefix"] * len(prefixes))], params=prefixes
        )
        for pt in match_prefixes:
            yield pt.table, "<"

    @classmethod
    def iter_lazy_labels(cls, prefixes: Union[str, List[str]]):
        for pt, condition in cls.iter_match_prefix(prefixes):
            yield f"noc::prefixfilter::{pt.name}::{condition}"


class PrefixTablePrefix(NOCModel):
    class Meta(object):
        verbose_name = _("Prefix")
        verbose_name_plural = _("Prefixes")
        app_label = "main"
        db_table = "main_prefixtableprefix"
        unique_together = [("table", "afi", "prefix")]
        ordering = ["table", "afi", "prefix"]

    table = models.ForeignKey(PrefixTable, verbose_name=_("Prefix Table"), on_delete=models.CASCADE)
    afi = models.CharField(
        _("Address Family"), max_length=1, choices=[("4", _("IPv4")), ("6", _("IPv6"))]
    )
    prefix = CIDRField(_("Prefix"))

    def __str__(self):
        return "%s %s" % (self.table.name, self.prefix)

    def save(self, *args, **kwargs):
        # Set AFI
        self.afi = IP.prefix(self.prefix).afi
        return super().save(*args, **kwargs)
