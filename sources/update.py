#!/usr/bin/env update


import os
from ConfigParser import ConfigParser


BASEPATH = os.path.abspath(os.path.dirname(__file__))


PREFIX = '''# DO NOT MODIFY
# This file is auto generated, use the update script!

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
    sorted(map(lambda name: output.set('branches',
                                       name.split('/')[-1], 'master'),
               reduce(list.__add__, repos.values())))


def write_sources(repos, output):
    for name in repos['gitolite']:
        shortname = name.split('/')[-1]

        output.set(
            'sources', shortname,
            'git gitolite@git.4teamwork.ch:%s.git'
            ' branch=${branches:%s}' % (
                name, shortname))

    for name in repos['github_private']:
        output.set(
            'sources', name,
            'git git@github.com:4teamwork/%s.git'
            ' branch=${branches:%s}' % (
                name, name))


config = get_config()
output = ConfigParser()
output.add_section('buildout')
output.set('buildout', 'extends', 'http://plonesource.org/sources.cfg')

# copy branches and sources sections
output.add_section('branches')
for key, value in config.items('branches'):
    output.set('branches', key, value)

output.add_section('sources')
for key, value in config.items('sources'):
    output.set('sources', key, value)

repos = get_repos()
branches = write_branches(repos, output)
sources = write_sources(repos, output)

with open(os.path.join(BASEPATH, 'sources.cfg'), 'w+') as file_:
    file_.write(PREFIX)
    output.write(file_)

print 'UPDATED'
