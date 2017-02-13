#!/usr/bin/env python
# a simple ansible plugin to summarise only the info we require 
# only from the modules we care about
"""
This is a custom callback module that summarises the network patching QA process

For each NIC item fro which we have a patching config, generate a report in JSON format.

also, pretty print to stdout.

TODO?
post output to BAM endpoint as JSON?



"""
from __future__ import print_function, division, absolute_import

__metaclass__ = type

import json
import re

from ansible.plugins.callback import CallbackBase
from pprint import pprint

class CallbackModule(CallbackBase):
    """
    SHUTUP!
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "stdout"
    CALLBACK_NAME = "silent"
    # what does this imply?
    # can I write callback that doesn't need this?
    CALLBACK_NEEDS_WHITELIST = True

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

    def playbook_on_stats(self, stats):
        pass
