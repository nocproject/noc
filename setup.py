#!/usr/bin/env python
##----------------------------------------------------------------------
## NOC setup.py
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import glob
from distutils.core import setup
from distutils.command.sdist import sdist
from distutils.extension import Extension

VERSION_PATH = "VERSION"
DESCRIPTION_PATH = "README"
REQUIREMENTS_PATH = "requirements.txt"
SPEEDUPS = "speedup/*.pyx"


def get_version():
    """
    Read actual NOC version from VERSION file
    :return: Version as a string
    """
    with open(VERSION_PATH) as f:
        return f.read().strip()


def get_long_description():
    """
    Read long NOC description
    :return:
    """
    with open(DESCRIPTION_PATH) as f:
        return f.read()


def get_requirements():
    """
    Build requirements from requirements.txt
    :return:
    """
    r = []
    with open(REQUIREMENTS_PATH) as f:
        for l in r:
            l = l.strip()
            if not l:
                continue
            pkg, op, version = None, None, None
            for op in ("==", ">="):
                if op in l:
                    pkg, version = l.split(op)
                    break
            if not pkg:
                continue
            r += ["%s (%s%s)" % (pkg, op, version)]
    return r


class NOCSdist(sdist):
    def run(self):
        from Cython.Build import cythonize
        cythonize(SPEEDUPS)
        sdist.run(self)

setup(
    name="noc",
    version=get_version(),
    author="nocproject.org",
    url="http://nocproject.org",
    author_email="pkg@nocproject.org",
    license="BSD",
    description="The Open-Source OSS for telecom, internet and service providers",
    long_description=get_long_description(),
    requires=get_requirements(),
    cmdclass={
        "sdist": NOCSdist
    },
    ext_modules=[Extension("speedup", ["*.c"])]
)
