#!/usr/bin/env python
##----------------------------------------------------------------------
## Distutils setup.py
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from __future__ import with_statement
from distutils.core import setup
import distutils.command.sdist
from distutils.command.install import INSTALL_SCHEMES
import subprocess
import os

##
## Prefix to where noc to be installed
##
PREFIX = "/opt/noc"


def get_version():
    """
    Read actual NOC version from VERSION file
    :return:
    """
    with open("VERSION") as f:
        return f.read().strip()

MANIFEST = []


def get_manifest():
    """
    Build distribution manifest
    :return:
    """
    global MANIFEST
    if not MANIFEST:
        if os.path.exists(".hg"):
            # Rebuild MANIFEST file every time mercurial repo found
            proc = subprocess.Popen(["hg", "locate"], stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            mf = stdout.splitlines()
            if os.path.exists(".hgsub"):
                with open(".hgsub") as sf:
                    for l in sf:
                        if "=" not in l:
                            continue
                        sr, r = l.split("=", 1)
                        sr = sr.strip()
                        proc = subprocess.Popen(["hg", "-R", sr, "locate"],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
                        stdout, stderr = proc.communicate()
                        mf += [sr + "/" + x for x in stdout.splitlines()]
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


class noc_sdist(distutils.command.sdist.sdist):
    """
    Get file list for sdist from MANIFEST
    """
    def get_file_list(self):
        self.filelist.files = get_manifest()

##
## Monkeypatch distutils to install noc to the desired location
##
for scheme in INSTALL_SCHEMES.values():
    scheme["purelib"] = PREFIX
    scheme["data"] = PREFIX
##
## Pass control to the setuptools
##
setup(name="noc",
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
      cmdclass={"sdist": noc_sdist},
      packages=get_packages(),
      data_files=get_data(),
      provides=["noc"],
      requires=[
          "psycopg2 (>= 2.0.5)",
          "pycrypto (>= 2.3)",
          "pymongo (>= 1.1)"
          ]
      )
