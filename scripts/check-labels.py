#!/usr/bin/env python
# ---------------------------------------------------------------------
# Check gitlab MR labels
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import sys
import argparse
import time
from xml.sax.saxutils import escape


ENV_LABELS = "CI_MERGE_REQUEST_LABELS"
ENV_CI = "CI"
ERR_OK = 0
ERR_FAIL = 1


JUNIT_CLASS_NAME = "scripts.check_labels"
JUNIT_FILE = escape(sys.argv[0])


class FatalError(Exception):
    pass


class TestCase(object):
    def __init__(self, name=None, path=None, fatal=False, ref=None):
        self.name = name
        self.path = path
        self.fatal = fatal
        self.start = None
        self.stop = None
        self.failure = None
        self.ref = ref

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop = time.time()
        if exc_type is None:
            return
        self.failure = str(exc_val)
        if exc_type is AssertionError:
            if self.ref:
                self.failure += (
                    f"\nRefer to https://docs.getnoc.com/master/en/go.html#{self.ref} for details."
                )
            if self.fatal:
                raise FatalError
            return True

    @property
    def is_failed(self):
        return bool(self.failure)

    def to_junit_xml(self):
        duration = self.stop - self.start
        if self.path:
            test_name = f"{self.name}[{self.path}]"
        else:
            test_name = self.name
        r = [
            f'  <testcase classname="{JUNIT_CLASS_NAME}" file="{JUNIT_FILE}" line="1" '
            f'name="{test_name}" time="{duration:.3f}">'
        ]
        if self.is_failed:
            r.append(f'    <failure message="{escape(self.failure)}"></failure>')
        r.append("  </testcase>")
        return "\n".join(r)


class TestSuite(object):
    PRI_LABELS = ["pri::p1", "pri::p2", "pri::p3", "pri::p4"]
    COMP_LABELS = ["comp::trivial", "comp::low", "comp::medium", "comp::high"]
    KIND_LABELS = ["kind::feature", "kind::improvement", "kind::bug", "kind::cleanup"]
    BACKPORT = "backport"

    def __init__(self, files, verbose=False):
        self.files = files
        self.tests = []
        self.start = None
        self.stop = None
        self._is_failed = None
        self._labels = None
        self.verbose = verbose

    def to_junit_xml(self):
        pass

    def test(self, name, path=None, fatal=False, ref=None):
        t = TestCase(name=name, path=path, fatal=fatal, ref=ref)
        self.tests += [t]
        return t

    def check(self):
        if self.verbose:
            print("# MR Labels:\n%s\n" % "\n".join(self.labels))
            print("# Affected files:\n%s\n" % "\n".join(self.files))
        self.start = time.time()
        try:
            self.do_check()
        except FatalError:
            pass
        self.stop = time.time()

    def do_check(self):
        self.check_env_labels()
        if self.is_contribution():
            print("Thank you for contributing to the project!")
            return
        self.check_required_scoped_labels()
        self.check_backport_label()
        self.check_affected()

    @property
    def is_failed(self):
        if self._is_failed is None:
            self._is_failed = any(t for t in self.tests if t.is_failed)
        return self._is_failed

    def report(self):
        print("\n\n".join(t.failure for t in self.tests if t.is_failed))

    def report_junit(self, path):
        duration = self.stop - self.start
        n_tests = len(self.tests)
        n_failures = sum(1 for t in self.tests if t.is_failed)
        r = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f'<testsuite errors="0" failures="{n_failures}" name="check-labels" skipped="0" tests="{n_tests}" time="{duration:.3f}">',
        ]
        for t in self.tests:
            r.append(t.to_junit_xml())
        r.append("</testsuite>")
        report = "\n".join(r)
        # Write report
        rdir = os.path.dirname(path)
        if not os.path.exists(rdir):
            os.makedirs(rdir)
        with open(path, "w") as f:
            f.write(report)
        print(os.path.dirname(path))

    @property
    def labels(self):
        if self._labels is None:
            self._labels = os.environ.get(ENV_LABELS, "").split(",")
        return self._labels

    def is_contribution(self):
        """
        Check if MR is from forked repo
        :return:
        """
        return os.environ.get("CI_MERGE_REQUEST_SOURCE_PROJECT_PATH") != os.environ.get(
            "CI_MERGE_REQUEST_PROJECT_PATH"
        )

    def check_env_labels(self):
        """
        Check ENV_LABELS is exit
        :return:
        """
        with self.test("test_env_labels", fatal=True):
            assert (
                ENV_LABELS in os.environ or ENV_CI in os.environ
            ), f"{ENV_LABELS} environment variable is not defined. Must be called within Gitlab CI"

    def check_backport_label(self):
        with self.test("test_backport"):
            if self.BACKPORT not in self.labels:
                return
            kind = [x for x in self.labels if x.startswith("kind::")]
            for label in kind:
                assert (
                    label == "kind::bug"
                ), f"'{self.BACKPORT}' cannot be used with '{label}'.\n Use only with 'kind::bug'"

    def check_required_scoped_labels(self):
        def test_required(label, choices):
            prefix = f"{label}::"
            seen_labels = [x for x in self.labels if x.startswith(prefix)]
            n_labels = len(seen_labels)
            # Check label is exists
            with self.test(f"test_{label}_label_set", ref=f"dev-mr-labels-{label}"):
                assert (
                    n_labels > 0
                ), f"'{label}::*' label is not set. Must be one of {', '.join(choices)}."
            # Check label is defined only once
            with self.test(f"test_{label}_label_single", ref="dev-mr-labels-{label}"):
                assert n_labels < 2, f"Multiple '{label}::*' labels defined. Must be exactly one."
            # Check label is known one
            with self.test(f"test_{label}_known", ref=f"dev-mr-labels-{label}"):
                for x in seen_labels:
                    assert (
                        x in choices
                    ), f"Invalid label '{x}'. Must be one of {', '.join(choices)}."

        test_required("pri", self.PRI_LABELS)
        test_required("comp", self.COMP_LABELS)
        test_required("kind", self.KIND_LABELS)

    def check_affected(self):
        def test_affected(label, checker):
            with self.test(f"test_{label}", ref="dev-mr-labels-affected"):
                has_changed = any(1 for p in file_parts if checker(p))
                if has_changed:
                    assert label in self.labels, f"'{label}' label is not set."
                else:
                    assert label not in self.labels, f"'{label}' label must not be set."

        file_parts = [f.split(os.sep) for f in self.files]
        test_affected("ansible", lambda x: x[0] == "ansible")
        test_affected("core", lambda x: x[0] == "core")
        test_affected("confdb", lambda x: x[:3] == ["core", "confdb", "syntax"])
        test_affected("documentation", lambda x: x[0] == "docs")
        test_affected("ui", lambda x: x[0] == "ui")
        test_affected("profiles", lambda x: x[:2] == ["sa", "profiles"])
        test_affected("migration", lambda x: len(x) > 2 and x[1] == "migrations")
        test_affected("tests", lambda x: x[0] == "tests")
        test_affected("nbi", lambda x: x[:3] == ["services", "nbi", "api"])
        test_affected("rust", lambda x: x[0] == "rust")
        test_affected("collections", lambda x: x[0] == "collections")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit-report", help="Write JUnit XML report to file")
    parser.add_argument("files", nargs="*", help="List of affected files")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    suite = TestSuite(args.files, verbose=args.verbose)
    suite.check()
    if suite.is_failed:
        suite.report()
    if args.junit_report:
        suite.report_junit(args.junit_report)
    sys.exit(ERR_FAIL if suite.is_failed else ERR_OK)


if __name__ == "__main__":
    main()
