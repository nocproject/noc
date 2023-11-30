# ----------------------------------------------------------------------
# Job request
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict
import datetime

# Third party modules
from pydantic import BaseModel


class InputMapping(BaseModel):
    """
    Input variables mappings.

    Arguments:
        name: Name of the input parameter, action specific.
        value: Parameter value. Jinja2 template in where
            the environment is used as context.
    """

    name: str
    value: str


class OutputMapping(BaseModel):
    """
    Output mappings.

    Argumens:
        name: Evironment variable name.
        value: Jinja2 template, in where output parameters
            are used as context.
    """

    name: str
    value: str


class JobRequest(BaseModel):
    """
    Pipeline job.

    Attributes:
        name: Jobb name, unique within job group
        action: Name of the action. Mutual exclusive with jobs.
        description: Optional descriptionn.
        labels: List of labels.
        allow_fail: If set to true, FAILED job became WARNING.
        locks: Optional list of lock names.
        inputs: List of input mappigs.
        outputs: List of output mappings.
        require_approval: Job will be created in PENDING status.
        depends_on: List of dependencies. Dependencies are
            the name of the jobs from the same group.
            Circular dependensies are not allowed.
        environment: Dict of evrironment variables and their
            values, available for same job and exposed to
            all children.
        after: Schedule job to start after the specified time.
        deadline: Job must be completed before deadline, or it
            became cancelled.
        jobs: List of nested jobs. Mutual exclusive with actions.
    """

    name: str
    action: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    allow_fail: bool = False
    locks: Optional[List[str]] = None
    inputs: Optional[List[InputMapping]] = None
    outputs: Optional[List[OutputMapping]] = None
    require_approval: bool = False
    depends_on: Optional[List[str]] = None
    environment: Optional[Dict[str, str]] = None
    after: Optional[datetime.datetime] = None
    deadline: Optional[datetime.datetime] = None
    jobs: Optional[List["JobRequest"]] = None
