Ansible QA Testing for server onboarding
========================================

This repo contains a number of playbooks and roles to facilitate comparison of patching schedules 
(and other "golden" sources of info) with servers, once they have been installed.

To use it, place your inventory files (and their `group_vars` and `host_vars` directories, if any) into the `inventory` directory.

To adjust any settings, please update the local ansible.cfg file.

Current playbooks
---------------------------

  * `serverqa.yml` - playbook to run all of the other qa roles
  * `lldp.yml`  - playbook to use LLDP (via lldpad) to gather info about switch connections and compare them with a patching schedule.
  * `d42.yml` - playbook wrapping the `qa_d42` role
  * `ping.yml` - playbook wrapping the `qa_gw` role

Current Roles
-------------

  * `patching_qa` - role to deploy and read output from lldpad on target hosts, comparing it to golden data
  * `qa_d42` - role to confirm that the server is in D42 with the correct serial number
  * `qa_gw` - role to test connectivity to interface-specific gateways (and the default) using ping



Current inventory scripts
-------------------------

  * `parse_patching_schedule.py` - dynamic inventory script that parses a CSV patch schedule

The CSV input should fields in the following order:

    switch name, port ID, hostname, interface, cabletype, VLAN ID, bond device
    
Blank (or other non-matching) lines before this are ignored

This script, when run, will produce output similar to the following:

    { '_meta': {
        'hostvars': {
            hostname: {
                interface: {  
                    'switch_name': foo,
                    'port_id' : bar,
                    'bond': baz,
                    }
                }
            }
        }
    }

All properties, hostnames and interface names are lowercased.

How to run this
---------------

  * Update ansible.cfg appropriately for your environment
  * put your standard inventory into  the 'inventory' directory, including any group and host vars
  * put your patching schedule into the inventory directory in csv format
  * run the playbook a bit like this:


    [user@ansiblehost syseng-ansible-qa]$ ansible-playbook -l rate-bas-p002 -vvk lldp.yml
    Using /home/user/syseng-ansible-qa/ansible.cfg as config file
    SSH password: ********
    1 plays in lldp.yml
    Starting Play:  test LLDP
      - Starting Task
      * [SUCCESS] on host rate-bas-p002
      - Starting Task ensure lldpad is available
      * [SUCCESS] on host rate-bas-p002
      - Starting Task ensure lldpad is running
      * [SUCCESS] on host rate-bas-p002
      - Starting Task enable LLDP transmission on all interfaces
      * [FAILED] on host rate-bas-p002
      - Starting Task wait for lldpad to wake up
    Pausing for 10 seconds
    (ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
      * [SUCCESS] on host rate-bas-p002
      - Starting Task gather LLDP information
      * [SUCCESS] on host rate-bas-p002
      - Starting Task check patching schedule for rate-bas-p002
      * [FAILED] on host rate-bas-p002
    HOST: rate-bas-p002
    em1      port_id     : PASS     ethernet3 == ethernet3
    em1      switch_name : PASS     bas-jpm-0h1e-11s-ml1 == bas-jpm-0h1e-11s-ml1.picotrading.com
    imm      port_id     : SKIPPED  INTERFACE NOT PRESENT
    imm      switch_name : SKIPPED  INTERFACE NOT PRESENT
    p1p1     port_id     : PASS     ethernet4 == ethernet4
    p1p1     switch_name : SKIPPED  INTERFACE NOT PRESENT
    p3p2     port_id     : PASS     ethernet2 == ethernet2
    p3p2     switch_name : PASS     bas-jpm-0h1e-12s-ml2 == bas-jpm-0h1e-12s-ml2.picotrading.com
    p4p2     switch_name : PASS     bas-fic-0h1e-12s-c02 == bas-fic-0h1e-12s-c02.picotrading.com
    p5p1     port_id     : PASS     ethernet6 == ethernet6
    p5p1     switch_name : PASS     bas-fic-0h1e-11s-c01 == bas-fic-0h1e-11s-c01.picotrading.com
    p5p2     port_id     : PASS     ethernet5 == ethernet5
    p5p2     switch_name : PASS     bas-fic-0h1e-12s-c02 == bas-fic-0h1e-12s-c02.picotrading.com
    p6p1     port_id     : PASS     ethernet5 == ethernet5
    p6p1     switch_name : SKIPPED  INTERFACE NOT PRESENT
    p6p2     port_id     : PASS     ethernet6 == ethernet6
    p6p2     switch_name : PASS     bas-fic-0h1e-12s-c02 == bas-fic-0h1e-12s-c02.picotrading.com

The output above uses the 'titles' callback plugin for standard output, plus the patching_qa callback contained within the `patching_qa` role for the final report. This also produces JSON output for further parsing if required, this is found in the playbook directory as `patching_qa.json`

This file contains a nested dict like the following:

    {
      "rate-bas-p002": [
        {
          "actual": "bas-fic-0h1e-12s-c02.picotrading.com", 
          "desired": "bas-fic-0h1e-12s-c02", 
          "host": "rate-bas-p002", 
          "result": "PASS", 
          "interface": "p4p2", 
          "property": "switch_name"
        }, 
        ...
    }


