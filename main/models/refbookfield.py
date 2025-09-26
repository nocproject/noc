# ---------------------------------------------------------------------
# RefBookField
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from .refbook import RefBook


class RefBookField(NOCModel):
    """
    Refbook fields
    """

    class Meta(object):
        app_label = "main"
        verbose_name = "Ref Book Field"
        verbose_name_plural = "Ref Book Fields"
        unique_together = [("ref_book", "order"), ("ref_book", "name")]
        ordering = ["ref_book", "order"]

    ref_book = models.ForeignKey(RefBook, verbose_name="Ref Book", on_delete=models.CASCADE)
    name = models.CharField("Name", max_length="64")
    order = models.IntegerField("Order")
    is_required = models.BooleanField("Is Required", default=True)
    description = models.TextField("Description", blank=True, null=True)
    search_method = models.CharField(
        "Search Method",
        max_length=64,
        blank=True,
        null=True,
        choices=[
            ("string", "string"),
            ("substring", "substring"),
            ("starting", "starting"),
            ("mac_3_octets_upper", "3 Octets of the MAC"),
        ],
    )

    rx_mac_3_octets = re.compile("^([0-9A-F]{6}|[0-9A-F]{12})$", re.IGNORECASE)

    def __str__(self):
        return "%s: %s" % (self.ref_book, self.name)

    # Return **kwargs for extra
    def get_extra(self, search):
        if self.search_method:
            return getattr(self, "search_%s" % self.search_method)(search)
        return {}

    def search_string(self, search):
        """
        string search method
        """
        return {"where": ["value[%d] ILIKE %%s" % self.order], "params": [search]}

    def search_substring(self, search):
        """
        substring search method
        """
        return {"where": ["value[%d] ILIKE %%s" % self.order], "params": ["%" + search + "%"]}

    def search_starting(self, search):
        """
        starting search method
        """
        return {"where": ["value[%d] ILIKE %%s" % self.order], "params": [search + "%"]}

    def search_mac_3_octets_upper(self, search):
        """
        Match 3 first octets of the MAC address
        """
        mac = search.replace(":", "").replace("-", "").replace(".", "")
        if not self.rx_mac_3_octets.match(mac):
            return {}
        return {"where": ["value[%d]=%%s" % self.order], "params": [mac]}
