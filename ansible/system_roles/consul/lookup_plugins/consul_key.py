# -*- coding: utf-8 -*-
# Generate consul keyfile

# Python modules
import os
import base64

# Ansible modules
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):
    def run(self, terms, inject=None, **kwargs):
        """Generate consul keyfile"""
        ret = []

        # this can happen if the variable contains a string, strictly not desired for lookup
        # plugins, but users may try it, so make it work.
        if not isinstance(terms, list):
            terms = [terms]

        for term in terms:
            params = term.split()
            relpath = params[0]
            path = self._loader.path_dwim(relpath)
            if os.path.exists(path):
                with open(path) as f:
                    key = f.read().strip()
            else:
                d = os.path.dirname(path)
                if not os.path.exists(d):
                    os.makedirs(d, mode=0o700)
                # Generate key file
                key = str(base64.b64encode(os.urandom(16)).decode())
                with open(path, "w") as f:
                    os.chmod(path, 0o600)
                    f.write(key)
            ret += [key]
        return ret
