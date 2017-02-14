#!/usr/bin/env python
# a simple ansible callback plugin to essentially shut ansible up
"""
This is a custom callback module that stifles all output to stdout to test other callbacks
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

    def v2_runner_item_on_ok(self, result):
        pass

    def v2_runner_item_on_failed(self, result):
        pass
        
    def v2_runner_item_on_skipped(self, result):
        pass

    def playbook_on_stats(self, stats):
        pass
