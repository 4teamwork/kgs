#!/usr/bin/env python


import os
from ConfigParser import ConfigParser


BASEPATH = os.path.abspath(os.path.dirname(__file__))


PREFIX = '''# DO NOT MODIFY
# This file is auto generated, use the update script!

[buildout]
extends = http://plonesource.org/sources.cfg
'''


def get_config():
    parser = ConfigParser()

    with open(os.path.join(BASEPATH, 'config.ini')) as file_:
        parser.readfp(file_)

    return parser


def get_repos():
    config = get_config()
    return dict(map(lambda item: (item[0], item[1].strip().split()),
                    config.items('repos')))


def write_branches(repos, output):
    for name in reduce(list.__add__, repos.values()):
        shortname = name.split('/')[-1]
        output['branches'][shortname] = 'master'


def write_forks(repos, output):
    for name in repos['github_private']:
        output['forks'][name] = '4teamwork'


def write_sources(repos, output):
    for name in repos['gitlab']:
        shortname = name.split('/')[-1]

        output['sources'][shortname] = \
            'git git@git.4teamwork.ch:%s.git  branch=${branches:%s}' % (
            name, shortname)

    for name in repos['github_private']:
        output['sources'][name] = \
            'git ${buildout:github-cloneurl}' \
            '${forks:%(name)s}/%(name)s.git' \
            ' pushurl=${buildout:github-pushurl}' \
            '${forks:%(name)s}/%(name)s.git' \
            ' branch=${branches:%(name)s}' % {'name': name}


def write_output(data, file_):
    for section in sorted(data):
        file_.write('\n')
        file_.write('\n')
        file_.write('[%s]\n' % section)

        for key, value in sorted(data[section].items()):
            file_.write('%s = %s\n' % (key, value))



config = get_config()
output = {'branches': dict(config.items('branches')),
          'forks': {},
          'sources': dict(config.items('sources'))}

repos = get_repos()
write_branches(repos, output)
write_forks(repos, output)
write_sources(repos, output)

with open(os.path.join(BASEPATH, 'sources.cfg'), 'w+') as file_:
    file_.write(PREFIX)
    write_output(output, file_)

print 'UPDATED'
