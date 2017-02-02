#!/usr/bin/env python
# A python tool to process the server patching schedule
# Requires CSV-formatted input

# standard library modules
import sys
import os
from glob import glob
import csv
from optparse import OptionParser
try:
    import json
except ImportError:
    import simplejson as json

# other mods if needed
# to export in ansible vars format
import yaml

FIELDNAMES = [
    'switch',
    'switch_port',
    'hostname',
    'interface',
    'cable_type',
    'vlan',
    'bond'
    ]

def parse_cmdline(argv):
    """Process commandline options and arguments"""
    usg = "%prog [-h] [-o FORMAT] [--host HOST] CSVFILE"
    preamble = "Parses CSV for relevant patching info, returns JSON or YAML"
    parser = OptionParser(usage=usg, description=preamble)
    parser.add_option("-y", "--yaml", action="store_true", default=False, help="output YAML (for ansible vars files) rather than JSON (ansible dynamic inventory)")
    parser.add_option("-H", "--host", help="select hostname to extract from input file, must match exactly, not case sensitive though")
    parser.add_option("-l", "--list", action="store_true", default=False, help="list all groups, hosts and vars")

    opts, args = parser.parse_args(argv)

#     if len(args) != 1:
#         print "Error: please provide one CSV-format input file to parse"
#         parser.print_help()
#         sys.exit(1)
# 
#     if not os.path.exists(args[0]):
#         print "Error: file %s does not appear to exist" % args[0]
#         parser.print_help()
#         sys.exit(2)

    if len(args) == 0:
        args = glob('%s/*.csv' % os.path.dirname(os.path.abspath(__file__)))


    return opts, args

def parse_patch_schedule(inputdata, hostlimit=None, inventory_format=False):
    """
    Process a CSV-formatted patching schedule and convert it to a 
    """
    output = {}
    reader = csv.reader(inputdata)
    for line in reader:
        # skip the column header lines
        if line[0] == 'Device Name':
            continue
        try:
            sw, pi, hn, ni, ct, vl, bo = line
            host = hn.lower()
            if hostlimit is not None and host != hostlimit:
                continue
            nic = ni.lower()

            netinfo = { 'switch_name': sw,
                        'port_id': pi.replace('ET','Ethernet'),
                        'bond' : bo.lower()
                      }

            if host not in output:
                output[host] = { 'patching' : {nic: netinfo }}
            else:
                output[host]['patching'][nic] = netinfo
        # if there aren't enough entries to split the line, move on
        # this should skip blank lines and 
        except IndexError:
            continue
    if inventory_format:
        return {'_meta': {
                    'hostvars': output 
                    }
               }

    return output


def main():
    """main script funcionality"""

    opts, filelist = parse_cmdline(sys.argv[1:])

    output = {}

    for inputfile in filelist:
        try:
            output.update(parse_patch_schedule(open(inputfile), opts.host, inventory_format=opts.list))
        except IOError, OSError:
            continue


    if opts.yaml:
        print yaml.dump(output, default_flow_style=False)
    else:
        print json.dumps(output, indent=2)

if __name__ == "__main__":
    main()

