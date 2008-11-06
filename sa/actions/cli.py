from noc.sa.actions import BaseAction
import logging

class Action(BaseAction):
    ARGS=["user","password","super_password","commands"]
    def prepare_action(self):
        self.commands=self.args["commands"][:]
        fsm=[
            (self.profile.pattern_username, self.s_username),
            (self.profile.pattern_password, self.s_password),
        ]
        if self.profile.pattern_unpriveleged_prompt and self.args["super_password"]:
            fsm+=[
                (self.profile.pattern_unpriveleged_prompt, self.s_super),
            ]
        fsm+=[
            (self.profile.pattern_prompt,   self.s_command),
        ]
        self.set_fsm(fsm)
        
    def s_username(self,match):
        self.submit(self.args["user"])
        return [
            (self.profile.pattern_password, self.s_password),
            (self.profile.pattern_prompt,   self.s_command),
        ]
        
    def s_password(self,match):
        self.submit(self.args["password"])
        fsm=[
            (self.profile.pattern_prompt,   self.s_command),
        ]
        if self.profile.pattern_unpriveleged_prompt and self.args["super_password"]:
            fsm+=[
                (self.profile.pattern_unpriveleged_prompt, self.s_super),
            ]
        fsm+=[
            (self.profile.pattern_username, "FAILURE"),
            (self.profile.pattern_password, "FAILURE"),
        ]
        return fsm
        
    def s_super(self,match):
        self.submit(self.profile.command_super)
        return [
            (self.profile.pattern_prompt,   self.s_command),
            (self.profile.pattern_password, self.s_super_password),
        ]
        
    def s_super_password(self,match):
        self.submit(self.args["super_password"])
        return [
            (self.profile.pattern_prompt,   self.s_command),
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