# ---------------------------------------------------------------------
# Alarm handlers for test cases
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


def is_run_one(alarm, **kwargs):
    alarm._run_handler = "run_one"


def is_run_two(alarm, **kwargs):
    alarm._run_handler = "run_two"


def is_run_three(alarm, **kwargs):
    alarm._run_handler = "run_three"
