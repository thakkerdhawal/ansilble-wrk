#!/usr/bin/env python
# a simple ansible plugin to summarise only the info we require
# only from the modules we care about
"""
This is a custom callback module that summarises the network patching QA process

"""
from __future__ import print_function, division, absolute_import

__metaclass__ = type

import json
import re

from ansible.plugins.callback import CallbackBase
from pprint import pprint


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "parse"
    # what does this imply?
    # can I write a callback that doesn't need this?
    CALLBACK_NEEDS_WHITELIST = True
    # which modules do we react to?
    LOG_MODULES = [
            'assert', 
            'command',
    ]

     
    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__(*args, **kwargs)
        self.task = None
        self.play = None
        self.reportlines = []
        self.stats_run = 0
 

    def v2_on_any(self, *args, **kwargs):
        pass

    def v2_playbook_on_play_start(self, play):
        pass

    def v2_playbook_on_task_start(self, task, is_conditional):
        pass

# for loop management, react to individual items in a list
    def v2_runner_item_on_ok(self, result):
        pass

    def v2_runner_item_on_failed(self, result):
        pass

    def v2_runner_item_on_skipped(self, result):
        pass

    def v2_playbook_on_play_start(self, play):
        # print play name
        self.play = play
        print ("Starting Play: ", play.name)
        pass

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.task = task
        print ("  - Starting Task %s" %(task.name))

    def v2_runner_on_ok(self, result, *args, **kwargs):
        res = result._result 
        #modname = res['module_name']
        print ("   * [SUCCESS] on host %s" %(result._host.get_name()))
        #print ("  * [result] for host %s: %s" %(result._host.get_name() ,result._result)) 
        #print ("  * [result] for host %s: %s" %(result._host.get_name() , modname)) 

    def v2_runner_on_failed(self, result, ignore_errors):
        print ("  * [FAILED] on host %s" %(result._host.get_name()))
        res = result._result 
        #modname = res['invocation']
        #print ("  * [result] for host %s: %s" %(result._host.get_name() ,modname)) 

    def v2_runner_on_skipped(self, result):
        print ("  * [SKIPPED] host %s" %(result._host.get_name()))

    def playbook_on_stats(self, stats):
        pass

