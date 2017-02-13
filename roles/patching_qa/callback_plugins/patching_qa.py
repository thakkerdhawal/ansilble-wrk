#!/usr/bin/env python
# a simple ansible plugin to summarise only the info we require 
# only from the modules we care about
"""
This is a custom callback module that summarises the network patching QA process

For each NIC item fro which we have a patching config, generate a report in JSON format.
"""
from __future__ import print_function, division, absolute_import

__metaclass__ = type

import json
import re

from ansible.plugins.callback import CallbackBase
from pprint import pprint

from operator import itemgetter

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
            else:
                output[idx].append(item)
        except KeyError:
            continue
    return output


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "patching_qa"
    # what does this imply?
    # can I write callback that doesn't need this?
    CALLBACK_NEEDS_WHITELIST = True
    # which modules do we react to?
    LOG_MODULES = [
            'assert_pico',
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
        self.play = play
        self._hosts = play.hosts
        # pprint (self.play.serialize())

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.task = task
        self._module = self.task.action
        # pprint (self.task.serialize())

# for loop management, react to individual items in a list
    def v2_runner_item_on_ok(self, result):
        """
sample output:
{
  "changed": false,
  "_ansible_no_log": false,
  "_ansible_item_result": true,
  "item": [
    "p3p2",
    "port_id"
  ],
  "invocation": {
    "module_name": "assert_pico",
    "module_args": {
      "fail_msg": "p3p2.port_id: FAIL [ ethernet2 !=  ethernet2]",
      "pass_msg": "p3p2.port_id: PASS",
      "that": "patching['p3p2']['port_id'].split('.')|first == ansible_lldp['p3p2']['port_id'].split('.')|first"
    }
  },
  "msg": "p3p2.port_id: PASS"
}

        """
        if self._module in self.LOG_MODULES:
            res = result._result
            host = result._host.get_name()
            nic, prop = res['item']
            state = res.get('state', 'SKIPPED')
            if state == 'SKIPPED':
                des = 'Not available'
                act = 'Not available'
            else:
                des, act = re.split(' *[!=]+ *', res['msg'])

            self.reportlines.append({'host': host, 'interface': nic, 'property': prop, 'result': state, 'desired': des, 'actual': act })

    """
    desired output...
    { 'hostname.picotrading.com' :
        { 'p1p2': {
            'port_id': { 'result': PASS, 'desired': item.0, 'actual': item.1 }
            'switch_name': {'result': PASS, 'desired': item.0, 'actual': item.1 }
            },
        }
    }

    """

    def v2_runner_item_on_failed(self, result):
        self.v2_runner_item_on_ok(result)
        
    def v2_runner_item_on_skipped(self, result):
        self.v2_runner_item_on_ok(result)

    def playbook_on_stats(self, stats):
        results_per_host = index_dictlist(self.reportlines, key='host')
        for host, qa_results in results_per_host.iteritems():
            print ("HOST: %s" % host)
            for r in sorted(qa_results, key=itemgetter('interface')):
                if r['result'] == "PASS":
                    print ("%(interface)-8s %(property)-12s: %(result)-8s %(desired)s == %(actual)s" % r)
                elif r['result'] == "FAIL":
                    print ("%(interface)-8s %(property)-12s: %(result)-8s %(desired)s != %(actual)s" % r)
                else:
                    print ("%(interface)-8s %(property)-12s: %(result)-8s INTERFACE NOT PRESENT" %r)
        with open('patching_qa.json', 'wb') as out:
            json.dump(results_per_host, out, indent=2)
        # print (json.dumps(results_per_host, indent=2))
