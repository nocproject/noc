# ----------------------------------------------------------------------
# Job tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable, Dict
import asyncio

# Third-party modules
import pytest

# NOC modules
from noc.sa.models.job import JobStatus
from noc.services.runner.runner import Runner
from noc.services.runner.job import Job
from noc.services.runner.models.jobreq import JobRequest


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


@pytest.mark.parametrize(
    ("req", "expected"),
    [
        # single-success
        (JobRequest(name="root", action="success"), {"root": JobStatus.SUCCESS}),
        # single-failed
        (JobRequest(name="root", action="fail"), {"root": JobStatus.FAILED}),
        # single-warning
        (JobRequest(name="root", action="fail", allow_fail=True), {"root": JobStatus.WARNING}),
        # group-single-success
        (
            JobRequest(name="root", jobs=[JobRequest(name="job-1", action="success")]),
            {"root": JobStatus.SUCCESS, "job-1": JobStatus.SUCCESS},
        ),
        # group-single-failed
        (
            JobRequest(name="root", jobs=[JobRequest(name="job-1", action="fail")]),
            {"root": JobStatus.FAILED, "job-1": JobStatus.FAILED},
        ),
        # group-single-warning
        (
            JobRequest(
                name="root", jobs=[JobRequest(name="job-1", action="fail", allow_fail=True)]
            ),
            {"root": JobStatus.SUCCESS, "job-1": JobStatus.WARNING},
        ),
        # group-two-success
        (
            JobRequest(
                name="root",
                jobs=[
                    JobRequest(name="job-1", action="success"),
                    JobRequest(name="job-2", action="success"),
                ],
            ),
            {"root": JobStatus.SUCCESS, "job-1": JobStatus.SUCCESS, "job-2": JobStatus.SUCCESS},
        ),
        # group-two-one-fail1
        (
            JobRequest(
                name="root",
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
                jobs=[
                    JobRequest(name="job-1", action="success"),
                    JobRequest(name="job-2", action="fail", allow_fail=True),
                ],
            ),
            {"root": JobStatus.SUCCESS, "job-1": JobStatus.SUCCESS, "job-2": JobStatus.WARNING},
        ),
    ],
    ids=[
        "single-success",
        "single-failed",
        "single-warning",
        "group-single-success",
        "group-single-failed",
        "group-single-warning",
        "group-two-success",
        "group-two-one-fail1",
        "group-two-one-fail2",
        "group-two-two-fails",
        "group-two-warning1",
        "group-two-warnning2",
    ],
)
def test_scenario(req: JobRequest, expected: Dict[str, JobStatus]):
    async def inner() -> None:
        runner = RunnerWrapper()
        runner.submit(req)
        await asyncio.wait_for(runner.drain(), 1.0)
        return runner.last_state

    r = asyncio.run(inner())
    assert r == expected
