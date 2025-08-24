# ----------------------------------------------------------------------
# DiagnosticItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Dict, List, Optional

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, EnumField, DateTimeField, BooleanField, DictField

# NOC modules
from noc.core.diagnostic.types import DiagnosticState, DiagnosticValue, CheckStatus


class CheckItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    name: str = StringField(required=True)
    status: bool = BooleanField(required=True)
    args: Dict[str, str] = DictField(required=False)
    skipped: bool = BooleanField(default=False)
    error: Optional[str] = StringField(required=False)

    def __str__(self):
        if not self.args:
            return f"{self.name} = {self.status}"
        arg0 = ";".join(f"{k}={v}" for k, v in self.args.items())
        return f"{self.name}({arg0}) = {self.status}"

    def to_status(self) -> CheckStatus:
        return CheckStatus(
            name=self.name,
            status=self.status,
            skipped=self.skipped,
            error=self.error or None,
        )

    @classmethod
    def from_status(cls, value: CheckStatus) -> "CheckItem":
        """Create Item from diagnostic value"""
        return CheckItem(
            name=value.name,
            status=value.status,
            skipped=value.skipped,
            error=value.error or None,
        )


class DiagnosticItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    diagnostic = StringField(required=True)
    state: DiagnosticState = EnumField(DiagnosticState, default=DiagnosticState("unknown"))
    checks: Optional[List[CheckItem]] = None
    reason: Optional[str] = StringField(required=False)
    changed: Optional[datetime.datetime] = DateTimeField(required=False)

    def __str__(self):
        return f"{self.diagnostic}: {','.join(c for c in self.checks)}; C: {self.changed}"

    def get_value(self) -> DiagnosticValue:
        """Convert to Value"""
        return DiagnosticValue(
            diagnostic=self.diagnostic,
            state=self.state,
            checks=[c.to_status() for c in self.checks],
            reason=self.reason or None,
            changed=self.changed,
        )

    @classmethod
    def from_value(cls, value: DiagnosticValue) -> "DiagnosticItem":
        """Create Item from diagnostic value"""
        return DiagnosticItem(
            diagnostic=value.diagnostic,
            state=value.state,
            checks=[CheckItem.from_status(c) for c in value.checks],
            reason=value.reason or None,
            changed=value.changed,
        )

    # def clean(self):
    #     super().clean()
    #     if self.default_value:
    #         self.capability.clean_value(self.default_value)
