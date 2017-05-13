from __future__ import (absolute_import, division, print_function)

from ansible.plugins.lookup import LookupBase
from __main__ import cli

class LookupModule(LookupBase):

    def run(self, terms='', **kwargs):
        tag = cli.get_opt('tags')
        if tag:
            tags = cli.get_opt('tags')
        else:
            tags = []
        return [ tags ]
