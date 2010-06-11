# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## lib/fsm tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from unittest import TestCase
from noc.lib.fsm import *
from noc.lib.fileutils import temporary_file
##
##
##
class FSMTestCase(TestCase):
    class SimpleFSM(FSM):
        FSM_NAME="Simple FSM"
        DEFAULT_STATE="START"
        STATES={
            "START" : {
                "E1" : "S1",
                "E2" : "S2",
                "E3" : "S3"
            },
            "S1" : {
                "E2" : "S2",
                "E3" : "S3"
            },
            "S2" : {
                "E1" : "S1",
                "E2" : "S2",
                "E3" : "S3"
            },
            "S3" : {
                "E1" : "S1",
                "EE" : "END"
            },
            "END" : {},
        }
        def __init__(self):
            super(self.__class__,self).__init__()
            self.s2_enter_count=0
            self.s2_exit_count=0
            self.s2_e3_count=0
        def on_S2_enter(self):
            self.s2_enter_count+=1
        def on_S2_exit(self):
            self.s2_exit_count+=1
        def on_S2_E3(self):
            self.s2_e3_count+=1
        @check_state("S2")
        def check_state_s2(self):
            pass
        @check_state("S3")
        def check_state_s3(self):
            pass
            
    def test_simple_fsm(self):
        fsm=self.SimpleFSM()
        # Check FSM in the starting state
        self.assertEquals(fsm.get_state(),"START")
        # Perform transitions tests
        for event,final_state in [("E1","S1"),("E2","S2"),("E3","S3"),("E1","S1"),("E2","S2"),("E2","S2")]:
            fsm.event(event)
            self.assertEquals(fsm.get_state(),final_state)
        # Check @check_state_decorator
        fsm.check_state_s2() # Should pass
        self.assertRaises(AssertionError,fsm.check_state_s3) # Should fail
        # Check incorrect state. Try to send "EE" event from state "S2"
        self.assertRaises(FSMEventError,fsm.event,"EE")
        # Try to set incorrect state
        self.assertRaises(FSMStateError,fsm.set_state,"Invalid")
        # Check on_* execution
        self.assertEquals(fsm.s2_enter_count,2)
        self.assertEquals(fsm.s2_exit_count,1)
        self.assertEquals(fsm.s2_e3_count,1)
        # Try to generate Graphviz dot
        with temporary_file() as p:
            self.SimpleFSM.write_dot(p)
    
    class SimpleStreamFSM(StreamFSM):
        FSM_NAME="Simple Stream FSM"
        DEFAULT_STATE="START"
        STATES={
            "START"    : {
                "USERNAME" : "USERNAME",
                "PASSWORD" : "PASSWORD",
                "PROMPT"   : "PROMPT",
            },
            "USERNAME" : {
                "USERNAME" : "FAILURE",
                "PASSWORD" : "PASSWORD",
                "PROMPT"   : "PROMPT"
            },
            "PASSWORD" : {
                "USERNAME" : "FAILURE",
                "PASSWORD" : "PASSWORD",
                "PROMPT"   : "PROMPT",
            },
            "PROMPT" : {
                "PROMPT" : "PROMPT",
            }
        }
        def __init__(self):
            super(self.__class__,self).__init__()
            self.set_patterns([
                ("Username: ","USERNAME"),
                ("Password: ","PASSWORD"),
                ("prompt> ",  "PROMPT")])
    def test_simple_stream_fsm(self):
        fsm=self.SimpleStreamFSM()
        # Check starting state
        self.assertEquals(fsm.get_state(),"START")
        #
        for data,state in [
            ("Welcome!!!\n\nUsername: ","USERNAME"),
            ("Password: ","PASSWORD"),
            ("prompt> ", "PROMPT"),
            ("data",     "PROMPT"),
            ("pro",      "PROMPT"),
            ("mpt> ",    "PROMPT"),
            ]:
            fsm.feed(data)
            self.assertEquals(fsm.get_state(),state)
        