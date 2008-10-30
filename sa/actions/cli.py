from noc.sa.actions import BaseAction
import logging

class Action(BaseAction):
    ARGS=["user","password","commands"]
    def prepare_action(self):
        self.commands=self.args["commands"][:]
        self.set_fsm([
            (self.profile.pattern_username, self.s_username),
            (self.profile.pattern_password, self.s_password),
            (self.profile.pattern_prompt,   self.s_command),
        ])
        
    def s_username(self,match):
        self.submit(self.args["user"])
        return [
            (self.profile.pattern_password, self.s_password),
            (self.profile.pattern_prompt,   self.s_command),
        ]
        
    def s_password(self,match):
        self.submit(self.args["password"])
        return [
            (self.profile.pattern_prompt,   self.s_command),
            (self.profile.pattern_username, "FAILURE"),
            (self.profile.pattern_password, "FAILURE"),
        ]
        
    def s_command(self,match):
        if len(self.commands)==0:
            self.close(True)
            return
        self.to_collect_result=True
        c=self.commands.pop(0)
        self.submit(c)
        if len(self.commands):
            return [
                (self.profile.pattern_more,   self.s_more),
                (self.profile.pattern_prompt, self.s_command),
                ]
        else:
            return [
                (self.profile.pattern_more,   self.s_more),
                (self.profile.pattern_prompt, "SUCCESS"),
                ]
        
    def s_more(self,match):
        self.stream.write(self.profile.command_more)
        return [
            (self.profile.pattern_more, self.s_more),
            (self.profile.pattern_prompt, self.s_command),
            ]