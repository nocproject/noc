# ----------------------------------------------------------------------
# @diagnostic decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable

# NOC modules
from noc.models import is_document
from .types import DiagnosticValue, DiagnosticState
from .hub import DiagnosticHub


def iter_model_diagnostics(self) -> Iterable[DiagnosticValue]:
    """Iterate over Model Instance diagnostics"""


def iter_document_diagnostics(self) -> Iterable[DiagnosticValue]:
    """Iterate over document Diagnostics"""


def save_document_diagnostics(self, diagnostics: List[DiagnosticValue], dry_run: bool = False):
    """"""
    from noc.inv.models.capsitem import CapsItem

    self.diagnostics = [
        CapsItem(capability=c.capability, value=c.value, source=c.source.value, scope=c.scope or "")
        for c in diagnostics
    ]
    if dry_run and not self._created:
        return
    self.update(caps=self.caps)


def save_model_diagnostics(self, diagnostics: List[DiagnosticValue], dry_run: bool = False):
    """"""
    self.diagnostics = [d for d in diagnostics]
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
        cls.diagnostics = iter_model_diagnostics
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
