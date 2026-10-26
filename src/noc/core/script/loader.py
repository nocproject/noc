# ----------------------------------------------------------------------
# Script loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import glob
import importlib
import os
import re
import sys
import threading
from importlib.resources import files

# NOC modules
from noc.config import config
from noc.core.loader.base import BaseLoader
from noc.core.profile.loader import GENERIC_PROFILE

from .base import BaseScript


class ScriptLoader(BaseLoader):
    name = "script"

    rx_requires = re.compile(r"^\s+requires\s*=\s*\[([^\]]*)\]", re.DOTALL | re.MULTILINE)

    protected_names = {"profile", "__init__"}

    def __init__(self) -> None:
        super().__init__()
        self.scripts = {}  # Load scripts
        self.lock = threading.Lock()
        self.all_scripts = set()

    def get_script(self, name):
        """Load script and return BaseScript instance.
        Returns None when no script found or loading error occured
        """
        if name in self.protected_names:
            return None
        with self.lock:
            script = self.scripts.get(name)
            if not script:
                self.logger.info("Loading script %s", name)
                if not self.is_valid_name(name):
                    self.logger.error("Invalid script name")
                    return None
                try:
                    vendor, system, sn = name.split(".")
                except Exception as e:
                    self.logger.error('Error in script name "%s": %s', name, e)
                    return None
                is_generic = False
                for p in config.get_customized_paths(prefer_custom=True):
                    if os.path.exists(
                        os.path.join(
                            p or str(files("noc")),
                            "sa",
                            "profiles",
                            vendor,
                            system,
                            f"{sn}.py",
                        )
                    ):
                        base_name = "noc.custom" if p else "noc"
                        module_name = f"{base_name}.sa.profiles.{name}"
                        break
                else:
                    # Generic script
                    module_name = f"noc.sa.profiles.Generic.{sn}"
                    is_generic = True
                # Load script
                script = self.find_class(module_name, BaseScript, name)
                # Fix generic's module
                if script and is_generic:
                    # Create subclass with proper name
                    script = type("Script", (script,), {"name": name})
                    script.__module__ = f"noc.sa.profiles.{name}"
                self.scripts[name] = script
            return script

    def reload(self):
        """Reset script cache and release all modules"""
        with self.lock:
            self.logger.info("Reloading scripts")
            for s in self.scripts:
                self.logger.debug("Reload script %s", s.name)
                importlib.reload(sys.modules[s.__module__])
            self.scripts = {}
            self.all_scripts = set()

    def is_valid_name(self, name):
        return ".." not in name

    def find_scripts(self):
        """Scan all available scripts"""
        ns = set()
        # Load generic scripts
        generics = {}  # Name -> dependencies
        generic_path = os.path.join(str(files("noc")), "sa", "profiles", "Generic", "*.py")
        for path in glob.glob(generic_path):
            gn = path.rsplit(os.sep)[-1][:-3]
            if gn in self.protected_names:
                continue
            with open(path) as f:
                data = f.read()
                # Scan for requires = [..]
                match = self.rx_requires.search(data)
                if match:
                    generics[gn] = [s.strip()[1:-1] for s in match.group(1).split(",") if s.strip()]
                    ns.add(f"{GENERIC_PROFILE}.{gn}")
        # Load custom scripts, Load common scripts
        profiles = set()
        for base in config.get_customized_paths(prefer_custom=True):
            gx = os.path.join(base or str(files("noc")), "sa", "profiles", "*", "*", "*.py")
            for path in glob.glob(gx):
                vendor, system, name = path.split(os.sep)[-3:]
                name = name[:-3]
                if name in self.protected_names:
                    continue
                ns.add(f"{vendor}.{system}.{name}")
                profiles.add(f"{vendor}.{system}")
        # Apply generic scripts
        for p in profiles:
            for g in generics:
                fgn = f"{p}.{g}"
                if fgn in ns:
                    # Generic overriden with common script
                    continue
                if any(1 for r in generics[g] if f"{p}.{r}" not in ns):
                    continue  # Unsatisfied dependency
                # Add generic script
                ns.add(fgn)
        with self.lock:
            self.all_scripts = ns

    def iter_scripts(self):
        """Returns all available script names"""
        if not self.all_scripts:
            self.find_scripts()
        yield from sorted(self.all_scripts)

    def has_script(self, name):
        """Check script is exists"""
        if not self.all_scripts:
            self.find_scripts()
        return name in self.all_scripts


# Create singleton object
loader = ScriptLoader()
