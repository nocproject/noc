#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Check gitlab MR labels
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import os
import sys


ENV_LABELS = "CI_MERGE_REQUEST_LABELS"
ENV_CI = "CI"
ERR_OK = 0
ERR_FAIL = 1

PRI_LABELS = ["pri::p1", "pri::p2", "pri::p3", "pri::p4"]
COMP_LABELS = ["comp::trivial", "comp::low", "comp::medium", "comp::high"]
KIND_LABELS = ["kind::feature", "kind::improvement", "kind::bug", "kind::cleanup"]
BACKPORT = "backport"


def get_labels():
    """
    Get list of labels.
    :return: List of labels or None if environment is not set
    """
    if ENV_LABELS not in os.environ and ENV_CI not in os.environ:
        return None
    return os.environ.get(ENV_LABELS, "").split(",")


def go_url(anchor):
    return "https://docs.getnoc.com/master/en/go.html#%s" % anchor


def check_pri(labels):
    """
    Check `pri::*`
    :param labels:
    :return: List of problems
    """
    pri = [x for x in labels if x.startswith("pri::")]
    if not pri:
        return [
            "'pri::*' label is not set. Must be one of %s.\n"
            "Refer to %s for details." % (", ".join(PRI_LABELS), go_url("dev-mr-labels-pri"))
        ]
    if len(pri) > 1:
        return [
            "Multiple 'pri::*' labels defined. Must be exactly one.\n"
            "Refer to %s for details." % go_url("dev-mr-labels-priority")
        ]
    pri = pri[0]
    if pri not in PRI_LABELS:
        return [
            "Invalid label %s. Must be one of %s.\n"
            "Refer to %s for details." % (", ".join(PRI_LABELS), go_url("dev-mr-labels-pri"))
        ]
    return []


def check_comp(labels):
    """
    Check `comp::*`
    :param labels:
    :return:
    """
    comp = [x for x in labels if x.startswith("comp::")]
    if not comp:
        return [
            "'comp::*' label is not set. Must be one of %s.\n"
            "Refer to %s for details." % (", ".join(COMP_LABELS), go_url("dev-mr-labels-comp"))
        ]
    if len(comp) > 1:
        return [
            "Multiple 'comp::*' labels defined. Must be exactly one.\n"
            "Refer to %s for details." % go_url("dev-mr-labels-comp")
        ]
    comp = comp[0]
    if comp not in COMP_LABELS:
        return [
            "Invalid label %s. Must be one of %s.\n"
            "Refer to %s for details." % (", ".join(COMP_LABELS), go_url("dev-mr-labels-comp"))
        ]
    return []


def check_kind(labels):
    """
    Check `kind::*`
    :param labels:
    :return:
    """
    kind = [x for x in labels if x.startswith("kind::")]
    if not kind:
        return [
            "'kind::*' label is not set. Must be one of %s.\n"
            "Refer to %s for details." % (", ".join(KIND_LABELS), go_url("dev-mr-labels-kind"))
        ]
    if len(kind) > 1:
        return [
            "Multiple 'kind::*' labels defined. Must be exactly one.\n"
            "Refer to %s for details." % go_url("dev-mr-labels-kind")
        ]
    kind = kind[0]
    if kind not in KIND_LABELS:
        return [
            "Invalid label %s. Must be one of %s.\n"
            "Refer to %s for details." % (", ".join(KIND_LABELS), go_url("dev-mr-labels-kind"))
        ]
    return []


def check_backport(labels):
    if BACKPORT not in labels:
        return []
    kind = [x for x in labels if x.startswith("kind::")]
    if len(kind) != 1:
        return []  # Already have problems
    if kind[0] != "kind::bug":
        return [
            "'%s' cannot be used with '%s'.\n" "Use only with 'kind::bug'" % (BACKPORT, kind[0])
        ]
    return []


def check_affected(labels):
    # Get required labels
    should_have = set()
    for f in sys.argv[1:]:
        parts = f.split(os.sep)
        if parts[0] == "core":
            should_have.add("core")
        elif parts[0] == "docs":
            should_have.add("documentation")
        elif parts[0] == "ui":
            should_have.add("ui")
        elif parts[0] == "sa" and parts[1] == "profiles":
            should_have.add("profiles")
        elif len(parts) > 1 and parts[1] == "migrations":
            should_have.add("migration")
        elif parts[0] == "tests":
            should_have.add("tests")
    return [
        "'%s' label is not set.\n"
        "Refer to %s for details." % (l, go_url("dev-mr-labels-affected"))
        for l in should_have
        if l not in labels
    ]


def check(labels):
    """
    Perform all checks
    :param labels: List of labels
    :return: List of policy violations
    """
    problems = []
    problems += check_pri(labels)
    problems += check_comp(labels)
    problems += check_kind(labels)
    problems += check_backport(labels)
    problems += check_affected(labels)
    return problems


def main():
    labels = get_labels()
    problems = []
    if labels is None:
        problems += [
            "%s environment variable is not defined. Must be called within Gitlab CI" % ENV_LABELS
        ]
    else:
        problems += check(labels)
    if problems:
        print("\n\n".join(problems))
        sys.exit(ERR_FAIL)
    sys.exit(ERR_OK)


if __name__ == "__main__":
    main()
