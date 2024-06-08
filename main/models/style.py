# ---------------------------------------------------------------------
# Style model model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional
import operator

# Third-party modules
from django.db import models
import cachetools

# NOC models
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(
    check=[
        ("inv.InterfaceProfile", "style"),
        ("sa.ManagedObjectProfile", "style"),
        ("crm.SubscriberProfile", "style"),
        ("crm.SupplierProfile", "style"),
        ("sla.SLAProfile", "style"),
        ("inv.CPEProfile", "style"),
        ("inv.NetworkSegmentProfile", "style"),
        ("inv.SensorProfile", "style"),
        ("ip.AddressProfile", "style"),
        ("ip.PrefixProfile", "style"),
        ("vc.VPNProfile", "style"),
        ("fm.AlarmSeverity", "style"),
        ("peer.ASProfile", "style"),
        ("phone.PhoneNumberProfile", "style"),
        ("phone.PhoneRangeProfile", "style"),
        ("fm.ActiveAlarm", "custom_style"),
        ("vc.VLANProfile", "style"),
        ("vc.L2DomainProfile", "style"),
    ]
)
class Style(NOCModel):
    """
    CSS Style
    """

    class Meta(object):
        verbose_name = "Style"
        verbose_name_plural = "Styles"
        ordering = ["name"]
        app_label = "main"
        db_table = "main_style"

    name = models.CharField("Name", max_length=64, unique=True)
    font_color = models.IntegerField("Font Color", default=0)
    background_color = models.IntegerField("Background Color", default=0xFFFFFF)
    bold = models.BooleanField("Bold", default=False)
    italic = models.BooleanField("Italic", default=False)
    underlined = models.BooleanField("Underlined", default=False)
    is_active = models.BooleanField("Is Active", default=True)
    description = models.TextField("Description", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["Style"]:
        try:
            return Style.objects.get(id=id)
        except Style.DoesNotExist:
            return None

    @property
    def css_class_name(self):
        """
        CSS Class Name
        """
        return "noc-color-%d" % self.id

    @property
    def style(self):
        """
        CSS Style
        """
        s = "color: #%06X !important; background-color: #%06X !important;" % (
            self.font_color,
            self.background_color,
        )
        if self.bold:
            s += " font-weight: bold !important;"
        if self.italic:
            s += " font-style: italic !important;"
        if self.underlined:
            s += " text-decoration: underline !important;"
        return s

    @property
    def css(self):
        """
        CSS class style
        """
        return ".%s, .%s td { %s }\n" % (self.css_class_name, self.css_class_name, self.style)
