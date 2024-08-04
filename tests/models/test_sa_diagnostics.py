# ----------------------------------------------------------------------
# sa.ManagedObject diagnostics tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from dataclasses import dataclass

# NOC modules
from noc.core.wf.diagnostic import (
    DiagnosticConfig,
    DiagnosticState,
    DiagnosticHub,
    SNMP_DIAG,
    CheckResult,
    Check,
)


@dataclass
class Object(object):
    id = 10
    diagnostics = {}
    effective_labels = []
    access_preference = "S"

    @property
    def diagnostic(self) -> "DiagnosticHub":
        diagnostics = getattr(self, "_diagnostics", None)
        if diagnostics:
            return diagnostics
        self._diagnostics = DiagnosticHub(self, dry_run=True)
        return self._diagnostics

    def iter_diagnostic_configs(self):
        """
        Iterate over object diagnostics
        :return:
        """
        yield DiagnosticConfig(diagnostic="D1")
        yield DiagnosticConfig(diagnostic="D2")
        yield DiagnosticConfig(
            SNMP_DIAG,
            display_description="Check Device response by SNMP request",
            checks=[Check(name="SNMPv1"), Check(name="SNMPv2c")],
            blocked=self.access_preference == "C",
            run_policy="F",
            run_order="S",
            discovery_box=True,
            alarm_class="NOC | Managed Object | Access Lost",
            alarm_labels=["noc::access::method::SNMP"],
            reason="Blocked by AccessPreference" if self.access_preference == "C" else None,
        )
        yield DiagnosticConfig(
            "Access",
            dependent=["SNMP", "CLI", "HTTP"],
            show_in_display=False,
            alarm_class="NOC | Managed Object | Access Degraded",
        )


def test_set_state():
    o = Object()
    o.diagnostics = {
        "D2": {"diagnostic": "D2", "state": "failed", "reason": "1"},
        "Access": {"diagnostic": "Access", "state": "failed", "reason": "2"},
    }
    assert o.diagnostic.D2.state == DiagnosticState.failed
    o.diagnostic.set_state("D1", DiagnosticState.enabled)
    assert o.diagnostic.D1.state == DiagnosticState.enabled
    o.diagnostic.update_checks([CheckResult(check="SNMPv1", status=False)])
    assert o.diagnostic.SNMP.state == DiagnosticState.failed
    o.diagnostic.update_checks(
        [CheckResult(check="SNMPv1", status=False), CheckResult(check="SNMPv1", status=True)]
    )
    assert o.diagnostic.SNMP.state == DiagnosticState.enabled
    assert o.diagnostic.Access.state == DiagnosticState.enabled
    assert o.diagnostics["Access"]["state"] == "enabled"


def test_change_object_config_state():
    o = Object()
    o.diagnostics = {
        "D2": {"diagnostic": "D2", "state": "failed", "reason": "1"},
        "SNMP": {
            "diagnostic": "SNMP",
            "state": "failed",
            "checks": [{"name": "SNMPv1", "status": False, "error": "Timeout"}],
            "reason": "1",
        },
        "Access": {"diagnostic": "Access", "state": "failed", "reason": "2"},
    }
    assert o.diagnostic.SNMP.state == DiagnosticState.failed
    o.diagnostic.refresh_diagnostics()
    assert o.diagnostic.SNMP.state == DiagnosticState.failed
    o.access_preference = "C"
    o.diagnostic.refresh_diagnostics()
    assert o.diagnostic.SNMP.state == DiagnosticState.blocked


def test_bulk_set_state():
    o = Object()
    o.diagnostics = {
        "D2": {"diagnostic": "D2", "state": "failed", "reason": "1"},
        "Access": {"diagnostic": "Access", "state": "failed", "reason": "2"},
    }
    with DiagnosticHub(o, dry_run=True) as d:
        assert d.D2.state == DiagnosticState.failed
        d.set_state("D1", DiagnosticState.enabled)
        assert d.D1.state == DiagnosticState.enabled
        d.update_checks([CheckResult(check="SNMPv1", status=False)])
        assert d.SNMP.state == DiagnosticState.failed
        d.update_checks(
            [CheckResult(check="SNMPv1", status=False), CheckResult(check="SNMPv1", status=True)]
        )
        assert d.SNMP.state == DiagnosticState.enabled
        assert d.Access.state == DiagnosticState.enabled
        assert o.diagnostics["Access"]["state"] != "enabled"

    assert o.diagnostics["Access"]["state"] == "enabled"
