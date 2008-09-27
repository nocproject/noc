from noc.cm.handlers import BaseHandler

class Handler(BaseHandler):
    name="config"
    def pull(self):
        return self.object.profile.pull_config(self.object.stream_url)