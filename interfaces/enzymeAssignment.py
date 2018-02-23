# -*- coding: utf-8 -*-

import abc
import collections
import re
import sys

ec_pattern = re.compile('\d+\.\d+\.\d+\.\d+')


class EnzymeAssignment(abc.ABC):
    """
    Abstract class for enzyme assignment stage
    Each subclass should provide a mechanism for assigning enzymes for a given input
    """
    def __init__(self):
        self._assigned_enzymes = AssignedEnzymeDict()

    @property
    def assigned_enzymes(self):
        """
        :getter: returns an AssignedEnzymeDict with enzyme numbers as the key, and a list of gene ids as the values
        :type: dictionary

        """
        return self._assigned_enzymes

    @abc.abstractmethod
    def get_name(self):
        """
        :return: The name of the Enzyme Assignment
        """
        pass

    @abc.abstractmethod
    def assign_enzymes(self):
        """
        Assign enzymes abstract method.
        All subclasses should use this method to do the enzyme assignment
        """
        pass


class AssignedEnzymeDict(collections.MutableMapping):
    """
    A dictionary designed to store enzyme numbers as keys, with gene ids as values
    """

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[self.enzyme_key(key)]

    def __setitem__(self, key, value):
        self.store[self.enzyme_key(key)] = self.gene_values(value)

    def __delitem__(self, key):
        del self.store[self.enzyme_key(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    @staticmethod
    def enzyme_key(key):
        """
        check that key is an enzyme number
        :param key:
        :return key:
        """
        try:
            assert re.match(ec_pattern, key)
            return key
        except AssertionError:
            print('Keys for the assigned_enzyme dict must be valid E.C. numbers')
            sys.exit()

    @staticmethod
    def gene_values(value):
        """
        check that values are in correct form
        :param value:
        :return:
        """
        try:
            assert bool(value) and isinstance(value, list) and all(isinstance(elem, str) for elem in value)
            return value
        except AssertionError:
            print('Values for the assigned_enzyme dict must be a list of strings')
            sys.exit()
