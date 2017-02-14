#!/usr/bin/env python
# a simple ansible plugin to summarise only the info we require
"""
This is a custom callback module that displays only minimal info to stdout
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
    CALLBACK_NAME = "titles"
    # what does this imply?
    # can I write a callback that doesn't need this?
    CALLBACK_NEEDS_WHITELIST = True
    # which modules do we react to?

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
        if self.task.name.strip() == '':
            name = self.task.action
        else:
            name = self.task.name
        print ("  - Starting Task %s" % name )

    def v2_runner_on_ok(self, result, *args, **kwargs):
        print ("  * [SUCCESS] on host %s" %(result._host.get_name()))

    def v2_runner_on_failed(self, result, ignore_errors):
        print ("  * [FAILED ] on host %s" %(result._host.get_name()))

    def v2_runner_on_skipped(self, result):
        print ("  * [SKIPPED] host %s" %(result._host.get_name()))

    def v2_runner_item_on_ok(self, result):
        print ("      + [SUCCESS] %s - %s" % (result._host.get_name(), '.'.join(result._result['item'])))

    def v2_runner_item_on_failed(self, result):
        print ("      + [FAILED ] %s - %s" % (result._host.get_name(), '.'.join(result._result['item'])))

    def v2_runner_item_on_skipped(self, result):
        print ("      + [SKIPPED] %s - %s" % (result._host.get_name(), '.'.join(result._result['item'])))

    def playbook_on_stats(self, stats):
        pass
