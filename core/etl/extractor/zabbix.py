# ----------------------------------------------------------------------
# Zabbix Extractors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import Iterable

# Third-party modules
from zabbix_utils import ZabbixAPI

# NOC modules
from noc.core.etl.extractor.base import BaseExtractor
from noc.core.etl.remotesystem.base import BaseRemoteSystem
from noc.core.etl.models.managedobjectprofile import ManagedObjectProfile
from noc.core.etl.models.typing import ETLMapping
from noc.core.etl.models.managedobject import ManagedObject
from noc.core.etl.models.authprofile import AuthProfile
from noc.core.etl.models.resourcegroup import ResourceGroup


class ObjectType(enum.IntEnum):
    TRIGGER = 0
    REGISTERED_HOST = 1
    REGISTERED_SERVICE = 2
    REGISTRATION = 3
    ITEM = 4
    LLD_RULE = 5
    SERVICE = 6


class ZabbixHostInterfaceType(enum.IntEnum):
    AGENT = 1
    SNMP = 2
    IPMI = 3
    JMX = 4


class ZabbixRemoteSystem(BaseRemoteSystem):
    """
    Configuration variables (Main -> Setup -> Remote System -> Environments)
    API_URL - URL zabbix web interface
    API_USER - username for ro access to device
    API_PASSWORD - password for user access
    GROUPS_FILTER - list groups for extract
    """


class ZabbixExtractor(BaseExtractor):
    def __init__(self, system):
        super().__init__(system)
        self.url = self.config.get("API_URL", None)
        self.token = self.config.get("API_TOKEN", None)
        self.groups_filter = self.config.get("GROUPS_FILTER", [])
        self.user = self.config.get("API_USER", None)
        self.passw = self.config.get("API_PASSWORD", None)
        self.scheme = self.config.get("DEFAULT_SCHEME", None) or "2"
        self.pool = self.config.get("DEFAULT_POOL", None) or "default"
        self.api = ZabbixAPI(url=self.url, token=self.token, validate_certs=False)


@ZabbixRemoteSystem.extractor
class ZBAuthProfileExtractor(BaseExtractor):
    """ """

    name = "authprofile"
    model = AuthProfile
    data = [
        AuthProfile(id="ZB.AUTO", name="ZB.AUTO", type="G", snmp_ro="public"),
    ]


@ZabbixRemoteSystem.extractor
class ZabbixManagedObjectProfileExtractor(BaseExtractor):
    name = "managedobjectprofile"
    model = ManagedObjectProfile

    data = [
        ManagedObjectProfile(id="zb.std.sw", name="zb.std.sw", level=25),
    ]


@ZabbixRemoteSystem.extractor
class ZabbixHostGroupExtractor(ZabbixExtractor):
    """
    Extract Device Roles from NetBox
    """

    name = "resourcegroup"
    model = ResourceGroup

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[ResourceGroup]:
        yield ResourceGroup(
            id="zabbix.group",
            name="Zabbix groups",
            technology="Object Group",
        )
        r = self.api.hostgroup.get()
        for group in r:
            yield ResourceGroup(
                id=str(group["groupid"]),
                name=group["name"],
                technology="Object Group",
                parent="zabbix.group",
            )
        self.api.logout()


@ZabbixRemoteSystem.extractor
class ZabbixHostExtractor(ZabbixExtractor):
    """
    Extract Device Roles from NetBox
    """

    name = "managedobject"
    model = ManagedObject

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[ManagedObject]:
        r = self.api.host.get(
            **{"selectHostGroups": "extend", "selectInterfaces": "extend", "selectTags": "extend"}
        )
        for host in r:
            host_id = host["hostid"]
            if host["status"] == 1 or not host["interfaces"]:
                # Unmonitored host
                continue
            h_interface = host["interfaces"][0]
            i_type = ZabbixHostInterfaceType(int(h_interface["type"]))
            if i_type != ZabbixHostInterfaceType.SNMP:
                # Agent host
                continue
            labels = [t["tag"] for t in host["tags"]]
            for hg in host["hostgroups"]:
                name = hg["name"].replace("\\", "_")
                labels.append(f"zabbix::hg::{name}")
            if "mal" in labels:
                labels.remove("mal")
            # address = [i["ip"] for i in host["interfaces"] if i["type"] == "2"]
            if not h_interface["ip"]:
                continue
            yield ManagedObject(
                id=host_id,
                name=host["name"],
                profile="Generic.Host",
                pool=self.pool,
                segment=ETLMapping(value="ALL", scope="segment"),
                administrative_domain=ETLMapping(value="default", scope="adm_domain"),
                descriptrion=host["description"],
                object_profile="zb.std.sw",
                static_service_groups=[hg["groupid"] for hg in host["hostgroups"]],
                static_client_groups=[],
                scheme=self.scheme,
                address=h_interface["ip"],
                labels=labels,
                auth_profile="ZB.AUTO",
            )
        self.api.logout()
