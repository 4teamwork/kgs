"""
Created on Feb 25, 2013

@author: deif

This script generates pinning files on the file system from google app engine
exported csv files.

For the google app-engine data bulkloader/exporter see:
https://svn.4teamwork.ch/repos/ftwkgs/good-py/trunk

"""
from dataloader import load_data
import os


def generate_files(system_versions):
    """Write data to pinning files.
    """

    kgs_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'kgs')
    for each in system_versions.values():
        filepath = os.path.join(kgs_dir, each.rel_path)
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        kgs_file = open(filepath, 'w')
        kgs_file.write(each.render())
        kgs_file.close()


if __name__ == '__main__':
    generate_files(load_data())
