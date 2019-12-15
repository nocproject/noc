# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# mib API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import subprocess
import re
import imp
import datetime

# Third-party modules
import six

# NOC modules
from noc.config import config
from noc.core.service.api import API, api
from noc.core.fileutils import temporary_file, safe_rewrite
from noc.fm.models.mib import MIB
from noc.core.error import ERR_MIB_NOT_FOUND, ERR_MIB_MISSED, ERR_MIB_TOOL_MISSED


class MIBAPI(API):
    """
    MIB API
    """

    name = "mib"
    rx_module_not_found = re.compile(r"{module-not-found}.*`([^']+)'")
    rx_oid = re.compile(r"^\d+(\.\d+)+")

    SMI_ENV = {"SMIPATH": config.path.mib_path}

    def get_path(self, name):
        """
        Get Full file path for MIB name
        :param name: MIB name
        :return: path
        """
        return os.path.join(config.path.mib_path, "%s.mib" % name)

    @api
    def get_text(self, name):
        """
        Get MIB text
        :param name: MIB name
        :return:
        """
        path = self.get_path(name)
        if os.path.exists(path):
            with open(path) as f:
                return {"status": True, "data": f.read()}
        return {"status": False, "msg": "Not found", "code": ERR_MIB_NOT_FOUND}

    @api
    def compile(self, data):
        """
        Compile MIB, upload to database and store MIB file
        :param data: MIB text
        :return:
        """
        if not config.path.smilint or not os.path.exists(config.path.smilint):
            return {"status": False, "msg": "smilint is missed", "error": ERR_MIB_TOOL_MISSED}
        if not config.path.smilint or not os.path.exists(config.path.smidump):
            return {"status": False, "msg": "smidump is missed", "error": ERR_MIB_TOOL_MISSED}
        # Put data to temporary file
        with temporary_file(data) as tmp_path:
            # Pass MIB through smilint to detect missed modules
            self.logger.debug("Pass MIB through smilint to detect missed modules")
            f = subprocess.Popen(
                [config.path.smilint, "-m", tmp_path], stderr=subprocess.PIPE, env=self.SMI_ENV
            ).stderr
            for l in f:
                match = self.rx_module_not_found.search(l.strip())
                if match:
                    return {
                        "status": False,
                        "msg": "Required MIB missed: %s" % match.group(1),
                        "code": ERR_MIB_MISSED,
                    }
            self.logger.debug("Convert MIB to python module and load")
            # Convert MIB to python module and load
            with temporary_file() as py_path:
                subprocess.check_call(
                    [config.path.smidump, "-k", "-q", "-f", "python", "-o", py_path, tmp_path],
                    env=self.SMI_ENV,
                )
                with open(py_path) as f:
                    p_data = unicode(f.read(), "ascii", "ignore").encode("ascii")
                with open(py_path, "w") as f:
                    f.write(p_data)
                m = imp.load_source("mib", py_path)
            # NOW we can deduce module name
            mib_name = m.MIB["moduleName"]
            # Check module dependencies
            depends_on = {}  # MIB Name -> Object ID
            self.logger.debug("Check module dependencies: %s", m.MIB.get("imports", ""))
            if "imports" in m.MIB:
                for i in m.MIB["imports"]:
                    if "module" not in i:
                        continue
                    rm = i["module"]
                    if rm in depends_on:
                        continue
                    md = MIB.get_by_name(rm)
                    if md is None:
                        return {
                            "status": False,
                            "msg": "Required MIB missed: %s" % rm,
                            "code": ERR_MIB_MISSED,
                        }
                    depends_on[rm] = md
            # Get MIB latest revision date
            try:
                last_updated = datetime.datetime.strptime(
                    sorted([x["date"] for x in m.MIB[mib_name]["revisions"]])[-1], "%Y-%m-%d %H:%M"
                )
            except ValueError:
                last_updated = datetime.datetime(year=1970, month=1, day=1)
            self.logger.debug("Extract MIB typedefs")
            # Extract MIB typedefs
            typedefs = {}
            if "typedefs" in m.MIB:
                for t in m.MIB["typedefs"]:
                    typedefs[t] = MIB.parse_syntax(m.MIB["typedefs"][t])
            # Check mib already uploaded
            mib_description = m.MIB[mib_name].get("description", None)
            mib = MIB.objects.filter(name=mib_name).first()
            if mib is not None:
                mib.description = mib_description
                mib.last_updated = last_updated
                mib.depends_on = sorted(depends_on)
                mib.typedefs = typedefs
                mib.save()
                # Delete all MIB Data
                mib.clean()
            else:
                # Create MIB
                mib = MIB(
                    name=mib_name,
                    description=mib_description,
                    last_updated=last_updated,
                    depends_on=sorted(depends_on),
                    typedefs=typedefs,
                )
                mib.save()
            # Upload MIB data
            cdata = []
            for i in ["nodes", "notifications"]:
                if i in m.MIB:
                    cdata += [
                        {
                            "name": "%s::%s" % (mib_name, node),
                            "oid": v["oid"],
                            "description": v.get("description"),
                            "syntax": v["syntax"]["type"] if "syntax" in v else None,
                        }
                        for node, v in six.iteritems(m.MIB[i])
                    ]
            mib.load_data(cdata)
            # Move file to permanent place
            safe_rewrite(self.get_path(mib_name), data)
        return {"status": True, "mib": mib_name}

    @api
    def lookup(self, oid):
        """
        Convert oid to symbolic name and vise versa
        :param oid:
        :return:
        """
        if self.rx_oid.match(oid):
            # oid -> name
            name = MIB.get_name(oid)
            oid = oid
        else:
            name = oid
            oid = MIB.get_oid(name)
        if oid and name:
            return {"status": True, "oid": oid, "name": name}
        return {"status": False}
