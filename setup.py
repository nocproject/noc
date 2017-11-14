#!/usr/bin/env python
# ---------------------------------------------------------------------
# Distutils setup.py
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from __future__ import with_statement

import os
import subprocess
from setuptools import setup

#
# Prefix to where noc to be installed
#
PREFIX = "/opt/noc"


def get_version():
    """
    Read actual NOC version from VERSION file
    :return:
    """
    with open("VERSION") as f:
        return f.read().strip()


MANIFEST = []

REQUIREMENTS = [i.strip() for i in open("requirements/all.txt").readlines()]


def get_manifest():
    """
    Build distribution manifest
    :return:
    """
    global MANIFEST
    if not MANIFEST:
        if os.path.exists(".git"):
            # Rebuild MANIFEST file every time mercurial repo found
            proc = subprocess.Popen(["git", "ls-tree", "--name-only", "-r", "HEAD"], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            mf = stdout.splitlines()
            mf += ["MANIFEST"]
            with open("MANIFEST", "w") as f:
                f.write("\n".join(mf))
        with open("MANIFEST") as f:
            MANIFEST = [n for n in f.read().splitlines() if
                        not n.startswith(".hg")]
    return MANIFEST


def get_packages():
    """
    Return list of packages
    :return:
    """
    return [""] + [f[:-12].replace(os.sep, ".") for f in get_manifest() if
                   f.endswith("__init__.py") and f != "__init__.py"]


def get_data():
    """
    Return data files
    :return:
    """
    data = {}
    for df in get_manifest():
        d, f = os.path.split(df)
        if d not in data:
            data[d] = [df]
        else:
            data[d].append(df)
    return data.items()


#
# Pass control to the setuptools
#
setup(
    name="noc",
    version=get_version(),
    description="Network Operation Center's OSS",
    author="Dmitry Volodin",
    author_email="dvolodin7@google.com",
    url="http://nocproject.org/",
    license="BSD",
    long_description="""NOC Project is an Operation Support System (OSS) for telecom companies,
service providers, and enterprise Network Operation Centers (NOC).
Areas covered by NOC include fault management, service activation/provisioning, multi-VRF address space management,
configuration management, DNS provisioning, peering management, RPSL and BGP filter generation, and reporting.""",
    packages=get_packages(),
    data_files=get_data(),
    provides=["noc"],
    install_requires=REQUIREMENTS
)
