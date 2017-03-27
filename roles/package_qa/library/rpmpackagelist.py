#!/usr/bin/env python
import os
import sys
import rpm
from rpmUtils.miscutils import compareEVR
from fnmatch import fnmatch

def pkg_is_newer(pkg1, pkg2):
    """
    compares package dicts from get_packagelist to see if
    pkg1 > pkg2

    Args:
        pkg1, pkg2: dict representing a package header

    Returns:
        bool: True if pkg1 > pkg2,. False otherwise
    """
    # return values of compareEVR(pt1, pt2) are
    # 1 pt1 > pt2
    # 0 pt1 = pt2
    # -1 pt1 < pt2
    return compareEVR( 
            (pkg1['epoch'], pkg1['version'], pkg1['release']),
            (pkg2['epoch'], pkg2['version'], pkg2['release'])
            ) 
                       

def get_packagelist(latest=False, filter=None):
    """
    returns a list of packages in a dict form
    For multi-installed packages returns a list unless 'latest' is true
    """
    output = {}
    ts = rpm.TransactionSet()
    mi = ts.dbMatch()
    for h in mi:
        if filter is not None and not fnmatch(h[rpm.RPMTAG_NAME], filter):
            continue
        p = { 'name': h[rpm.RPMTAG_NAME],
              'epoch': h[rpm.RPMTAG_EPOCH] or '',
              'version': h[rpm.RPMTAG_VERSION],
              'release': h[rpm.RPMTAG_RELEASE],
              'arch': h[rpm.RPMTAG_ARCH],
              'installed': h[rpm.RPMTAG_INSTALLTIME],
              }

        label = '%(name)s.%(arch)s' % p

        if label not in output:
                output[label] = [ p ]
        else:
            # we already have this package
            # this will probably be kernels etc
            if latest:
                if pkg_is_newer(p, output[label][0]) > 0:
                    output[label] = [ p ]
                else:
                    continue
            else:
                output[label].append(p)
                output[label].sort(cmp=pkg_is_newer, reverse=True)

    return output


def main():
    module = AnsibleModule(
        argument_spec = dict(
            latest = dict(type='bool', default=False),
            filter = dict(type='str', required=False),
            )
        )

    pkglist = get_packagelist(latest=module.params['latest'], filter=module.params['filter'])

    module.exit_json(changed=True, ansible_facts={ 'ansible_installed_rpms': pkglist })


# from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import *

if __name__ == "__main__":
    main()



