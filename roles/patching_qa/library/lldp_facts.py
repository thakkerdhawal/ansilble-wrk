#!/usr/bin/env python
# a custom ansible module to use LLDP to discover network information
import os
import re
import subprocess

"""

* This is normal LLDPTOOL output (lldptool -t -n -i INTERFACE)
Chassis ID TLV
        MAC: 44:4c:a8:d6:f9:05
Port ID TLV
        Ifname: Ethernet4
Time to Live TLV
        120
Port Description TLV
        RATE-BAS-P005_P4P2
System Name TLV
        BAS-FIC-0H1E-12S-C02.picotrading.com
System Description TLV
        Arista Networks EOS version 4.16.7M running on an Arista Networks DCS-7150S-64-CL
System Capabilities TLV
        System capabilities:  Bridge, Router
        Enabled capabilities: Bridge, Router
Management Address TLV
        IPv4: 100.72.66.1
        Ifindex: 5000000
Port VLAN ID TLV
        PVID: 3001
Link Aggregation TLV
        Aggregation capable
        Currently not aggregated
        Aggregated Port ID: 0
Maximum Frame Size TLV
        9236
End of LLDPDU TLV

munged into
{'Maximum Frame Size': '9236', 'ifmac': {'hwaddr': '08:94:ef:31:c6:8c', 'up': True}, 'Link Aggregation': '0', 'nic': 'p3p2', 'Management Address': '100.72.66.5,Ifindex: 5000000', 'System Name': 'BAS-JPM-0H1E-12S-ML2.picotrading.com', 'Time to Live': '120', 'Port VLAN ID': '702', 'Port Description': 'RATE-BAS-P005_P3P2', 'System Capabilities': 'Bridge, Router,Enabled capabilities: Bridge, Router', 'Chassis ID': '28:99:3a:02:70:53', 'Port ID': 'Ethernet2', 'System Description': 'Arista Networks EOS version 4.16.7M running on an Arista Networks DCS-7010T-48'}

"""

# constants for easy manipulation
LLDP_MAPS = {
    'Port Description TLV': 'port_description',
    'System Name TLV': 'switch_name',
    'Port ID TLV': 'port_id',
    'Chassis ID TLV': 'port_mac',
    'Port VLAN ID TLV': 'port_vlan_id',
    'System Description TLV': 'switch_description'
    }

# try:
#     try:
#         import json
#     except ImportError:
#         import simplejson as json
# except ImportError:
#     print json.dumps({})

def get_interfaces(devpath="/sys/class/net", exclude="^(bond|lo|usb)[0-9]?"):
    """
    List network devices from *devpath*, excluding those matching the exclude pattern

    Kwargs:
        devpath: path to device dir ["/sys/class/net"]
        exclude: regex pattern (as str) of device names to exclude

    Returns:
        list
    """
    return [ d for d in os.listdir(devpath) if not re.match(exclude, d) ]

def enable_lldp(interface):
    """
    Enable LLDP neighbour queries on the chosen interface

    Args:
        interface(str): network interface device name

    Returns:
        bool (returncode is 0 or not)
    """
    cmdstr = 'lldptool  -T -i %s -V portDesc enableTx=yes' % interface
    devnull = open(os.devnull, 'w')
    rc = subprocess.call(cmdstr.split(), stdout=devnull)
    return rc == 0


def get_lldp(interface, keymapping=LLDP_MAPS):
    """
    Runs lldptool and parses output for the given interface

    Args:
        interface(str): network interface device name

    Kwargs:
        keymapping(dict): mapping of LLDP output keys to desired key names in results

    Returns:
        dict (switch name, switch port, switch mac, etc)
    """
    output = {}
    cmdstr = 'lldptool get-tlv -n -i %s' % interface
    proc = subprocess.Popen(cmdstr.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode == 0:
        for l in out.replace('\n\t', ',').splitlines():
            try:
                tlv, val = l.split(',', 1)
                if tlv in keymapping:
                    output[keymapping.get(tlv)] = val.split(':', 1)[-1].strip().lower()
            except ValueError:
                continue
        return output
    else:
        return None

def main():
    """
    Main script entry point
    """
    module = AnsibleModule(
        argument_spec = dict(
            devpath = dict(default="/sys/class/net"),
            ignore  = dict(default="^(bond|lo|usb)([0-9]+)?"),
            ))

    devpath = module.params['devpath']
    ignore = module.params['ignore']

    # dict to hold structured output
    results = {}
    # iterate over discovered interfaces
    for dev in get_interfaces(devpath, ignore):
        # ensure LLDP transmission is enabled
        # ansible will do this anyway
        # enable_lldp(dev)
        nicinfo = get_lldp(dev)
        if nicinfo is not None:
            results[dev] = nicinfo

    module.exit_json(changed=True, 
                     ansible_facts = {
                         'ansible_lldp': results
                         })

from ansible.module_utils.basic import AnsibleModule
if __name__ == "__main__":
    main()


