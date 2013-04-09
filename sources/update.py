#!/usr/bin/env update


import os
from ConfigParser import ConfigParser


BASEPATH = os.path.abspath(os.path.dirname(__file__))


TEMPLATE = '''# DO NOT MODIFY
# This file is auto generated, use the update script!

[buildout]
extends = http://plonesource.org/sources.cfg

[branches]
%(branches)s

[sources]
%(sources)s
'''


def get_repos():
    parser = ConfigParser()

    with open(os.path.join(BASEPATH, 'config.ini')) as file_:
        parser.readfp(file_)

    return dict(map(lambda item: (item[0], item[1].strip().split()),
                    parser.items('repos')))


def get_branches(repos):
    lines = sorted(map(lambda name: '%s = master' % name.split('/')[-1],
                       reduce(list.__add__, repos.values())))
    return '\n'.join(lines)


def get_sources(repos):
    lines = []

    for name in repos['gitolite']:
        shortname = name.split('/')[-1]
        lines.append('%s = git gitolite@git.4teamwork.ch:%s.git'
                     ' branch=${branches:%s}' % (
                shortname, name, shortname))

    for name in repos['github_private']:
        lines.append(
            '%s = git git@github.com:4teamwork/%s.git'
            ' branch=${branches:%s}' % (
                name, name, name))

    return '\n'.join(sorted(lines))


repos = get_repos()
branches = get_branches(repos)
sources = get_sources(repos)

with open(os.path.join(BASEPATH, 'sources.cfg'), 'w+') as file_:
    file_.write(TEMPLATE % {
            'branches': branches,
            'sources': sources})

print 'UPDATED'
