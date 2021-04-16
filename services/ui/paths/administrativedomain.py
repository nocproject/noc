# ----------------------------------------------------------------------
# AdministrativeDomain REST API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.models.administrativedomain import AdministrativeDomain
from ..models.administrativedomain import (
    DefaultAdministrativeDomainItem,
    FormAdministrativeDomainItem,
)
from ..utils.ref import get_reference
from ..utils.rest.model import ModelResourceAPI


class AdministrativeDomainAPI(ModelResourceAPI[AdministrativeDomain]):
    prefix = "/api/ui/administrativedomain"
    model = AdministrativeDomain

    @classmethod
    def item_to_default(cls, item: AdministrativeDomain) -> DefaultAdministrativeDomainItem:
        return DefaultAdministrativeDomainItem(
            id=str(item.id),
            name=str(item.name),
            parent=get_reference(item.parent),
            default_pool=get_reference(item.default_pool),
            bioseg_floating_name_template=get_reference(item.bioseg_floating_name_template),
            bioseg_floating_parent_segment=get_reference(item.bioseg_floating_parent_segment),
            labels=item.labels,
            effective_labels=item.effective_labels,
            remote_system=get_reference(item.remote_system),
            remote_id=item.remote_id,
            bi_id=item.bi_id,
        )

    @classmethod
    def item_to_form(cls, item: AdministrativeDomain) -> FormAdministrativeDomainItem:
        return FormAdministrativeDomainItem(
            name=str(item.name),
            parent=get_reference(item.parent),
            default_pool=get_reference(item.default_pool),
            bioseg_floating_name_template=get_reference(item.bioseg_floating_name_template),
            bioseg_floating_parent_segment=get_reference(item.bioseg_floating_parent_segment),
            labels=item.labels,
        )


router = AdministrativeDomainAPI().router
