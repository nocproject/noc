# ----------------------------------------------------------------------
# AdministrativeDomain REST API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.main.models.label import Label
from ..models.administrativedomain import (
    DefaultAdministrativeDomainItem,
    FormAdministrativeDomainItem,
)
from ..utils.ref import get_reference, get_reference_label
from ..utils.rest.model import ModelResourceAPI
from ..utils.rest.op import FilterExact, RefFilter, FuncFilter, FilterIn

router = APIRouter()


class AdministrativeDomainAPI(ModelResourceAPI[AdministrativeDomain]):
    prefix = "/api/ui/administrativedomain"
    model = AdministrativeDomain
    list_ops = [
        FilterIn("id"),
        FuncFilter("query", function=lambda qs, values: qs.filter(name__icontains=values[0])),
        FilterExact("name"),
        RefFilter("parent", model=AdministrativeDomain),
    ]
    sort_fields = ["name", "id", ("parent", "parent__name")]

    @classmethod
    def item_to_default(cls, item: AdministrativeDomain) -> DefaultAdministrativeDomainItem:
        return DefaultAdministrativeDomainItem(
            id=str(item.id),
            name=str(item.name),
            parent=get_reference(item.parent),
            default_pool=get_reference(item.default_pool),
            bioseg_floating_name_template=get_reference(item.bioseg_floating_name_template),
            bioseg_floating_parent_segment=get_reference(item.bioseg_floating_parent_segment),
            labels=[get_reference_label(ii) for ii in Label.objects.filter(name__in=item.labels)],
            effective_labels=[
                get_reference_label(ii)
                for ii in Label.objects.filter(name__in=item.effective_labels)
            ],
            remote_system=get_reference(item.remote_system),
            remote_id=item.remote_id,
            bi_id=str(item.bi_id),
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


# Install endpoints
AdministrativeDomainAPI(router)
