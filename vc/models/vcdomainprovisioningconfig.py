# ---------------------------------------------------------------------
# VCDomainProvisioningConfig
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.fields import DocumentReferenceField
from noc.main.models.notificationgroup import NotificationGroup
from noc.inv.models.resourcegroup import ResourceGroup
from noc.core.comp import smart_text
from .vcdomain import VCDomain
from .vcfilter import VCFilter


class VCDomainProvisioningConfig(NOCModel):
    """
    VCDomain Provisioning Parameters
    """

    class Meta(object):
        verbose_name = "VC Domain Provisioning Config"
        verbose_name_plural = "VC Domain Provisioning Config"
        db_table = "vc_vcdomainprovisioningconfig"
        app_label = "vc"
        unique_together = [("vc_domain", "resource_group")]

    vc_domain = models.ForeignKey(VCDomain, verbose_name="VC Domain", on_delete=models.CASCADE)
    resource_group = DocumentReferenceField(ResourceGroup)
    is_enabled = models.BooleanField("Is Enabled", default=True)
    vc_filter = models.ForeignKey(
        VCFilter, verbose_name="VC Filter", null=True, blank=True, on_delete=models.CASCADE
    )
    tagged_ports = models.CharField("Tagged Ports", max_length=256, null=True, blank=True)
    notification_group = models.ForeignKey(
        NotificationGroup,
        verbose_name="Notification Group",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{smart_text(self.vc_domain)}: {smart_text(self.resource_group)}"

    @property
    def tagged_ports_list(self):
        """
        Returns a list of tagged ports
        """
        if self.tagged_ports:
            return [x.strip() for x in self.tagged_ports.split(",")]
        else:
            return []
