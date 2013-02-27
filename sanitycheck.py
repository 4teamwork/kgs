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
ERROR_MSG = ("ERROR: package '%s' has two or more pinnings: %s "
             "in file '%s'")


def _sanity_check(buf, filepath):
    """Sanity check contents of one kgs-file.
    """

    packages = dict()
    duplicates = dict()
    is_sane = True
    match = EXP_SECTION.search(buf)
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
            print ERROR_MSG % (package, ' and '.join(duplicate_versions),
                               filepath)
    return is_sane


def sanity_check_all():
    """Sanity check all kgs files on the filesystem.
    """

    my_dir = os.path.abspath(os.path.dirname(__file__))
    kgs_dir_path = os.path.join(my_dir, 'kgs')
    is_sane = True
    for root, _dirs, files in os.walk(kgs_dir_path):
        for each in files:
            filepath = os.path.join(root, each)
            is_sane = _sanity_check(open(filepath, 'r').read(), filepath)
    return is_sane


if __name__ == "__main__":
    is_sane = sanity_check_all()
    if not is_sane:
        sys.exit(0)
    else:
        sys.exit(1)
