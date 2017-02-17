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
        #print ("***** Task start *******")
        self.task = task
        self._module = self.task.action
        self._taskname = self.task.name
        #pprint (self.task.serialize())
        #print ("***** Task End *******")


# for loop management, react to individual items in a list
    def v2_runner_item_on_ok(self, result):
        if self._module in self.LOG_MODULES:
            res = result._result
            interface = '_'.join(res['item'])
            taskname = self._taskname
            ip =  res['cmd'][-1] 
            rc = res['rc']
            host = result._host.get_name()
            self.reportlines.append({'host': host, 'interface': interface, 'taskname': taskname, 'rc': rc, 'ping_ip': ip })



    def v2_runner_item_on_failed(self, result):
        self.v2_runner_item_on_ok(result)

    def v2_runner_item_on_skipped(self, result):
        self.v2_runner_item_on_ok(result)

    def v2_playbook_on_play_start(self, play):
        self.play = play
        pass

    def playbook_on_stats(self, stats):
        print(json.dumps(self.reportlines, indent=2))
        #pprint("reportlines %s" % self.reportlines)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        pass

