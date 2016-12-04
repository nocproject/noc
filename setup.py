#!/usr/bin/env python
##----------------------------------------------------------------------
## NOC setup.py
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import glob, os
from setuptools import find_packages, Extension, setup

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


with open('requirements.txt') as f:
    requirements = f.read().splitlines()


def get_data_files(extentions, directories):
    results = []

    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(extentions):
                results.append((root, map(lambda f: root + "/" + f, files)))

    for root, dirs, files in os.walk("."):
        if root.endswith(directories):
            results.append((root, map(lambda f: root + "/" + f, files)))
    return results


setup(
    name="noc",
    version=get_version(),
    author="nocproject.org",
    url="http://nocproject.org",
    author_email="pkg@nocproject.org",
    license="BSD",
    description="The Open-Source OSS for telecom, internet and service providers",
    long_description=get_long_description(),
    # install_requires=requirements,
    package_dir={"noc": "."},
    data_files=get_data_files(
        (".css", ".html", ".js", ".gif", ".hbs", ".svg",
         ".json", ".sh", ".txt",
         ".mo", ".po", ".pot",
         "VERSION", "LICENSE", "AUTHORS"),
        ("scripts/*", "etc/*", "commands/*")),
    packages=["noc.%s" % x for x in find_packages()],
    ext_modules=[Extension("noc/speedup/ber", ["speedup/ber.c"]),
                 Extension("noc/speedup/ip", ["speedup/ip.c"])],
    zip_safe=False
)

