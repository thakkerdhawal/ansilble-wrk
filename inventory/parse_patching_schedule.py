#!/usr/bin/env python
# A python tool to process the server patching schedule
# Requires CSV-formatted input
"""
This is an ansible inventory script, using CSV input files from
a patching schedule to add 
"""

# standard library modules
import sys
import os
from glob import glob
import csv
import re
from optparse import OptionParser
try:
    import json
except ImportError:
    import simplejson as json

# other mods if needed
# to export in ansible vars format
import yaml


def parse_cmdline(argv):
    """Process commandline options and arguments"""
    usg = "%prog [-h] [-o FORMAT] [--host HOST] CSVFILE"
    preamble = "Parses CSV for relevant patching info, returns JSON (for dynamic inventory) or YAML (for static versions)"
    parser = OptionParser(usage=usg, description=preamble)
    parser.add_option("-y", "--yaml", action="store_true", default=False, help="output YAML (for ansible vars files) rather than JSON (ansible dynamic inventory)")
    parser.add_option("-H", "--host", help="select hostname to extract from input file, must match exactly, not case sensitive though")
    parser.add_option("-l", "--list", action="store_true", default=False, help="list all groups, hosts and vars")

    opts, args = parser.parse_args(argv)

    if len(args) == 0:
        args = glob('%s/*.csv' % os.path.dirname(os.path.abspath(__file__)))

    return opts, args

def parse_patch_schedule(inputdata, hostlimit=None, inventory_format=False):
    """
    Process a CSV-formatted patching schedule and convert it to a dictionary
    like this:
    hostname : {
      patching : {
        nic : {
          switch_name: name,
          port_id: port,
          bond: bondingdev_name,
          vlan: VLAN label,
          }

    """
    output = {}
    reader = csv.reader(inputdata)
    for line in reader:
        if '-' not in line[0]:
            continue
        try:
            # split up the lines into fields
            # Excel has a peculariuty where it ends all exported lines with a comma, so
            # the lines won't ever work properly
            if len(line) == 8:
                sw, pi, hn, ni, ct, vl, bo = line[:-1]
            else:
                sw, pi, hn, ni, ct, vl, bo = line
            # JPM naming scheme, LOB-DC-
            if len(hn.split('-')) != 3:
                continue
            else:
                line_of_business, datacenter, hostid = hn.split('-')

            hostname = hn.lower()
            if hostlimit is not None and hostname != hostlimit:
                continue
            nic = ni.lower()

            netinfo = { 'switch_name': sw.lower(),
                        'port_id': pi.replace('ET','Ethernet').lower(),
                        'bond' : bo.lower(),
                        'vlan': vl,
                      }
            hostinfo = { 'lob_code': line_of_business,
                         'dc_name': datacenter,
                         'env_name': 'production' if hostid.startswith('P') else 'development',
                         'patch_schedule': {
                             nic: netinfo,
                             }
                         }

            if hostname not in output:
                output[hostname] = hostinfo
            else:
                output[hostname]['patch_schedule'][nic] = netinfo

        # if there aren't enough entries to split the line, move on
        # this should skip blank lines and 
        except IndexError:
            continue
        except ValueError:
            continue
        except:
            raise
    if hostlimit is not None:
        if hostlimit in output:
            return output[hostlimit]
        else:
            return {}

    return output

def csviter(filename, separator=',', fieldcount=7):
    """
    iterate over the lines in our CSV files, compressing empty fields that are not at the end of the line
    (to handle the empty fields in the BAS patching schedule workbook)

    Args:
        filename(str): file, probably in 

    """
    try:
        for line in open(filename):
            yield re.sub(r'%s+(?!$)' % separator, r'%s' % separator, line)
    except (IOError, OSError):
        return

def main():
    """main script funcionality"""

    opts, filelist = parse_cmdline(sys.argv[1:])

    output = {}

    for inputfile in filelist:
        try:
            output.update(parse_patch_schedule(csviter(inputfile), opts.host, inventory_format=opts.list))
        except IOError, OSError:
            continue

    # ansible calls the inventory with a --list option, we want to return all host info at once so it's cached
    if opts.list:
        output = {
                    '_meta': {
                        'hostvars': output 
                        }
                    }

    # support yaml output too if necessary
    # one large file for the time being, though.
    if opts.yaml:
        print yaml.dump(output, default_flow_style=False)
    else:
        print json.dumps(output, indent=2)

if __name__ == "__main__":
    main()

