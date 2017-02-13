Ansible Inventory Directory
===========================

Ansible supports inventory directories now, meaning that it is possible to easily combine static and dynamic inventories.

http://docs.ansible.com/ansible/intro_dynamic_inventory.html#using-inventory-directories-and-multiple-inventory-sources

This permits us to use a static file (as in our current infra) and add dynamic inventories too, which can simply add varialbes.
This is used here to parse a patching schedule (in CSV format) and add new vars to the inventory on the fly

We control which files in this directory count as inventory files using an ansible.cfg setting:

    inventory_ignore_extensions = ~, .orig, .bak, .ini, .retry, .pyc, .pyo, .csv, .md


