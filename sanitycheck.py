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
EXP_PINNING = re.compile("([\w\.]+)[\s]*=[\s]*([\w\.]+)")
MSG_ERROR = ("ERROR: package '%s' has two or more pinnings: %s "
             "in file '%s'")
MSG_OK = 'all ok!'


def _sanity_check(buf):
    """Sanity check contents of one kgs-file.
    """

    filepath = buf.name
    content = buf.read()
    packages = dict()
    duplicates = dict()
    is_sane = True
    match = EXP_SECTION.search(content)
    if not match:
        return

    version_pinnings = match.group(1)
    for package, version in EXP_PINNING.findall(version_pinnings):
        if package in packages:
            if not package in duplicates:
                duplicates[package] = [packages[package]]
            duplicates[package].append(version)
        else:
            packages[package] = version

    if duplicates:
        is_sane = False
        for package, duplicate_versions in duplicates.items():
            print MSG_ERROR % (package, ' and '.join(duplicate_versions),
                               filepath)
    return is_sane


def sanity_check_all():
    """Sanity check all kgs files on the filesystem.
    """

    my_dir = os.path.abspath(os.path.dirname(__file__))
    kgs_dir_path = os.path.join(my_dir, 'release')
    is_sane = True
    for root, _dirs, files in os.walk(kgs_dir_path):
        for each in files:
            filepath = os.path.join(root, each)
            is_sane = is_sane and _sanity_check(open(filepath, 'r'))
    return is_sane


if __name__ == "__main__":
    is_sane = sanity_check_all()
    if is_sane:
        print MSG_OK
        sys.exit(0)
    else:
        sys.exit(1)
