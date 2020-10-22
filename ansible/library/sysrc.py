#!/usr/bin/env python

from __future__ import print_function
from sys import exit, argv
from json import dumps
from subprocess import Popen, PIPE
from shlex import split


def read_var(name):
    """Reads variable with name"""
    args = ["sysrc", "-n", "-i", name]
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rc = process.returncode

    if rc != 0 or stderr != "":
        print(dumps({"failed": True, "msg": "failed to read variable named %s" % name}))
        exit(1)
    else:
        stdout = stdout[:-1]
        return stdout


def write_var(name, value):
    """Write variable with name and value"""
    binding = "%s=%s" % (name, value)
    args = ["sysrc", "-n", binding]
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rc = process.returncode

    if rc != 0 or stderr != "":
        print(dumps({"failed": True, "msg": "failed to write variable %s" % binding}))
        exit(1)
    else:
        stdout = stdout[:-1]
        return stdout


def assert_var(name, should):
    """Check if variable have value called 'should'"""
    actual = read_var(name)
    if actual == should:
        return should
    print(dumps({"failed": True, "msg": "failed assertion. %s != %s" % (name, should)}))
    exit(1)


if __name__ == "__main__":
    args_file = argv[1]
    with open(args_file) as f:
        args_data = f.read()
    args = split(args_data)
    changed = False
    changes = {}
    defined = {}

    for arg in args:
        if "=" not in arg:
            continue
        name, new_value = arg.split("=")
        defined[name] = new_value
        old_value = read_var(name)
        if old_value == new_value:
            continue
        changed = True
        changes[name] = new_value
        write_var(name, new_value)
        assert_var(name, new_value)

    print(
        dumps(
            {
                "changed": changed,
                "defined": defined,
                "changes": changes,
            }
        )
    )
    exit(0)
