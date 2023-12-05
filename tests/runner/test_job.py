# ----------------------------------------------------------------------
# Job tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable, Dict, Tuple
import asyncio

# Third-party modules
import pytest

# NOC modules
from noc.sa.models.job import JobStatus
from noc.core.runner.runner import Runner
from noc.core.runner.job import Job
from noc.core.runner.models.jobreq import JobRequest


@pytest.mark.parametrize(
    ("req", "expected"),
    [
        (JobRequest(name="job-1"), JobStatus.WAITING),
        (JobRequest(name="job-1", require_approval=True), JobStatus.PENDING),
    ],
)
def test_initial_status(req: JobRequest, expected: JobStatus) -> None:
    status = Job._get_initial_status(req)
    assert status == expected


@pytest.mark.parametrize(
    ("jobs", "expected"),
    [
        ([], True),
        ([JobRequest(name="", action="success")], False),
        ([JobRequest(name="job-1", action="success")], True),
        (
            [
                JobRequest(name="job-1", action="success"),
                JobRequest(name="job-2", action="success"),
            ],
            True,
        ),
        (
            [
                JobRequest(name="job-1", action="success"),
                JobRequest(name="job-2", action="success"),
                JobRequest(name="job-3", action="success"),
            ],
            True,
        ),
        (
            [
                JobRequest(name="job-1", action="success"),
                JobRequest(name="job-2", action="success"),
                JobRequest(name="job-1", action="success"),
            ],
            False,
        ),
    ],
)
def test_unique_names(jobs: List[JobRequest], expected: bool) -> None:
    def jobs_iter(jobs: List[JobRequest]) -> Iterable[Job]:
        for req in jobs:
            yield from Job.from_req(req)

    r = Job._is_unique_names(jobs_iter(jobs))
    assert r == expected


@pytest.mark.parametrize(
    "req",
    [
        JobRequest(
            name="leader",
            jobs=[
                JobRequest(name="job-1", action="success"),
                JobRequest(name="job-2", action="success"),
                JobRequest(name="job-1", action="success"),
            ],
        ),
        JobRequest(
            name="leader",
            jobs=[
                JobRequest(name="job-1", action="success", depends_on=["job-3"]),
                JobRequest(name="job-2", action="success", depends_on=["job-1"]),
                JobRequest(name="job-3", action="success", depends_on=["unknown"]),
            ],
        ),
        JobRequest(
            name="leader",
            jobs=[
                JobRequest(name="job-1", action="success", depends_on=["job-3"]),
                JobRequest(name="job-2", action="success", depends_on=["job-1"]),
                JobRequest(name="job-3", action="success", depends_on=["job-2"]),
            ],
        ),
        # Neither action or jobs
        JobRequest(name="job"),
        # action and jobs
        JobRequest(
            name="leader", action="success", jobs=[JobRequest(name="job-1", action="success")]
        ),
        # invalid action
        JobRequest(name="job", action="totallymessedup"),
    ],
)
def test_from_req_errors(req: JobRequest):
    runner = Runner()
    with pytest.raises(ValueError):
        runner.submit(req)
    # Should not submit jobs
    assert len(list(runner.iter_jobs())) == 0


def test_is_leader() -> None:
    req = JobRequest(
        name="leader",
        jobs=[
            JobRequest(name="job-1", action="success"),
            JobRequest(name="job-2", action="success"),
            JobRequest(name="job-3", action="success"),
        ],
    )
    jobs = list(Job.from_req(req))
    assert len(jobs) == 4
    assert jobs[0].is_leader
    assert not jobs[1].is_leader
    assert not jobs[2].is_leader
    assert not jobs[3].is_leader


class RunnerWrapper(Runner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_state = {}

    def set_status(self, job: Job, status: JobStatus) -> None:
        super().set_status(job, status)
        self.last_state[job.name] = status


def get_scenario_id(x) -> str:
    if isinstance(x, JobRequest):
        return str(x.description)
    if isinstance(x, dict):
        return x["root"].name


@pytest.mark.parametrize(
    ("req", "expected"),
    [
        # single-success
        (
            JobRequest(name="root", action="success", description="single-succes"),
            {"root": JobStatus.SUCCESS},
        ),
        # single-failed
        (
            JobRequest(name="root", action="fail", description="single-failed"),
            {"root": JobStatus.FAILED},
        ),
        # single-warning
        (
            JobRequest(name="root", action="fail", description="single-warning", allow_fail=True),
            {"root": JobStatus.WARNING},
        ),
        # group-single-success
        (
            JobRequest(
                name="root",
                description="group-single-succes",
                jobs=[JobRequest(name="job-1", action="success")],
            ),
            {"root": JobStatus.SUCCESS, "job-1": JobStatus.SUCCESS},
        ),
        # group-single-failed
        (
            JobRequest(
                name="root",
                description="group-single-failed",
                jobs=[JobRequest(name="job-1", action="fail")],
            ),
            {"root": JobStatus.FAILED, "job-1": JobStatus.FAILED},
        ),
        # group-single-warning
        (
            JobRequest(
                name="root",
                description="group-single-warning",
                jobs=[JobRequest(name="job-1", action="fail", allow_fail=True)],
            ),
            {"root": JobStatus.SUCCESS, "job-1": JobStatus.WARNING},
        ),
        # group-two-success
        (
            JobRequest(
                name="root",
                description="group-two-success",
                jobs=[
                    JobRequest(name="job-1", action="success"),
                    JobRequest(name="job-2", action="success"),
                ],
            ),
            {"root": JobStatus.SUCCESS, "job-1": JobStatus.SUCCESS, "job-2": JobStatus.SUCCESS},
        ),
        # group-two-success-deps
        (
            JobRequest(
                name="root",
                description="group-two-success-deps",
                jobs=[
                    JobRequest(name="job-1", action="success", depends_on=["job-2"]),
                    JobRequest(name="job-2", action="success"),
                ],
            ),
            {"root": JobStatus.SUCCESS, "job-1": JobStatus.SUCCESS, "job-2": JobStatus.SUCCESS},
        ),
        # group-two-one-fail1
        (
            JobRequest(
                name="root",
                description="group-two-one-fail1",
                jobs=[
                    JobRequest(name="job-1", action="fail"),
                    JobRequest(name="job-2", action="success"),
                ],
            ),
            {"root": JobStatus.FAILED, "job-1": JobStatus.FAILED, "job-2": JobStatus.CANCELLED},
        ),
        # group-two-one-fail2
        (
            JobRequest(
                name="root",
                description="group-two-one-fail2",
                jobs=[
                    JobRequest(name="job-1", action="success"),
                    JobRequest(name="job-2", action="fail"),
                ],
            ),
            {"root": JobStatus.FAILED, "job-1": JobStatus.SUCCESS, "job-2": JobStatus.FAILED},
        ),
        # group-two-two-fails
        (
            JobRequest(
                name="root",
                description="group-two-two-fails",
                jobs=[
                    JobRequest(name="job-1", action="fail"),
                    JobRequest(name="job-2", action="fail"),
                ],
            ),
            {"root": JobStatus.FAILED, "job-1": JobStatus.FAILED, "job-2": JobStatus.CANCELLED},
        ),
        # group-two-warning1
        (
            JobRequest(
                name="root",
                description="group-two-warning1",
                jobs=[
                    JobRequest(name="job-1", action="fail", allow_fail=True),
                    JobRequest(name="job-2", action="success"),
                ],
            ),
            {"root": JobStatus.SUCCESS, "job-1": JobStatus.WARNING, "job-2": JobStatus.SUCCESS},
        ),
        # group-two-warning2
        (
            JobRequest(
                name="root",
                description="group-two-warning2",
                jobs=[
                    JobRequest(name="job-1", action="success"),
                    JobRequest(name="job-2", action="fail", allow_fail=True),
                ],
            ),
            {"root": JobStatus.SUCCESS, "job-1": JobStatus.SUCCESS, "job-2": JobStatus.WARNING},
        ),
        # group-tree-success
        (
            JobRequest(
                name="root",
                description="job-tree-success",
                jobs=[
                    JobRequest(
                        name="group-1",
                        jobs=[
                            JobRequest(name="job-1-1", action="success"),
                            JobRequest(name="job-1-2", action="success"),
                            JobRequest(name="job-1-3", action="success"),
                        ],
                    ),
                    JobRequest(
                        name="group-2",
                        jobs=[
                            JobRequest(name="job-2-1", action="success"),
                            JobRequest(name="job-2-2", action="success"),
                            JobRequest(name="job-2-3", action="success"),
                        ],
                    ),
                    JobRequest(
                        name="group-3",
                        jobs=[
                            JobRequest(name="job-3-1", action="success"),
                            JobRequest(name="job-3-2", action="success"),
                            JobRequest(name="job-3-3", action="success"),
                        ],
                    ),
                ],
            ),
            {
                "root": JobStatus.SUCCESS,
                "group-1": JobStatus.SUCCESS,
                "group-2": JobStatus.SUCCESS,
                "group-3": JobStatus.SUCCESS,
                "job-1-1": JobStatus.SUCCESS,
                "job-1-2": JobStatus.SUCCESS,
                "job-1-3": JobStatus.SUCCESS,
                "job-2-1": JobStatus.SUCCESS,
                "job-2-2": JobStatus.SUCCESS,
                "job-2-3": JobStatus.SUCCESS,
                "job-3-1": JobStatus.SUCCESS,
                "job-3-2": JobStatus.SUCCESS,
                "job-3-3": JobStatus.SUCCESS,
            },
        ),
        # group-tree-success-deps
        (
            JobRequest(
                name="root",
                description="job-tree-success-deps",
                jobs=[
                    JobRequest(
                        name="group-1",
                        jobs=[
                            JobRequest(name="job-1-1", action="success", depends_on=["job-1-2"]),
                            JobRequest(name="job-1-2", action="success", depends_on=["job-1-3"]),
                            JobRequest(name="job-1-3", action="success"),
                        ],
                    ),
                    JobRequest(
                        name="group-2",
                        jobs=[
                            JobRequest(
                                name="job-2-1", action="success", depends_on=["job-2-2", "job-2-3"]
                            ),
                            JobRequest(name="job-2-2", action="success", depends_on=["job-2-3"]),
                            JobRequest(name="job-2-3", action="success"),
                        ],
                    ),
                    JobRequest(
                        name="group-3",
                        jobs=[
                            JobRequest(name="job-3-1", action="success"),
                            JobRequest(name="job-3-2", action="success"),
                            JobRequest(name="job-3-3", action="success"),
                        ],
                    ),
                ],
            ),
            {
                "root": JobStatus.SUCCESS,
                "group-1": JobStatus.SUCCESS,
                "group-2": JobStatus.SUCCESS,
                "group-3": JobStatus.SUCCESS,
                "job-1-1": JobStatus.SUCCESS,
                "job-1-2": JobStatus.SUCCESS,
                "job-1-3": JobStatus.SUCCESS,
                "job-2-1": JobStatus.SUCCESS,
                "job-2-2": JobStatus.SUCCESS,
                "job-2-3": JobStatus.SUCCESS,
                "job-3-1": JobStatus.SUCCESS,
                "job-3-2": JobStatus.SUCCESS,
                "job-3-3": JobStatus.SUCCESS,
            },
        ),
        # group-tree-success
        (
            JobRequest(
                name="root",
                description="job-tree-success",
                jobs=[
                    JobRequest(
                        name="group-1",
                        jobs=[
                            JobRequest(name="job-1-1", action="success"),
                            JobRequest(name="job-1-2", action="success"),
                            JobRequest(name="job-1-3", action="success"),
                        ],
                    ),
                    JobRequest(
                        name="group-2",
                        jobs=[
                            JobRequest(name="job-2-1", action="success"),
                            JobRequest(name="job-2-2", action="fail"),
                            JobRequest(name="job-2-3", action="success"),
                        ],
                    ),
                    JobRequest(
                        name="group-3",
                        jobs=[
                            JobRequest(name="job-3-1", action="success"),
                            JobRequest(name="job-3-2", action="success"),
                            JobRequest(name="job-3-3", action="success"),
                        ],
                    ),
                ],
            ),
            {
                "root": JobStatus.FAILED,
                "group-1": JobStatus.SUCCESS,
                "group-2": JobStatus.FAILED,
                "group-3": JobStatus.CANCELLED,
                "job-1-1": JobStatus.SUCCESS,
                "job-1-2": JobStatus.SUCCESS,
                "job-1-3": JobStatus.SUCCESS,
                "job-2-1": JobStatus.SUCCESS,
                "job-2-2": JobStatus.FAILED,
                "job-2-3": JobStatus.CANCELLED,
                "job-3-1": JobStatus.CANCELLED,
                "job-3-2": JobStatus.CANCELLED,
                "job-3-3": JobStatus.CANCELLED,
            },
        ),
    ],
    ids=get_scenario_id,
)
def test_scenario(req: JobRequest, expected: Dict[str, JobStatus]):
    async def inner() -> None:
        runner = RunnerWrapper()
        runner.submit(req)
        await asyncio.wait_for(runner.drain(), 1.0)
        return runner.last_state

    r = asyncio.run(inner())
    assert r == expected


@pytest.mark.parametrize(
    ("req", "expected"),
    [
        (JobRequest(name="job", action="success"), []),
        (
            JobRequest(name="job", action="success", environment={"a": "1", "b": "2"}),
            [("a", "1"), ("b", "2")],
        ),
        (
            JobRequest(
                name="job",
                environment={"a": "1", "b": "2"},
                jobs=[JobRequest(name="g1", action="success", environment={"a": "4", "c": "3"})],
            ),
            [("a", "4"), ("b", "2"), ("c", "3")],
        ),
    ],
)
def test_job_env(req: JobRequest, expected: List[Tuple[str, str]]) -> None:
    job = list(Job.from_req(req))[-1]
    r = list(sorted(job.environment.items()))
    assert r == expected


@pytest.mark.parametrize(
    ("req", "expected"),
    [
        (JobRequest(name="job", action="success"), []),
        (JobRequest(name="job", action="success", locks=["global", "l-1"]), ["global", "l-1"]),
        (
            JobRequest(
                name="job",
                action="success",
                environment={"a": "1", "b": "2"},
                locks=["global", "text", "a=={{a}}"],
            ),
            ["a==1", "global", "text"],
        ),
        (
            JobRequest(
                name="job",
                environment={"a": "1", "b": "2"},
                locks=["global", "up", "a=={{a}}"],
                jobs=[
                    JobRequest(
                        name="g1",
                        action="success",
                        environment={"a": "4", "c": "3"},
                        locks=["inner", "a=={{a}}"],
                    )
                ],
            ),
            ["a==1", "a==4", "global", "inner", "up"],
        ),
    ],
)
def test_iter_locks(req: JobRequest, expected: List[str]) -> None:
    job = list(Job.from_req(req))[-1]
    r = list(sorted(job.iter_lock_names()))
    assert r == expected
