# ----------------------------------------------------------------------
# Job request
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict, Literal
import datetime

# Third party modules
from pydantic import BaseModel, Field
from bson import ObjectId

# NOC modules
from noc.core.service.pub import publish


class InputMapping(BaseModel):
    """
    Input variables mappings.

    Arguments:
        name: Name of the input parameter, action specific.
        value: Parameter value. Jinja2 template in where
            the environment is used as context.
            If `job` parameter is set, the job result is exposed
            as `result` context variable.
        job: Optional job name.
    """

    name: str
    value: str
    job: Optional[str] = None

    @property
    def is_kv(self) -> bool:
        """Check if input is key-value mappig."""
        return self.name.startswith("*")


def KVInputMapping(name: str, value: str) -> InputMapping:
    """
    Key-value input mapping.
    """
    return InputMapping(name=f"*{name}", value=value)


class JobRequest(BaseModel):
    """
    Pipeline job.

    Attributes:
        name: Job name, unique within job group
        action: Name of the action. Mutual exclusive with jobs.
        description: Optional description.
        labels: List of labels.
        allow_fail: If set to true, FAILED job became WARNING.
        locks: Optional list of lock names. Lock names are jinja2
            template variables, in where environment is used as content.
        inputs: List of input mappigs.
        require_approval: Job will be created in PENDING status.
        depends_on: List of dependencies. Dependencies are
            the names of the jobs from the same group.
            Circular dependensies are not allowed.
        environment: Dict of evrironment variables and their
            values, available for same job and exposed to
            all children.
        after: Schedule job to start after the specified time.
        deadline: Job must be completed before deadline, or it
            became cancelled.
        resource_path: List representing path to resource.
        jobs: List of nested jobs. Mutual exclusive with actions.
    """

    op: Literal["submit"] = Field(None, alias="$op")
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    action: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    allow_fail: bool = False
    locks: Optional[List[str]] = None
    inputs: Optional[List[InputMapping]] = None
    require_approval: bool = False
    depends_on: Optional[List[str]] = None
    environment: Optional[Dict[str, str]] = None
    after: Optional[datetime.datetime] = None
    deadline: Optional[datetime.datetime] = None
    resource_path: Optional[List[str]] = None
    jobs: Optional[List["JobRequest"]] = None

    def submit(self) -> None:
        """Submit job request."""
        if not self.op:
            self.op = "submit"
        publish(self.model_dump_json().encode(), "submit", partition=0)
