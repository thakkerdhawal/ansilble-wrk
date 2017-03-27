#!/usr/bin/env python
# a simple ansible plugin to summarise only the info we require
# only from the modules we care about
"""
This is a custom callback module that summarises the network patching QA process

For each NIC item fro which we have a patching config, generate a report in JSON                                                                                                                                                              format.

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

def index_dictlist(alist, key):
    """
    converts a list of dict into a dict of lists, indexing on a chosen
    dictionary key, or optionally a string expansion (to combine keys)

    example:
    index_dictlist( foo, key='name')
    returns
    { 'name1' : [ {foo1} , {foo2} , {foo3}, ... ] } for all items in list that have a 'name' key

    Args:
        alist: a list of dict
        key: the key to use as an index, or a string expression
        exp(str): string generation expression to apply to each dict in turn.

    Returns:
        dict

    """
    output = {}
    for item in alist:
        try:
            idx = item[key]
            if idx not in output:
                output[idx] = [] 
                output[idx].append(item)
            else:
                output[idx].append(item)
        except KeyError:
            continue
    return output


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "new"
    # what does this imply?
    # can I write a callback that doesn't need this?
    CALLBACK_NEEDS_WHITELIST = True
    # which modules do we react to?
    LOG_MODULES = [
                   'assert',
                 ]

    
    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__(*args, **kwargs)
        self.task = None
        self.play = None
        self.reportlines = []
        self.stats_run = 0
        self._module = None
        self._taskname = None
        self._errmsg = None


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
        pass

    def v2_runner_item_on_failed(self, result):
        pass

    def v2_runner_item_on_skipped(self, result):
        pass

    def v2_playbook_on_play_start(self, play):
        # print play name
        self.play = play
        #print ("***** PLAY *******")
        #pprint (self.play.serialize())
        #print ("***** END PLAY *******\n")

    def v2_runner_on_ok(self, result, *args, **kwargs):
        if self._module in self.LOG_MODULES:
            host = result._host.get_name()
            taskname = self._taskname
            errmsg = result._result['invocation']['module_args']['msg'].replace('\n', '').replace('\r','').lower()
            retmsg = result._result['msg']
            errmsg, null = re.split(',', errmsg )
            dsr, act =  re.split(' *[!=]+ *', errmsg )
            if 'failed' in result._result.keys():
                rc = 1
            else:
                rc = 0
            self.reportlines.append({ 'host': host, 'taskname': taskname, 'desired': dsr, 'actual': act, 'rc': rc}) 


    v2_runner_on_failed = v2_runner_on_ok
    v2_runner_on_skipped = v2_runner_on_ok
    
    def playbook_on_stats(self, stats):
        results_per_host = index_dictlist(self.reportlines, key='host')
        #print (json.dumps(self.reportlines, indent=2))
        print (json.dumps(results_per_host, indent=2))



