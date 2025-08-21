# ----------------------------------------------------------------------
# @diagnostic decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable, Optional

# NOC modules
from noc.models import is_document
from .types import DiagnosticState, DiagnosticValue
from .hub import DiagnosticHub, DiagnosticItem

#
DEFER_CHANGE_STATE = "noc.core.diagnostic.decorator.change_state"


def iter_model_diagnostics(self, to_display: bool = False) -> Iterable[DiagnosticItem]:
    """Iterate over Model Instance diagnostics"""
    if not to_display:
        yield from self.diagnostic
        return
    for d in sorted(self.diagnostic, key=lambda x: x.config.display_order):
        if not d.show_in_display:
            continue
        yield d


def iter_document_diagnostics(self, to_display: bool = False) -> Iterable[DiagnosticItem]:
    """Iterate over document Diagnostics"""
    if not to_display:
        yield from self.diagnostic
        return
    for d in sorted(self.diagnostic, key=lambda x: x.config.display_order):
        if not d.show_in_display:
            continue
        yield d


def save_document_diagnostics(
    self,
    diagnostics: List[DiagnosticValue],
    resets: Optional[List[str]] = None,
    dry_run: bool = False,
):
    """"""


def save_model_diagnostics(self, diagnostics: List[DiagnosticItem], dry_run: bool = False):
    """Update Model Instance diagnostics"""
    from django.db import connection as pg_connection

    self.diagnostics = {d.diagnostic: d.get_value().model_dump() for d in diagnostics}
    if dry_run and not self.id:
        return
    self.__class__.objects.filter(id=self.id).update(diagnostics=self.diagnostics)
    self.update_init()
    self._reset_caches(self.id, credential=True)


def diagnostic(cls):
    """
    Diagnostic decorator.
     If model supported diagnostic (diagnostics field) add DiagnosticHub
    """

    def diagnostic(self) -> "DiagnosticHub":
        diagnostics = getattr(self, "_diagnostics", None)
        if diagnostics:
            return diagnostics
        self._diagnostics = DiagnosticHub(self)
        return self._diagnostics

    cls.diagnostic = property(diagnostic)
    if is_document(cls):
        # MongoEngine model
        cls.iter_diagnostics = iter_document_diagnostics
        if not hasattr(cls, "save_diagnostics"):
            cls.save_diagnostics = save_document_diagnostics
        # if not hasattr(cls, "get_caps_config"):
        #     cls.get_caps_config = get_caps_config

    else:
        # Django model
        cls.iter_diagnostics = iter_model_diagnostics
        if not hasattr(cls, "save_diagnostics"):
            cls.save_diagnostics = save_model_diagnostics
        # if not hasattr(cls, "get_caps_config"):
        #     cls.get_caps_config = get_caps_config

    return cls


def change_state(diagnostic: str, state: str, oid: str, model_id: str = "sa.ManagedObject"):
    """
    Defer change state
    Attrs:
        diagnostic: Diagnostic Name
        state: Diagnostic state
        oid: Instance ID
        model_id: Instance Model
    """
    from noc.models import get_model

    model = get_model(model_id)
    o = model.get_by_id(oid)
    if not hasattr(model, "diagnostic"):
        return
    o.diagnostic.set_state(diagnostic, DiagnosticState(state))
