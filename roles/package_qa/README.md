Role Name
=========

Perform package name and version QA, comparing either a master server (considered to have the correct packages installed) or a filename containing a list of name-version-release.arch packages, gleaned from the output of `rpm -qa --qf '%{name}-%{version}-%{release}.%{arch}\n'`

Requirements
------------

Python RPM plugins on the target servers (should be there by default)

Role Variables
--------------

| Name | Type | Default Value | Description |
|------|------|---------------|-------------|
| `package_qa_latest_only` | bool | no (false) | Only gather (and compare) the latest versions of packages between servers |
| `package_qa_filter` | list | [] (empty list) | Restrict package comparison to these wildcard patterns |
| `package_qa_exclude`| list | [] (empty list) | Exclude these wilcard patterns from comparison. |
| `package_qa_source` | str | null (not defined) | source filename for packages list (in NVR.A format) |
| `package_qa_master` | str | null (not defined) | source hostname - gather 'golden' package list from here |
| `package_qa_ignoremissing` | bool | yes (true) | ignore packages that are missing from either side|



Dependencies
------------

None

Example Playbook
----------------

    - hosts: servers
      roles:
         - role: package_qa
           package_qa_master: somehost.example.com
           package_qa_latest_only: yes
           package_qa_filter:
             - bash*
             - httpd*

Output
------
The provided packageqa action plugin produces output in the following format for consumption by callbacks, once written:

    {
      "xz.x86_64": {
        "actual": "xz-5.2.2-1.el7.x86_64",
        "desired": "xz-5.1.2-12alpha.el7.x86_64",
        "failed": true,
        "status": "NEWER" (or OLDER|MATCH|MISSING|EXTRA)
        }


License
-------

GPL or Pico Internal.

Author Information
------------------

Stuart Sears <stuart.sears@pico.global>
