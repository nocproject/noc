# ----------------------------------------------------------------------
# path API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from time import perf_counter
from typing import Tuple, Optional, Dict, List, Iterable, DefaultDict, Any, Union

# Third-party modules
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field, conint

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.sa.models.service import Service
from noc.core.span import Span
from noc.core.topology.path import KSPFinder
from noc.core.topology.constraint.base import BaseConstraint
from noc.core.topology.constraint.vlan import VLANConstraint
from noc.core.topology.constraint.upwards import UpwardsConstraint
from noc.core.topology.constraint.any import AnyConstraint
from noc.core.topology.goal.base import BaseGoal
from noc.core.topology.goal.managedobject import ManagedObjectGoal
from noc.core.topology.goal.level import ManagedObjectLevelGoal
from noc.core.text import alnum_key
from ..base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE

# Constants
MAX_DEPTH_DEFAULT = 20
N_SHORTEST_DEFAULT = 10

router = APIRouter()


# id/remote system pointer
class PointerId(BaseModel):
    id: str


class PointerRemote(BaseModel):
    remote_system: str
    remote_id: str


class InterfaceModel(BaseModel):
    name: str


# from: section
class ObjectPointer(BaseModel):
    object: Union[PointerId, PointerRemote]
    interface: Optional[InterfaceModel]


class InterfaceModel_(BaseModel):
    id: str  # ObjectIdParameter


class InterfacePointer(BaseModel):
    interface: InterfaceModel_


class LevelPointer(BaseModel):
    level: int


class ServiceOrderPointer(BaseModel):
    order_id: int
    remote_system: Optional[str]


class ServicePointer(BaseModel):
    service: Union[PointerId, PointerRemote, ServiceOrderPointer]


RequestFrom = Union[ObjectPointer, InterfacePointer, ServicePointer]

# to: section
RequestTo = Union[ObjectPointer, LevelPointer, InterfacePointer, ServicePointer]


# config: section
class RequestConfig(BaseModel):
    max_depth: int = MAX_DEPTH_DEFAULT
    n_shortest: int = N_SHORTEST_DEFAULT


# constraints: section
class RequestVLANConstraint(BaseModel):
    vlan: Optional[conint(ge=1, le=4095)] = None
    interface_untagged: Optional[bool] = None
    strict: bool = False


class RequestConstraints(BaseModel):
    vlan: Optional[RequestVLANConstraint] = None
    upwards: bool = False


class PathRequest(BaseModel):
    from_: RequestFrom = Field(..., alias="from")
    to: RequestTo
    config: Optional[RequestConfig] = None
    constraints: Optional[RequestConstraints] = None


class PathAPI(NBIAPI):
    api_name = "path"
    openapi_tags = ["path API"]

    def get_routes(self):
        route = {
            "path": "/api/nbi/path",
            "method": "POST",
            "endpoint": self.handler,
            "response_model": None,
            "name": "path",
            "description": "Trace k-shortest paths over network topology considering constraints.",
        }
        return [route]

    async def handler(
        self, req: PathRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)
    ):
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        # Find start of path
        try:
            with Span(in_label="start_of_path"):
                start, start_iface = self.get_object_and_interface(**dict(req.from_))
        except ValueError as e:
            raise HTTPException(
                404, {"status": False, "error": "Failed to find start of path: %s" % e}
            )
        # Find end of path
        if hasattr(req.to, "level"):
            goal = ManagedObjectLevelGoal(req.to.level)
            end_iface = None
        else:
            try:
                with Span(in_label="end_of_path"):
                    end, end_iface = self.get_object_and_interface(**dict(req.to))
                goal = ManagedObjectGoal(end)
            except ValueError as e:
                raise HTTPException(
                    404, {"status": False, "error": "Failed to find end of path: %s" % e}
                )
        # Trace the path
        if hasattr(req, "config"):
            max_depth = req.config.max_depth
            n_shortest = req.config.n_shortest
        else:
            max_depth = MAX_DEPTH_DEFAULT
            n_shortest = N_SHORTEST_DEFAULT
        error = None
        with Span(in_label="find_path"):
            t0 = perf_counter()
            try:
                paths = list(
                    self.iter_paths(
                        start,
                        start_iface,
                        goal,
                        end_iface,
                        constraints=self.get_constraints(
                            start, start_iface, getattr(req, "constraints", None)
                        ),
                        max_depth=max_depth,
                        n_shortest=n_shortest,
                    )
                )
            except ValueError as e:
                error = str(e)
            dt = perf_counter() - t0
        if error:
            raise HTTPException(404, {"status": False, "error": error, "time": dt})
        return {"status": True, "paths": paths, "time": dt}

    def get_object_and_interface(
        self,
        object: Optional[Union[PointerId, PointerRemote]] = None,
        interface: Optional[Union[InterfaceModel, InterfaceModel_]] = None,
        service: Optional[Union[PointerId, PointerRemote, ServiceOrderPointer]] = None,
    ) -> Tuple[ManagedObject, Optional[Interface]]:
        """
        Process from and to section of request and get object and interface

        :param object: request.object
        :param interface: request.interface
        :param service: request.service

        :return: ManagedObject Instance, Optional[Interface Instance]
        :raises ValueError:
        """
        if object:
            if hasattr(object, "id"):
                # object.id
                mo = ManagedObject.get_by_id(object.id)
            elif hasattr(object, "remote_system"):
                # object.remote_system/remote_id
                rs = RemoteSystem.get_by_id(object.remote_system)
                if not rs:
                    raise ValueError("Remote System not found")
                mo = ManagedObject.objects.filter(
                    remote_system=rs.id, remote_id=object.remote_id
                ).first()
            else:
                raise ValueError("Neither id or remote system specified")
            if not mo:
                raise ValueError("Object not found")
            if interface:
                # Additional interface restriction
                iface = mo.get_interface(interface.name)
                if iface is None:
                    raise ValueError("Interface not found")
                return mo, iface
            # No interface restriction
            return mo, None
        if interface:
            iface = Interface.objects.filter(id=interface.id).first()
            if not iface:
                raise ValueError("Interface not found")
            return iface.managed_object, iface
        if service:
            if hasattr(service, "id"):
                svc = Service.objects.filter(id=service.id).first()
            elif hasattr(service, "order_id") and hasattr(service, "remote_system"):
                svc = Service.objects.filter(
                    order_id=service.order_id, remote_system=service.remote_system
                ).first()
            elif hasattr(service, "order_id"):
                svc = Service.objects.filter(order_id=service.order_id).first()
            elif hasattr(service, "remote_system"):
                rs = RemoteSystem.get_by_id(service.remote_system)
                if not rs:
                    raise ValueError("Remote System not found")
                svc = Service.objects.filter(
                    remote_system=rs.id, remote_id=service.remote_id
                ).first()
            else:
                raise ValueError("Neither id or remote system specified")
            if svc is None:
                raise ValueError("Service not found")
            iface = Interface.objects.filter(service=svc.id).first()
            if not iface:
                raise ValueError("Interface not found")
            return iface.managed_object, iface
        raise ValueError("Invalid search condition")

    def iter_paths(
        self,
        start: ManagedObject,
        start_iface: Optional[Interface],
        goal: BaseGoal,
        end_iface: Optional[Interface],
        constraints: Optional[BaseConstraint] = None,
        max_depth: int = MAX_DEPTH_DEFAULT,
        n_shortest: int = N_SHORTEST_DEFAULT,
    ) -> Iterable[Dict]:
        """
        Iterate possible paths

        :param start: Starting Managed Object
        :param start_iface: Starting interface or None
        :param goal: BaseGoal instance to match end of path
        :param end_iface: Ending interface or None
        :param constraints: Path constraints
        :param max_depth: Max search depth
        :param n_shortest: Restrict to `n_shortest` shortest paths
        :return:
        """

        def encode_link(interfaces: List[Interface]) -> Dict:
            objects: DefaultDict[ManagedObject, List] = defaultdict(list)
            for iface in interfaces:
                objects[iface.managed_object] += [iface.name]
            # Order objects
            order: List[ManagedObject] = list(objects)
            try:
                idx = order.index(last["obj"])
                o = order.pop(idx)
                order.insert(0, o)
                last["obj"] = order[-1]
            except ValueError:
                pass
            return {
                "objects": [
                    {
                        "object": {
                            "id": obj.id,
                            "name": obj.name,
                            "address": obj.address,
                            "bi_id": obj.bi_id,
                        },
                        "interfaces": sorted(objects[obj], key=alnum_key),
                    }
                    for obj in order
                ]
            }

        finder = KSPFinder(
            start, goal, constraint=constraints, max_depth=max_depth, n_shortest=n_shortest
        )
        for path in finder.iter_shortest_paths():  # type: List[PathInfo]
            last: Dict[str, ManagedObject] = {"obj": start}
            r: Dict[str, Any] = {"path": [], "cost": {"l2": 0}}
            if start_iface:
                r["path"] += [{"links": [encode_link([start_iface])]}]
            for pi in path:  # type: PathInfo
                r["path"] += [{"links": [encode_link(link.interfaces) for link in pi.links]}]
                r["cost"]["l2"] += pi.l2_cost
            if end_iface:
                r["path"] += [{"links": [encode_link([end_iface])]}]
            yield r

    def get_constraints(
        self,
        start: ManagedObject,
        start_iface: Optional[Interface],
        constraints: RequestConstraints,
    ) -> Optional[BaseConstraint]:
        """
        Calculate path constraints
        :param start: Start of path
        :param start_iface: Starting interface
        :param constraints: request.constraints section
        :return: BaseConstraint index
        """
        if not constraints:
            return None
        constraint = AnyConstraint()
        if getattr(constraints, "upwards"):
            constraint &= UpwardsConstraint()
        if hasattr(constraints, "vlan"):
            vconst = constraints.vlan
            if hasattr(vconst, "vlan"):
                constraint &= VLANConstraint(vconst.vlan, strict=vconst.strict)
            elif getattr(vconst, "interface_untagged", None):
                if start_iface is None:
                    raise ValueError("No starting interface")
                constraint &= self.get_interface_untagged_constraint(
                    start_iface, strict=vconst.strict
                )
        return None

    def get_interface_untagged_constraint(
        self, iface: Interface, strict: bool = False
    ) -> BaseConstraint:
        for doc in SubInterface._get_collection().find(
            {"interface": iface.id},
            {"_id": 0, "enabled_afi": 1, "untagged_vlan": 1, "tagged_vlans": 1},
        ):
            if "BRIDGE" not in doc["enabled_afi"]:
                continue
            if doc.get("untagged_vlan"):
                return VLANConstraint(doc["untagged_vlan"], strict=strict)
        raise ValueError("Cannot get untagged vlan from interface")


# Install router
PathAPI(router)
