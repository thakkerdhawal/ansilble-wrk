Ansible QA Testing for server onboarding
========================================

This repo contains a number of playbooks and roles to facilitate comparison of patching schedules (and other "golden" sources of info with servers, once they have been installed.

To use it, place your inventory files (and their `group_vars` and `host_vars` directories, if any) into the `inventory` directory.

To adjust any settings, please update the local ansible.cfg file.

Current playbooks
---------------------------

  * lldp.yml  - playbook to use LLDP (via lldpad) to gather info about switch connections and compare them with a patching schedule.

Current Roles
-------------

  * patching_qa - role to deploy and read output from lldpad on target hosts, comparing it to golden data



Current inventory scripts
-------------------------

  * parse_patching_schedule.py - dynamic inventory script that parses a CSV patch schedule
