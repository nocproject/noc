# ---------------------------------------------------------------------
# Pipeline Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from enum import Enum
from typing import Iterable


# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ReferenceField,
    ListField,
    BooleanField,
    ObjectIdField,
    EmbeddedDocumentListField,
    DateTimeField,
    DictField,
)

# NOC models
from noc.core.model.decorator import on_delete_check


class JobStatus(Enum):
    """
    Job status.

    Attributes:
        * `p` - Pending, waiting for manual approve.
        * `w` - Waiting, ready to run.
        * `r` - Running
        * `S` - Suspended
        * `s` - Success
        * `f` - Failed with error
        * `w` - Warning. Failed, but allowed to fail.
        * `c` - Cancelled
    """

    PENDING = "p"
    WAITING = "w"
    RUNNING = "r"
    SUSPENDED = "S"
    SUCCESS = "s"
    FAILED = "f"
    WARNING = "W"
    CANCELLED = "c"


class InputMapping(EmbeddedDocument):
    """
    Input parameter mapping.

    Arguments:
        name: Input parameter name, as passed to the action.
        value: Parameter value. Contains jinja2 template
            which will be rendered at actual code,
            using pipeline environment as context.
        job: If not empty, expose `result` variable
            containing job result.
    """

    name = StringField(required=True)
    value = StringField(required=True)
    job = StringField(required=False)

    def __str__(self) -> str:
        """Convert to string representation."""
        return f"{self.name} = {self.value}"


@on_delete_check(check=[("sa.Job", "parent")])
class Job(Document):
    """
    Pipeline job.

    Attributes:
        parent: Parent job.
        name: Name, when parent is not empty, must be unique
            within parent.
        description: Optional description.
        labels: Job labels.
        effective_labels: Full set of labels.
        status: See JobStatus for values.
        allow_fail: If true, generate `w` status instead of `f`
        depends_on: List of jobs which can be completed before
            starting this one.
        action: Action name.
        locks: List of named locks.
        created_at: Creation timestamp.
        started_at: A timestamp when the job is entered Running state.
        completed_at: A timestamp when the job is leaved Runnig state.
        after: Optional timestamp of deferred execution.
        deadline: Optional timestamp when pipeline
            considered expired.
        results: Dict of results of the complete jobs.
    """

    meta = {
        "collection": "jobs",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["resource_path", "entity"],
    }
    parent = ReferenceField("self", required=False)
    name = StringField(required=True)
    description = StringField()
    # labels = ListField(StringField())
    # effective_labels = ListField(StringField())
    status = StringField(
        choices=[s.value for s in JobStatus], default=JobStatus.WAITING.value, required=True
    )
    allow_fail = BooleanField(default=False)
    depends_on = ListField(ObjectIdField(), required=False)
    action = StringField(required=False)
    inputs = EmbeddedDocumentListField(InputMapping)
    locks = ListField(StringField(), required=False)
    environment = DictField(required=False)
    created_at = DateTimeField(required=True)
    started_at = DateTimeField(required=False)
    completed_at = DateTimeField(required=False)
    resource_path = ListField(StringField(), required=False)
    # Resource starting job
    entity = StringField(required=False)
    # after = DateTimeField(required=False)
    # deadline = DateTimeField(required=False)
    results = DictField(required=False)

    def __str__(self) -> str:
        return f"{self.name}::{self.action}"

    @property
    def effective_environment(self) -> dict[str, str]:
        """
        Get full environment
        """
        env = self.environment.copy() if self.environment else {}
        if self.parent:
            for k, v in self.parent.environment.items():
                if k not in env:
                    env[k] = v
        return env

    @classmethod
    def iter_last_for_entities(cls, entities: Iterable[str]) -> Iterable["Job"]:
        """
        Iterate last jobs for entities.

        Args:
            entities: Iterable of entity strings.

        Returns:
            Yield last jobs for entitites.
        """
        ids = [
            x["_id"]
            for x in cls._get_collection().aggregate(
                [
                    # Filter entities
                    {"$match": {"entity": {"$in": list(entities)}}},
                    #
                    {
                        "$sort": {"entity": 1, "_id": -1},
                    },
                    #
                    {"$group": {"_id": "$entity", "max_id": {"$first": "$_id"}}},
                    #
                    {"$project": {"_id": "$max_id"}},
                ]
            )
        ]
        yield from cls.objects.filter(id__in=ids)
