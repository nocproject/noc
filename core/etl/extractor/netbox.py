# ----------------------------------------------------------------------
# Netbox Extractors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import bisect
from typing import Iterable, Optional, Union, Tuple, Any
from urllib.parse import urlparse

# Third-party modules
import orjson

# NOC modules
from noc.core.http.sync_client import HttpClient
from noc.core.etl.extractor.base import BaseExtractor, RemovedItem
from noc.core.etl.models.base import BaseModel
from noc.core.etl.remotesystem.base import BaseRemoteSystem
from noc.core.etl.models.object import Object, ObjectData
from noc.core.etl.models.managedobject import ManagedObject
from noc.core.etl.models.ipaddressprofile import IPAddressProfile
from noc.core.etl.models.ipprefixprofile import IPPrefixProfile
from noc.core.etl.models.ipprefix import IPPrefix
from noc.core.etl.models.ipaddress import IPAddress
from noc.core.etl.models.resourcegroup import ResourceGroup
from noc.core.etl.models.typing import ETLMapping, CapsItem
from noc.inv.models.objectmodel import ObjectModel


class NetBoxRemoteSystem(BaseRemoteSystem):
    """
    Базовый класс для Выгрузки.
    Для порядка описываем доступные для использования переменные, доступные в RemoteSystem Environment


    Configuration variables (Main -> Setup -> Remote System -> Environments)
    API_URL - URL zabbix web interface
    API_USER - username for ro access to device
    API_PASSWORD - password for user access
    GROUPS_FILTER - list groups for extract
    """


class NetBoxExtractor(BaseExtractor):
    resource_state_map = {
        "reserved": "Reserved",
        "active": "Approved",
        "dhcp": "Approved",
        "deprecated": "Cooldown",
        "container": "Reserved",
    }

    LIMIT = 300

    def __init__(self, system):
        super().__init__(system)
        self.url = self.config.get("API_URL", None)
        self.token = self.config.get("API_TOKEN", None)
        self.client = HttpClient(
            headers={
                "Content-Type": b"application/json",
                "Authorization": f"Token {self.token}".encode(),
            }
        )

    def iter_records(self, path: str):
        url = f"{self.url}{path}?limit={self.LIMIT}"
        while True:
            status, headers, content = self.client.get(url)
            body = orjson.loads(content)
            if status != 200:
                print(f"[{status}] Error when requested data: {body}")
                raise Exception(body)
            for r in body["results"]:
                yield r
            if not body["next"]:
                break
            p = urlparse(body["next"])
            url = f"{self.url}{p.path}?{p.query}"


@NetBoxRemoteSystem.extractor
class NetBoxObjectExtractor(NetBoxExtractor):
    """
    Extract Object Structure from NetBox
    Region -> PoP | Region
    Site -> PoP | Access
    Location -> Group
    Rack -> Rack

    Devices -> Generic Model (bu Unit)
    ? Insert Rack
    ? Contact
    ? label (tags)
    ? custom fields
    """

    name = "object"  # Имя загрузчика, для которого написано извлеченине данных
    model = Object

    rack_model_mapping = {
        18: 'NoName | Rack | 19" 18U Wall-Mount Cabinet',
        14: 'NoName | Rack | 19" 18U Wall-Mount Cabinet',
        15: 'NoName | Rack | 19" 18U Wall-Mount Cabinet',
        24: 'NoName | Rack | 19" 24U 1000mm Shelf',
        42: 'NoName | Rack | 19" 42U 1000mm Shelf',
        44: 'NoName | Rack | 19" 44U 1000mm Shelf',
        47: 'NoName | Rack | 19" 48U 1000mm Shelf',
        48: 'NoName | Rack | 19" 48U 1000mm Shelf',
        49: 'NoName | Rack | 19" 48U 1000mm Shelf',
    }

    device_mode_mapping = {"Generic | Access | Switch"}

    def __init__(self, system):
        super().__init__(system)
        self.racks = set()
        self.object_model_map = self.load_model_map()

    def get_model(self) -> str:
        return "Generic | Access | Switch"

    @staticmethod
    def load_model_map():
        r = {}
        for om in ObjectModel.objects.filter():
            part_no = om.get_data("asset", "part_no")
            if not part_no:
                continue
            for pn in part_no:
                r[pn] = om.name
        return r

    def iter_region(self):
        """
        Iterate over Region
        """
        for r in self.iter_records("/api/dcim/regions/?brief=1"):
            yield Object(
                id=str(r["id"]),
                name=r["name"],
                model="PoP | Regional",
                parent=r.get("parent"),
            )

    def iter_site(self):
        for r in self.iter_records("/api/dcim/sites/"):
            container, data = None, []
            # lat, lon = r.get("latitude"), r.get("longitude")
            location = r.get("physical_address")
            if location:
                data += [
                    ObjectData(
                        interface="address",
                        attr="text",
                        value=location,
                    ),
                    ObjectData(
                        interface="address",
                        attr="id",
                        value=str(hash(location)),
                    ),
                ]
            if r.get("region"):
                container = str(r["region"]["id"])
            yield Object(
                id=f"SITE-{r['id']}",
                name=r["name"],
                model="PoP | Access",
                parent=container,
                data=data,
            )

    def iter_location(self):
        for r in self.iter_records("/api/dcim/locations/"):
            container = None
            data = []
            if r.get("parent"):
                container = f"LOC-{r['parent']['id']}"
            elif r.get("site"):
                container = f"SITE-{r['site']['id']}"
            elif r.get("region"):
                container = f"{r['region']['id']}"
            yield Object(
                id=f"LOC-{r['id']}",
                name=r["name"],
                model="Group",
                parent=container,
                data=data,
            )

    def iter_rack(self):
        r_map = sorted(self.rack_model_mapping)
        for r in self.iter_records("/api/dcim/racks/"):
            h_rack = bisect.bisect_right(r_map, r["u_height"])
            if len(r_map) == h_rack:
                self.logger.warning("Rack with height: %s not in Models", r["u_height"])
                h_rack = 8
            data = []
            if r.get("site"):
                container = f"SITE-{r['site']['id']}"
            elif r.get("region"):
                container = f"{r['region']['id']}"
            else:
                container = None
            self.racks.add(f"RACK-{r['id']}")
            yield Object(
                id=f"RACK-{r['id']}",
                name=r["name"],
                model=self.rack_model_mapping[r_map[h_rack]],
                parent=container,
                data=data,
            )

    def iter_devices(self):
        for r in self.iter_records("/api/dcim/devices/"):
            if r.get("rack"):
                container = f"RACK-{r['rack']['id']}"
            else:
                container = f"SITE-{r['site']['id']}"
            if container not in self.racks:
                container = None
            data = []
            labels = []
            if r.get("role"):
                labels.append(f"netbox::role::{r['role']['slug']}")
            if r["serial"]:
                data.append(
                    ObjectData(
                        interface="asset",
                        attr="serial",
                        value=r["serial"],
                        scope="netbox",
                    )
                )
            if r["position"]:
                data += [
                    ObjectData(
                        interface="rackmount",
                        attr="position",
                        value=int(r["position"]),
                    ),
                    ObjectData(
                        interface="rackmount",
                        attr="side",
                        value=r["face"]["value"][0],
                    ),
                ]
            yield Object(
                id=f"DEVICE-{r['id']}",
                name=r["name"] or r["display"],
                model=self.get_model(),
                container=container,
                data=data,
            )

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[Object]:
        yield from self.iter_region()
        yield from self.iter_site()
        yield from self.iter_location()
        yield from self.iter_rack()
        # yield from self.iter_devices()


@NetBoxRemoteSystem.extractor
class NetBoxDeviceRolesExtractor(NetBoxExtractor):
    """
    Extract Device Roles from NetBox
    """

    name = "resourcegroup"
    model = ResourceGroup

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[ResourceGroup]:
        yield ResourceGroup(
            id="netbox.roles",
            name="Netbox Device Roles",
            technology="Object Group",
        )
        for r in self.iter_records("/api/dcim/device-roles/"):
            if r["device_count"] == 0:
                continue
            yield ResourceGroup(
                id=str(r["id"]),
                name=r["name"],
                technology="Object Group",
                parent="netbox.roles",
            )


@NetBoxRemoteSystem.extractor
class NetBoxIPPrefixProfileExtractor(NetBoxExtractor):
    """
    Extract IPAM IP Prefix Structure from NetBox
    """

    name = "ipprefixprofile"
    model = IPPrefixProfile

    data = [IPPrefixProfile(id="netbox.default", name="netbox.default")]


@NetBoxRemoteSystem.extractor
class NetBoxIPAddressProfileExtractor(NetBoxExtractor):
    """
    Extract IPAM IP Prefix Structure from NetBox
    """

    name = "ipaddressprofile"
    model = IPAddressProfile
    data = [IPAddressProfile(id="netbox.default", name="netbox.default")]


@NetBoxRemoteSystem.extractor
class NetBoxIPPrefixExtractor(NetBoxExtractor):
    """
    Extract IPAM IP Prefix Structure from NetBox
    """

    name = "ipprefix"
    model = IPPrefix

    def iter_data(
        self, *, checkpoint: Optional[str] = None, **kwargs
    ) -> Iterable[Union[BaseModel, RemovedItem, Tuple[Any, ...]]]:
        duplicate = set()
        roles = set()
        for r in self.iter_records("/api/ipam/prefixes/"):
            if r["prefix"] in duplicate:
                self.logger.warning("Duplicated prefix: %s", r["prefix"])
                continue
            if r["role"]:
                roles.add((r["role"]["id"], r["role"]["name"]))
            labels = [f"netbox::{x['name']}" for x in r["tags"]]
            if r["role"]:
                labels.append(f"netbox::role::{r['role']['name'].lower()}")
            yield IPPrefix(
                id=str(r["id"]),
                name=r["display"],
                prefix=r["prefix"],
                profile="netbox.default",
                description=r["description"],
                labels=labels,
                state=self.resource_state_map[r["status"]["value"]],
                state_changed=datetime.datetime.fromisoformat(r["last_updated"]),
            )
            duplicate.add(r["prefix"])
        print(roles)


@NetBoxRemoteSystem.extractor
class NetBoxIPAddressExtractor(NetBoxExtractor):
    """
    Extract IPAM IP Address from NetBox
    """

    name = "ipaddress"
    model = IPAddress

    def iter_data(
        self, *, checkpoint: Optional[str] = None, **kwargs
    ) -> Iterable[Union[BaseModel, RemovedItem, Tuple[Any, ...]]]:
        duplicate = set()
        for r in self.iter_records("/api/ipam/ip-addresses/"):
            address = r["address"].split("/")[0]
            if address in duplicate:
                self.logger.warning("Duplicated address: %s", address)
                continue
            fqdn = r.get("dns_name") or None
            name = r["display"]
            if fqdn and "." not in fqdn:
                name, fqdn = fqdn, None
            yield IPAddress(
                id=str(r["id"]),
                name=name,
                address=address,
                profile="netbox.default",
                description=r["description"],
                labels=[f"netbox::{x['name']}" for x in r["tags"]],
                fqdn=fqdn,
                state=self.resource_state_map[r["status"]["value"]],
                state_changed=datetime.datetime.fromisoformat(r["last_updated"]),
            )
            duplicate.add(address)


@NetBoxRemoteSystem.extractor
class NetBoxHostExtractor(NetBoxExtractor):
    """
    Extract Device Roles from NetBox
    """

    name = "managedobject"
    model = ManagedObject

    def __init__(self, system):
        super().__init__(system)
        self.pool: str = self.config.get("POOL") or "default"
        self.fm_pool: str = self.config.get("FM_POOL")

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[ManagedObject]:
        for r in self.iter_records("/api/dcim/devices/"):
            if r.get("rack"):
                container = f"RACK-{r['rack']['id']}"
            else:
                container = f"SITE-{r['site']['id']}"
            caps, groups, labels = [], [], []
            if r.get("role"):
                labels.append(f"netbox::role::{r['role']['slug']}")
                groups.append(str(r["role"]["id"]))
            host_id = f"DEVICE-{r['id']}"
            if not r.get("primary_ip"):
                continue
            if r["serial"]:
                caps.append(CapsItem(name="Asset | Serial Numbers", value=[r["serial"].strip()]))
            # if container in ["RACK-243", "RACK-325", "RACK-555"]:
            #    container = None
            yield ManagedObject(
                id=host_id,
                name=r["name"] or r["display"],
                profile="Generic.Host",
                pool=self.pool,
                fm_pool=self.fm_pool,
                container=container,
                segment=ETLMapping(value="ALL", scope="segment"),
                administrative_domain=ETLMapping(value="default", scope="adm_domain"),
                object_profile=ETLMapping(value="default", scope="objectprofile"),
                static_service_groups=groups,
                scheme="2",
                address=r["primary_ip"]["address"].split("/")[0],
                labels=labels,
                capabilities=caps,
            )
