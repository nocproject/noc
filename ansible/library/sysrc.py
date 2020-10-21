#!/usr/bin/env python

from sys import exit, argv
from json import dumps
from subprocess import Popen, PIPE
from shlex import split



def read_var(name):
    args           = ["sysrc", "-n", "-i", name]
    process        = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rc             = process.returncode

    if rc != 0 or stderr != "":
        print dumps({
            "failed" : True,
            "msg"    : "failed to read variable named " + name
        })
        exit(1)
    else:
        stdout = stdout[:-1]
        return stdout



def write_var(name, value):
    binding        = name + "=" + value
    args           = ["sysrc", "-n", binding]
    process        = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rc             = process.returncode

    if rc != 0 or stderr != "":
        print dumps({
            "failed" : True,
            "msg"    : "failed to write variable " + binding
        })
        exit(1)
    else:
        stdout = stdout[:-1]
        return stdout



def assert_var(name, should):
    actual = read_var(name)
    if actual != should:
        print dumps({
            "failed" : True,
            "msg"    : "failed assertion. " + name + " != " + should
        })
        exit(1)
    else:
        return should



args_file = argv[1]
args_data = file(args_file).read()
args      = split(args_data)
changed   = False
changes   = {}
defined   = {}

for arg in args:
    if "=" in arg:
        (name, new_value) = arg.split("=")
        defined[name]     = new_value
        old_value         = read_var(name)

        if old_value != new_value:
            changed       = True
            changes[name] = new_value

            write_var(name, new_value)
            assert_var(name, new_value)

print dumps({
    "changed" : changed,
    "defined" : defined,
    "changes" : changes,
})
exit(0)
