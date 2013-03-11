"""
Created on Feb 27, 2013

@author: deif

This script performs a migration sanity check on the migrated files.

"""
from ConfigParser import SafeConfigParser
from StringIO import StringIO
from dataloader import load_data
from pprint import pprint
import urllib2
from urlparse import urlsplit


class BuildoutConfigReader(object):
    """Read buildout config files from buffers.
    """

    def __init__(self, buf):
        self._mainconfig_string = buf

    @property
    def mainconfig(self):
        """Return file-like mainconfig.
        """

        return StringIO(buf=self._mainconfig_string)

    def get_config(self):
        files = self.get_ordered_extend_files()
        files.reverse()
        return self.load_config_files(files)

    def load_config_files(self, files):
        parser = SafeConfigParser()
        for path in files:
            parser.readfp(path)
        return parser

    def get_ordered_extend_files(self):
        configfiles = []
        self.get_extends_recursive(configfiles, self.mainconfig)
        return configfiles

    def get_extends_recursive(self, configfiles, buf):
        parser = SafeConfigParser()
        file_content = buf.read()
        parser.readfp(StringIO(buf=file_content))
        configfiles.append(StringIO(buf=file_content))

        if parser.has_option('buildout', 'extends'):
            extend_files = reversed(parser.get('buildout', 'extends').split())
            for url in extend_files:
                assert url.startswith('http')
                self.get_extends_recursive(configfiles,
                                           self._get_file_contents(url))

    def _get_file_contents(self, url):
        """ Download url an return response file-like object.
        """

        request = urllib2.Request(url)
        return urllib2.urlopen(request)


class LocalBuildoutConfigReader(BuildoutConfigReader):
    """Read buildout config files only from local data if possible.
    """

    def __init__(self, buf, system_versions):
        super(LocalBuildoutConfigReader, self).__init__(buf)
        self.system_versions = system_versions

    def _get_file_contents(self, url):
        """Extract package and version from url and try the local data storage
        first before falling back to downloading data over the web.

        """

        _scheme, _netloc, path, _query, _fragment = urlsplit(url)
        paths = path.split('/')
        version = paths[-1]
        package = paths[-2]

        system_version = self.system_versions.get((package, version))
        if system_version:
            return StringIO(buf=system_version.render())
        else:
            return super(LocalBuildoutConfigReader, self)\
                                                       ._get_file_contents(url)


def check_migration(system_versions):
    """Check that pinnings are not changed by the migration.
    """

    for each in system_versions.values():
        print "checking: %s" % each
        local_parser = LocalBuildoutConfigReader(each.render(),
                                                 system_versions).get_config()
        local_pinnings = set(local_parser.items('versions'))

        try:
            response = urllib2.urlopen(urllib2.Request(each.app_engine_url))
        except urllib2.HTTPError:
            print "skipping bugged version %s" % each.kgs_url
            continue

        web_parser = BuildoutConfigReader(response.read()).get_config()
        web_pinnings = set(web_parser.items('versions'))

        difference = local_pinnings.difference(web_pinnings)
        if difference:
            print 30 * '-'
            print 'difference for %s:' % each
            pprint(difference)
            print 30 * '-'

        missing = web_pinnings.difference(local_pinnings)
        if missing:
            print 30 * '-'
            print 'missing for %s:' % each
            pprint(missing)
            print 30 * '-'

    print 'done'


if __name__ == "__main__":
    check_migration(load_data())

