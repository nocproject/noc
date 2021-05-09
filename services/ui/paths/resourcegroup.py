# ----------------------------------------------------------------------
# ResourceGroup REST API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.inv.models.resourcegroup import ResourceGroup
from ..models.resourcegroup import DefaultResourceGroupItem, FormResourceGroupItem
from ..utils.ref import get_reference, get_reference_label
from ..utils.rest.document import DocumentResourceAPI
from ..utils.rest.op import FilterExact, RefFilter

router = APIRouter()


class ResourceGroupAPI(DocumentResourceAPI[ResourceGroup]):
    prefix = "/api/ui/resourcegroup"
    model = ResourceGroup
    list_ops = [FilterExact("id"), RefFilter("parent", model=ResourceGroup)]

    @classmethod
    def item_to_default(cls, item: ResourceGroup) -> DefaultResourceGroupItem:
        return DefaultResourceGroupItem(
            id=str(item.id),
            name=str(item.name),
            technology=get_reference(item.technology),
            parent=get_reference(item.parent),
            description=item.description,
            dynamic_service_labels=[get_reference_label(ll) for ll in item.dynamic_client_labels],
            dynamic_client_labels=[get_reference_label(ll) for ll in item.dynamic_client_labels],
            remote_system=get_reference(item.remote_system),
            remote_id=item.remote_id,
            bi_id=str(item.bi_id),
            labels=[get_reference_label(ll) for ll in item.labels],
            effective_labels=[get_reference_label(ll) for ll in item.effective_labels],
        )

    @classmethod
    def item_to_form(cls, item: ResourceGroup) -> FormResourceGroupItem:
        return FormResourceGroupItem(
            name=str(item.name),
            technology=get_reference(item.technology),
            parent=get_reference(item.parent),
            description=item.description,
            dynamic_service_labels=item.dynamic_client_labels,
            dynamic_client_labels=item.dynamic_client_labels,
            labels=item.labels,
        )


# Install endpoints
ResourceGroupAPI(router)
