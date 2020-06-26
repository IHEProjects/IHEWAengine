# -*- coding: utf-8 -*-
"""
"""


def same_keys(list_of_dictionaries):
    """
    Check if different dictionaries have the same keys.

    Parameters
    ----------
    list_of_dictionaries : list
        List containing the dictionaries to check.
    """
    length1 = len(list_of_dictionaries[0].keys())
    keys1 = list_of_dictionaries[0].keys()
    for dictionary in list_of_dictionaries[1:]:
        assert len(dictionary.keys()) == length1, "The length of the provided dictionaries do not match"
        assert np.all(np.sort(dictionary.keys()) == np.sort(keys1)), "The keys in the provided dictionaries do not match"
