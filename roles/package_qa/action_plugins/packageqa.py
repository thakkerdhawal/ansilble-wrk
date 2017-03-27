#!/usr/bin/env python
# package QA tool for ansible
from __future__ import print_function, division, absolute_import
__metaclass__ = type

"""
Compares installed RPM package lists between a master server and another

returns lists of 
1. Packages completely missing on the target (as compared to the master)
2. Packages that are of a different version to the master (older or newer)
"""
# assumes that you have run the 'listpackages' module to gather info for each host.
# although I could run that here, of course
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
# from ansible.module_utils._text import to_native
# from ansible.module_utils.pycompat24 import get_exception


# RPM filename shenanigans
from rpmUtils.miscutils import splitFilename, compareEVR

# file globbing
from fnmatch import fnmatch

def rpmqa_to_dict(pkglist):
    """
    Process an rpm -qa outputlist into a dict
    """
    return { "%s.%s" %(name, arch) : { 'name': name, 'epoch': epoch, 'version': ver, 'release': release, 'arch': arch  } for name, ver, release, epoch, arch in map(splitFilename, pkglist) }


def compare_pkgver(pkg1, pkg2):
    """
    compare 2 dicts representing packages (name, arch, epoch, version, release as keys)
    returns an appropriate symbol "<", "==" or ">"

    Args:
        pkg1: dict
        pkg2: dict

    Returns:
        int:
        -1 if pkg1 < pkg2
         0 if pkg1 = pkg2
         1 if pkg1 > pkg2
    """
    return compareEVR((pkg1['epoch'], pkg1['version'], pkg1['release']), (pkg2['epoch'], pkg2['version'], pkg2['release']))

def diff_packagelist(plist1, plist2, ignorepkgs=[], pkgfilter=[], ignore_missing=False):
    """
    Run a diff between 2 packagelists (lists of dicts representing packages),
    reporting on packages in plist2 that are
      * not in plist1 (in any version at all, this is name.arch comparison), unless "ignore_missing" is True
      * older than their equivalents in plist1
      * newer than their equivalents in plist1

    Args:
        plist1, plist2(dict): indexed dict of packages, name.arch: { name, version, arch etc... }

    Kwargs: 
        ignorepkgs(list): list of package name.arch patterns (fnmatch/shell wildcard) to ignore
        pkgfilter(list): list of package name.arch patterns (fnmatch/shell wildcard) to compare
        ignore_missing(bool): whether to report on packages that are missing/extra on the target host

    Returns:
        dict:
            name.arch: { 'desired' : NVR.A or "present" (if this is a missing package) - from list1
                         'actual' : NVR.A or "absent" (if this is n 'extra' package) - from list2
                         'status': OLDER|NEWER|MISSING|EXTRA|MATCH
                         'failed': True (False if 'MATCH' above)
                         }

    """
    status_maps = {
            -1 : "NEWER",
             0 : "MATCH",
             1 : "OLDER",
             }

    results = {}
    for pna in set(plist1).union(plist2):
        # the set of all available packages from both hosts
        p1 = plist1.get(pna, ["absent"]).pop(0)
        p2 = plist2.get(pna, ["missing"]).pop(0)

        # let's filter
        if any([fnmatch(pna, p) for p in ignorepkgs]):
            # this package matches one of our 'ignore me' patterns, skip it
            continue

        if len(pkgfilter) > 0 and  not any([fnmatch(pna, p) for p in pkgfilter]):
            # we've specified filters and this package doesn't match it
            continue

        # simple tests first:
        if p1 == "absent":
            if ignore_missing:
                continue
            results[pna] = { 
                "actual": "%(name)s-%(version)s-%(release)s.%(arch)s" % p2,
                "desired": "",
                "status": "EXTRA",
                "failed": True,
               }
            continue

        if p2 == "missing":
            if ignore_missing:
                continue
            results[pna] = {
                "actual": "",
                "desired": "%(name)s-%(version)s-%(release)s.%(arch)s" % p1,
                "status": "MISSING",
                "failed": True,
               }
            continue
        # package is present in both lists
        comp = compare_pkgver(p1, p2)
        results[pna] = {
            "actual": "%(name)s-%(version)s-%(release)s.%(arch)s" % p2,
            "desired": "%(name)s-%(version)s-%(release)s.%(arch)s" % p1,
            "status": status_maps.get(comp),
            "failed" : comp != 0,
            }

    return results

         

class ActionModule(ActionBase):
    TRANSFERS_FILES = False


    def run(self, tmp=None, task_vars=None):

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        print(result)

        # parameters we support
        # 'master' server - golden source
        master = self._task.args.get('master', None)
        # alternatively, an inputfile in NVR.A format, one per line
        inputfile = self._task.args.get('src', None)
        # only compare the latest version of packages
        latest = self._task.args.get('latest', False)
        # list of shell-style wildcards for packages to ignore
        ignorepkgs = self._task.args.get('exclude', [])
        # list of shell-style wildcards for packages to compare (restricts to this list)
        pkgfilter = self._task.args.get('filter', [])
        # do we care about completely missing packages?
        ignore_missing = self._task.args.get('ignore_missing', False)
        # diff only - don't show packages that are the same on both sides
        # essentially this should produce "fail" if there are any differences
        diff_only = self._task.args.get('diff_only', True)

        if master is None and inputfile is None:
            result['failed'] = True
            result['msg'] = "Either 'master' or 'src' is required"

        elif inputfile is not None:
            try:
                # find file to use as input, in our 'files' dir (or one of them)
                src = self._find_needle('files', inputfile)
                with open(src) as f:
                    masterpkgs = rpmqa_to_dict(f)
                   
            except AnsibleError, E:
                result['failed'] = True
                resuLt['msg'] = str(E)

        else:
            # master is not None, inputfile is None
            masterpkgs = task_vars['hostvars'][master].get('ansible_installed_rpms')

        if masterpkgs is None:
            # we need to run the fact gathering thingy, which is a custom module
            # we can't run this on another host when processing our current one.
            result['failed'] = True
            result['msg'] = "please ensure you have run the 'rpmpackagelist' module for your master server before this one"

        if 'ansible_installed_rpms' not in task_vars:
            print ("running remote module")
            mod_result = self._execute_module(module_name='rpmpackagelist', 
                                              module_args={'filter': pkgfilter, 'latest': latest },
                                              task_vars=task_vars, 
                                              tmp=tmp, 
                                              delete_remote_tmp=True)
            task_vars.update(mod_result['ansible_facts'])

        if 'failed' in result:
            return result



        comparison = diff_packagelist(masterpkgs, 
                                      task_vars['ansible_installed_rpms'], 
                                      ignorepkgs=ignorepkgs, 
                                      pkgfilter=pkgfilter, 
                                      ignore_missing=ignore_missing)
        if any([ p.get('failed', False) for p in comparison.values() ]):
            result['failed'] = True
        else:
            result['failed'] = False

        if diff_only:
            result['results'] = dict([(k, v) for k, v in comparison.iteritems() if v['failed'] ]) 
        else:
            result['results'] = comparison


        return result
