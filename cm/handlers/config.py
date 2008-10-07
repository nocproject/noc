import noc.cm.handlers

class Handler(noc.cm.handlers.Handler):
    name="config"
    def pull(self):
        return self.object.profile.pull_config(self.object.stream_url)