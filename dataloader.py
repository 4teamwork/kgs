"""
Created on Feb 27, 2013

@author: deif
"""
from csv import DictReader
import model
import os


def load_data():
    """Load data from csv.
    """

    systems = _load('system.csv', model.System)
    system_versions = _load('systemversion.csv', model.SystemVersion,
                            systems=systems)
    _load('knowngood.csv', model.KnownGood, system_versions=system_versions)
    for each in system_versions.values():
        each.resolve(system_versions)
    return system_versions


def _load(filename, class_, **kwargs):
    """Load objects from a .csv file and return a dict.
    """

    my_dir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(my_dir, 'data', filename)
    reader = DictReader(open(filepath, 'r'))
    result = dict()
    for row in reader:
        instance = class_(row, **kwargs)
        result[instance.key] = instance
    return result
