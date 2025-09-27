# ----------------------------------------------------------------------
# BioSegTrial model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    ObjectIdField,
    IntField,
    BooleanField,
    DateTimeField,
)

# NOC modules
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.managedobject import ManagedObject
from noc.config import config


class BioSegTrial(Document):
    meta = {
        "collection": "biosegtrials",
        "strict": False,
        "auto_create_index": False,
        "indexes": [{"fields": ["expires"], "expireAfterSeconds": 0}],
    }

    # Reason of the trial
    reason = StringField()
    # Attacker segment
    attacker_id = ObjectIdField()
    # Target segment
    target_id = ObjectIdField()
    # Optional attacker object id
    attacker_object_id = IntField()
    # Optional target object id
    target_object_id = IntField()
    # Trial is processed
    processed = BooleanField(default=False)
    # Trial outcome, i.e. keep, eat, feed, calcify
    outcome = StringField()
    # Error report
    error = StringField()
    # Schedule for expiration, only when processed is True
    expires = DateTimeField()

    def __str__(self):
        return str(self.id)

    @classmethod
    def schedule_trial(
        cls,
        attacker: NetworkSegment,
        target: NetworkSegment,
        attacker_object: Optional[ManagedObject] = None,
        target_object: Optional[ManagedObject] = None,
        reason="manual",
    ) -> Optional["BioSegTrial"]:
        if target.id == attacker.id:
            # Not trial same
            return None
        if attacker.profile.is_persistent and attacker.parent != target.parent:
            # Persistent segment can trial only it has one parent (ring)
            return None
        trial = BioSegTrial(
            reason=reason, attacker_id=attacker.id, target_id=target.id, processed=False
        )
        if attacker_object and target_object:
            trial.attacker_object_id = attacker_object.id
            trial.target_object_id = target_object.id
        trial.save()
        return trial

    def set_outcome(self, outcome: str) -> None:
        self.outcome = outcome
        self.processed = True
        self.error = None
        self._set_expires()
        self.save()

    def set_error(self, error: str, fatal: bool = False) -> None:
        self.error = error
        if fatal:
            self.processed = True
            self._set_expires()
        self.save()

    def _set_expires(self) -> None:
        """
        Set expires when necessary

        :return:
        """
        if config.biosegmentation.processed_trials_ttl:
            self.expires = datetime.datetime.now() + datetime.timedelta(
                seconds=config.biosegmentation.processed_trials_ttl
            )

    def retry(self) -> None:
        """
        Restart trial

        :return:
        """
        self.processed = None
        self.error = None
        self.outcome = None
        self.save()
