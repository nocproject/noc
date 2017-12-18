# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VCFilter model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from threading import Lock
import operator
# Third-party modules
from django.db import models
import cachetools
import six
# NOC modules
from noc.core.model.decorator import on_delete_check

rx_vc_filter = re.compile(r"^\s*\d+\s*(-\d+\s*)?(,\s*\d+\s*(-\d+)?)*$")
id_lock = Lock()


@on_delete_check(check=[
    ("vc.VCBindFilter", "vc_filter"),
    ("vc.VCDomainProvisioningConfig", "vc_filter"),
])
class VCFilter(models.Model):
    """
    VC Filter
    """
    class Meta:
        verbose_name = "VC Filter"
        verbose_name_plural = "VC Filters"
        db_table = "vc_vcfilter"
        app_label = "vc"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    expression = models.CharField("Expression", max_length=256)
    description = models.TextField("Description", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        try:
            return VCFilter.objects.get(id=id)
        except VCFilter.DoesNotExist:
            return None

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Check expression before save
        """
        VCFilter.compile(self.expression)
        super(VCFilter, self).save(*args, **kwargs)

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
        if isinstance(name, six.string_types):
            name = "\"%s\"" % name.replace("\"", "\"\"")
        elif type(name) in (int, long):
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
