"""
Created on Feb 25, 2013

@author: deif
"""
import os
import re
import urllib


class System(object):
    """A system is a collection of packages.
    """

    def __init__(self, row):
        self.name = row['name']

    def __repr__(self):
        return 'System(name="%s")' % (self.name)

    @property
    def key(self):
        return self.name


class SystemVersion(object):
    """A version of a system. Packages are recorded against a particular
    version.
    """

    def __init__(self, row, systems):
        self.system = systems[row['parent_name']]
        self.name = row['name']
        self.parent = None
        self.extends = []
        self.pinnings = []
        exp = re.compile("datastore_types.Key.from_path\("
                         "u'System', u'sys_([\w\.]*)', u'SystemVersion', "
                         "u'ver_([\w\.]*)', _app=u'ftwkgs'\)")
        self._extends = exp.findall(row['extends'])

    def resolve(self, system_versions):
        """Resolve parent and extended SystemVersions.
        """

        for key in self._extends:
            extends = system_versions[key]
            if extends.system.name == self.system.name:
                assert self.parent is None, 'only one parent is expected'
                self.parent = extends
            else:
                self.extends.append(extends)

    def __str__(self):
        return "%s:%s" % (self.system.name, self.name)

    def __repr__(self):
        return 'SystemVersion(system="%s", name="%s")' % (self.system.name,
                                                          self.name)

    def render(self):
        """Render the configuration file for this SystemVersion.
        """

        lines = []
        self.append_header_lines(lines)
        self.append_buildout_section_lines(lines)
        self.append_version_section_lines(lines)
        return '\n'.join(lines)

    def append_version_section_lines(self, lines):
        lines.append('[versions]')
        self.append_version_lines(lines, set())

    def append_header_lines(self, lines):
        lines.append("# Known good set for %s version %s" % (self.system.name,
                     self.name))
        lines.append("# The latest version can be found at %s" % self.kgs_url)
        lines.append('')

    def append_buildout_section_lines(self, lines):
        if self.extends:
            lines.append('[buildout]')
            for index, each in enumerate(self.extends):
                if index == 0:
                    prefix = 'extends = '
                else:
                    prefix = 10 * ' '
                lines.append(prefix + each.kgs_url)
            lines.append('')

    def append_version_lines(self, lines, skip):
        lines.append('# %s' % self.kgs_url)
        new_pinnings = []
        for each in self.pinnings:
            if not each.package in skip:
                skip.add(each.package)
                new_pinnings.append(str(each))
        lines.extend(sorted(new_pinnings))
        if self.parent:
            lines.append('')
            self.parent.append_version_lines(lines, skip)

    def add_pinning(self, pinning):
        self.pinnings.append(pinning)

    @property
    def key(self):
        """Return the key for this SystemVersion.
        """

        return (self.system.name, self.name)

    @property
    def kgs_url(self):
        """Return the URL where this SystemVersion is available.
        """

        sys_name = urllib.quote(self.system.name)
        name = urllib.quote(self.name)
        return "http://kgs.4teamwork.ch/release/%s/%s" % (sys_name, name)

    @property
    def rel_path(self):
        """Return the relative path to this SystemVersion's file.
        """

        return os.path.join(self.system.name, self.name)


class KnownGood(object):
    """A Known Good pinning for a package consisting of package name and
    version
    """

    def __init__(self, row, system_versions):
        self.system, self.name = row['system_version'].split(':')
        self._parent_key = (self.system, self.name)
        self.system_version = system_versions[self._parent_key]
        self.system_version.add_pinning(self)
        self.version = row['version']
        self.package = row['package']

    def __str__(self):
        return "%s = %s" % (self.package, self.version)

    def __repr__(self):
        return ('KnownGood(system="%s", name="%s", '
                'package="%s", version="%s")' % (self.system,
                                                 self.name,
                                                 self.package,
                                                 self.version))

    @property
    def key(self):
        return self._parent_key + (self.package, self.version)

