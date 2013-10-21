"""
Created on Feb 27, 2013

@author: deif

This script performs a sanity check for duplicated pinning definitions for
each file on the file system.

"""
import os
import re
import sys


EXP_SECTION = re.compile("\[versions\]\n([^\[]*)")
MSG_ERROR_EXP_SECTION = (
    "ERROR: file '%s' needs a [version] section")
EXP_PINNING = re.compile("([#\w\.-]+)[\s]*=[\s]*([\w\.]+)")
MSG_ERROR = ("ERROR: package '%s' has two or more pinnings: %s "
             "in file '%s'")
MSG_OK = 'all ok!'


def sanity_check(buf):
    """Sanity check contents of one kgs-file. Buf must be a file-like object.

    We don't use ConfigParser to read the file since it overwrites duplicate
    entries silently.

    """
    filepath = buf.name
    content = buf.read()
    packages = dict()
    duplicates = dict()
    match = EXP_SECTION.search(content)
    if not match:
        msg = MSG_ERROR_EXP_SECTION % (filepath)
        raise MissingSection(msg)

    version_pinnings = match.group(1)
    for package, version in EXP_PINNING.findall(version_pinnings):
        if package.startswith('#'):
            continue

        if package in packages:
            if not package in duplicates:
                duplicates[package] = [packages[package]]
            duplicates[package].append(version)
        else:
            packages[package] = version

    if duplicates:
        messages = []
        for package, duplicate_versions in duplicates.items():
            msg = MSG_ERROR % (package, ' and '.join(duplicate_versions),
                               filepath)
            messages.append(msg)
        raise Insane('\n'.join(messages))


def sanity_check_all():
    """Sanity check all kgs files on the filesystem.
    """

    my_dir = os.path.abspath(os.path.dirname(__file__))
    kgs_dir_path = os.path.join(my_dir, 'release')
    is_sane = True

    for root, _dirs, files in os.walk(kgs_dir_path):
        for each in files:
            try:
                filepath = os.path.join(root, each)
                sanity_check(open(filepath, 'r'))
            except Insane as e:
                print e.message
                is_sane = False

    return is_sane


class Insane(Exception):
    """Raised when a sanity check fails."""


class MissingSection(Exception):
    """Raised when an expected section is missing."""


if __name__ == "__main__":
    is_sane = sanity_check_all()
    if is_sane:
        print MSG_OK
        sys.exit(0)
    else:
        sys.exit(1)
