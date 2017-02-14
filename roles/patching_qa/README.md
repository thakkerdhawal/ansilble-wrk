README for patch qa module
==========================

This role compares the output of LLDPtool on a target host with its entries in a patching schedule spreadsheet (in CSV format)

Requirements
------------

1. Patching information for the servers being verified, in ansible vars format
2. lldptool available on the target servers

Functionality
-------------

1. Create custom fact script to report on current interface config
  * next hop (switch name)
  * switch port
  * default gateway

Much of this is in the standard ansible 'setup' module, but the LLDP parts
are not.
so this basically adds a dict like this:
ansible_local:
    lldp:
      <interface>:
        switch_name
        switch_port
        switch_mac

sample output:

    {
      "p4p2": {
        "port_description": "RATE-BAS-P005_P4P2",
        "port_id": "Ethernet4",
        "port_mac": "44:4c:a8:d6:f9:05",
        "switch_name": "BAS-FIC-0H1E-12S-C02.picotrading.com"
      },
      "p5p1": {},
      "p5p2": {},
      "p1p1": {},
      "p6p2": {},
      "p6p1": {
        "port_description": "RATE-BAS-P005_P6P1",
        "port_id": "Ethernet5",
        "port_mac": "44:4c:a8:d7:02:4d",
        "switch_name": "BAS-FIC-0H1E-11S-C01.picotrading.com"
      },
      "em1": {
        "port_description": "RATE-BAS-P005_EM1",
        "port_id": "Ethernet3",
        "port_mac": "28:99:3a:02:63:e1",
        "switch_name": "BAS-JPM-0H1E-11S-ML1.picotrading.com"
      },
      "p3p2": {
        "port_description": "RATE-BAS-P005_P3P2",
        "port_id": "Ethernet2",
        "port_mac": "28:99:3a:02:70:53",
        "switch_name": "BAS-JPM-0H1E-12S-ML2.picotrading.com"
      }
    }

2. Check that this matches the patching schedule
         

