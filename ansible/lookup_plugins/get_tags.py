from __future__ import absolute_import, division, print_function

from __main__ import cli
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):
    def run(self, terms="", **kwargs):
        """Get tags"""
        tag = cli.get_opt("tags")
        if tag:
            tags = cli.get_opt("tags")
        else:
            tags = []
        return [tags]
