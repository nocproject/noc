# ---------------------------------------------------------------------
# Runner Job implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, List, Iterable, Optional, Set, Iterator, Type, DefaultDict, Union
from logging import getLogger
from weakref import ref, ReferenceType
import asyncio
from dataclasses import dataclass
from collections import defaultdict

# Third-party modules
from bson import ObjectId
from jinja2 import Template, TemplateSyntaxError

# NOC modules
from .models.jobreq import JobRequest
from noc.sa.models.job import JobStatus
from .actions.loader import loader
from .actions.base import BaseAction
from .env import Environment

logger = getLogger(__name__)


@dataclass
class Input(object):
    """
    Input mapping.

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


class Job(object):
    """
    Job runtime representation.

    Args:
        name: Job name
    """

    def __init__(
        self,
        name: str,
        status: JobStatus,
        action: Optional[Type[BaseAction]] = None,
        allow_fail: bool = False,
        parent: Optional["Job"] = None,
        environment: Optional[Dict[str, str]] = None,
        locks: Optional[Iterable[str]] = None,
        inputs: Optional[Iterable[Input]] = None,
    ) -> None:
        self.id = ObjectId()
        self.name = name
        self.action = action
        self.allow_fail = allow_fail
        self.status: JobStatus = status
        self.parent = parent
        self.environment = Environment(environment)
        if self.parent:
            self.environment.set_parent(self.parent.environment)
        self.inputs = list(inputs) if inputs else None
        self.locks = list(locks) if locks is not None else None
        self.depends_on: Optional[List[ReferenceType[Job]]] = None
        self.children: Optional[List[ReferenceType[Job]]] = None
        self._task: Optional[ReferenceType[asyncio.Task]] = None
        self.results: Dict[str, Union[None, str, object]] = {}

    def __str__(self) -> str:
        return f"{self.name}({self.id})"

    @property
    def has_children(self) -> bool:
        return bool(self.children)

    def iter_parents(self) -> Iterable["Job"]:
        """Iterate over parents all way up."""
        p = self.parent
        while p is not None:
            yield p
            p = p.parent

    def iter_children(self) -> Iterable["Job"]:
        """Iterate over direct children."""
        if self.children:
            for r in self.children:
                item = r()
                if item:
                    yield item

    def iter_siblings(self) -> Iterable["Job"]:
        """Iterate over siblings."""
        if self.parent:
            for item in self.parent.iter_children():
                if item != self:
                    yield item

    def iter_depends_on(self) -> Iterable["Job"]:
        """
        Iterate dependencies.
        """
        if self.depends_on:
            for d in self.depends_on:
                r = d()
                if r:
                    yield r

    def iter_group(self) -> Iterable["Job"]:
        """
        Iterate job and all direct and indirect children.
        """
        yield self
        for c in self.iter_children():
            yield from c.iter_group()

    def is_blocked_by_parents(self) -> bool:
        for p in self.iter_parents():
            if p.status not in (JobStatus.WAITING, JobStatus.RUNNING):
                return True
            if p.is_blocked_by_siblings():
                return True
        return False

    def is_blocked_by_siblings(self) -> bool:
        # Any failed sibling
        if any(True for s in self.iter_siblings() if s.is_complete_failed):
            return True
        # Check dependencies
        if self.depends_on and any(
            True for s in self.iter_depends_on() if not s.is_complete_success
        ):
            return True
        return False

    def is_blocked(self) -> bool:
        return not self.is_waiting or self.is_blocked_by_parents() or self.is_blocked_by_siblings()

    @property
    def leader(self) -> "Job":
        """
        Top-level job.
        """
        if self.is_leader:
            return self
        return list(self.iter_parents())[-1]

    @property
    def is_leader(self) -> bool:
        """
        Check if job is top-level job.

        Returns:
            True, if job has no parent
        """
        return not self.parent

    @property
    def is_waiting(self) -> bool:
        return self.status == JobStatus.WAITING

    @property
    def is_running(self) -> bool:
        return self.status == JobStatus.RUNNING

    @property
    def is_cancelled(self) -> bool:
        return self.status == JobStatus.CANCELLED

    @property
    def is_complete_success(self) -> bool:
        return self.status in (
            JobStatus.SUCCESS,
            JobStatus.WARNING,
        )

    @property
    def is_complete_failed(self) -> bool:
        return self.status in (
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        )

    @property
    def is_complete(self) -> bool:
        return self.status in (
            JobStatus.SUCCESS,
            JobStatus.WARNING,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        )

    @staticmethod
    def _get_initial_status(req: JobRequest) -> JobStatus:
        """
        Get status from request.
        """
        if req.require_approval:
            return JobStatus.PENDING
        return JobStatus.WAITING

    @staticmethod
    def _is_unique_names(jobs: Iterable[JobRequest]) -> bool:
        """
        Check if all names are unique.

        Args:
            jobs: Iterable of jobs.
        """
        seen: Set[str] = set()
        for job in jobs:
            if not job.name:
                return False  # Empty name
            if job.name in seen:
                return False
            seen.add(job.name)
        return True

    @staticmethod
    def _has_loops(graph: Dict[str, List[str]]) -> bool:
        """
        Check a graph has loops.

        Args:
            graph: A dict of name -> depends_on name

        Returns:
            True: if the graph has loops.
        """

        def dfs(node: str, visited: Dict[str, bool], path: Set[str]) -> bool:
            visited[node] = True
            path.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, visited, path):
                        return True
                elif neighbor in path:
                    return True

            path.remove(node)
            return False

        visited: Dict[str, bool] = {}
        for node in graph:
            if node not in visited:
                if dfs(node, visited, set()):
                    return True

        return False

    @classmethod
    def _validate_req(cls, req: JobRequest) -> None:
        """
        Validate request.

        Args:
            req: Request

        Raises:
            ValueError: when failed
        """
        # Validate actions/jobs
        if not req.action and not req.jobs:
            msg = "Either action or jobs must be set"
            raise ValueError(msg)
        if req.action and req.jobs:
            msg = "action and jobs cannot be used together"
            raise ValueError(msg)
        if req.action and req.action not in loader:
            msg = f"Invalid action {req.action}"
            raise ValueError(msg)
        if req.inputs and not req.action:
            msg = "action must be set"
            raise ValueError(msg)
        # Validate inputs
        if req.inputs:
            action: Type[BaseAction] = loader[req.action]
            seen_inputs: Set[str] = set()
            for i in req.inputs:
                if i.name not in action.inputs:
                    msg = f"Invalid input `{i.name}`"
                    raise ValueError(msg)
                if i.name in seen_inputs:
                    msg = f"Input `{i.name}` is defined twice"
                    raise ValueError(msg)
                seen_inputs.add(i.name)
                # @todo: Test name
                try:
                    Template(i.value)
                except TemplateSyntaxError as e:
                    msg = f"Invalid value for input {i.name}: '{i.value}' ({e})"
                    raise ValueError(msg) from e
            # Check all required inputs are set
            missed = set(k for k, v in action.inputs.items() if not v) - seen_inputs
            if missed:
                msg = f"Missed inputs: {', '.join(missed)}"
                raise ValueError(msg)
        # Validate locks
        if req.locks:
            for lock in req.locks:
                try:
                    Template(lock)
                except TemplateSyntaxError as e:
                    msg = f"Invalid lock template '{lock}': {e}"
                    raise ValueError(msg) from e
        if not req.jobs:
            return
        # Check for unique names
        if not cls._is_unique_names(req.jobs):
            msg = "Job names must be unique within the leader"
            raise ValueError(msg)
        # Check dependency refers to known name
        known_names = {j.name for j in req.jobs}
        for j in req.jobs:
            if j.depends_on:
                # Direct dependencies
                for dj in j.depends_on:
                    if dj not in known_names:
                        msg = f"Dependency refers to unknown job {dj}"
                        raise ValueError(msg)
            if j.inputs:
                # Input dependencies
                for i in j.inputs:
                    if i.job and i.job not in known_names:
                        msg = f"Dependency refers to unknown job {i.job}"
                        raise ValueError(msg)
        # Check for dependency cycles
        graph = {j.name: j.depends_on if j.depends_on else [] for j in req.jobs}
        if cls._has_loops(graph):
            msg = "Job graph cannot contain a cycle"
            raise ValueError(msg)
        # Validate nested jobs
        for j_req in req.jobs:
            cls._validate_req(j_req)

    @classmethod
    def from_req(cls, req: JobRequest, parent: Optional["Job"] = None) -> Iterator["Job"]:
        """
        Create jobs from request.
        """
        # Validate
        if not parent:
            # Check only from top level
            cls._validate_req(req)
        # Inputs
        if req.inputs:
            inputs = [Input(name=i.name, value=i.value, job=i.job) for i in req.inputs] or None
        else:
            inputs = None
        # Create job
        leader = Job(
            name=req.name,
            action=loader[req.action] if req.action else None,
            status=cls._get_initial_status(req),
            allow_fail=req.allow_fail,
            parent=parent,
            environment=req.environment,
            inputs=inputs,
            locks=req.locks,
        )
        # Create nested jobs
        chains: List[List[Job]] = []
        if req.jobs:
            jobs: Dict[str, Job] = {}
            deps: DefaultDict[str, Set[str]] = defaultdict(set)
            for j_req in req.jobs:
                chain = list(Job.from_req(j_req, parent=leader))
                first = chain[0]
                jobs[first.name] = first
                # Direct dependencies
                if j_req.depends_on:
                    deps[first.name].update(j_req.depends_on)
                # Input dependencies
                if j_req.inputs:
                    for i in j_req.inputs:
                        if i.job:
                            deps[first.name].add(i.job)
                chains.append(chain)
            # Bind children
            leader.children = [ref(j) for j in jobs.values()]
            # Bind children dependencies
            for dn, dset in deps.items():
                jobs[dn].depends_on = [ref(jobs[j]) for j in dset]
        # Finnlly yield all
        yield leader
        for ch in chains:
            yield from ch

    def set_task(self, task: Optional[asyncio.Task] = None) -> None:
        if self._task and not task:
            # Reset task
            self._task = None
        else:
            self._task = ref(task) if task else None

    def cancel(self) -> None:
        if not self._task:
            return
        task = self._task()
        if task:
            task.cancel()

    @property
    def is_scheduled(self) -> bool:
        if self._task is None:
            return False
        return bool(self._task())

    def iter_lock_names(self) -> Iterator[str]:
        """
        Iterate real lock names.
        """
        all_locks: Set[str] = set()
        if self.locks:
            for lock in self.locks:
                r = Template(lock).render(**self.environment)
                all_locks.add(r)
        for parent in self.iter_parents():
            all_locks.update(parent.iter_lock_names())
        yield from all_locks

    async def run(self) -> None:
        """
        Run action.
        """
        if self.action is None:
            return
        # Prepare input arguments
        kwargs: Dict[str, str] = {}
        if self.inputs:
            for i in self.inputs:
                if self.parent and i.job:
                    kwargs[i.name] = Template(i.value).render(
                        result=self.parent.results[i.job], **self.environment
                    )
                else:
                    kwargs[i.name] = Template(i.value).render(**self.environment)
        action = self.action(env=self.environment, logger=logger)
        r = await action.execute(**kwargs)
        if self.parent:
            logger.info("[%s] Set result: %s", self, r)
            self.parent.results[self.name] = r
