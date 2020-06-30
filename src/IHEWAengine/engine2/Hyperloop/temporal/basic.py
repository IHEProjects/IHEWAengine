# -*- coding: utf-8 -*-
"""
"""

# Builtins
from __future__ import print_function
from builtins import range

import os
from dateutil.relativedelta import relativedelta
# Math
import numpy as np


def find_possible_dates(str_):
    """
    Finds index of possible year and month in a string if the date is of format
    yyyymm or yyyy{char}mm for years between 1900 and 2020
    """
    basename = os.path.basename(str_)
    months = ['{0:02d}'.format(i) for i in range(1, 12)]
    years = ['{0}'.format(i) for i in range(1900, 2020)]
    options = {}
    i = 0
    for y in years:
        index = basename.find(y)
        if index > 0:
            if basename[index + 4:index + 6] in months:
                options[i] = ([index, index + 4], [index + 4, index + 6])
                i += 1
            elif basename[index + 5:index + 7] in months:
                options[i] = ([index, index + 4], [index + 5, index + 7])
                i += 1
            else:
                options[i] = [index, index + 4]
    if len(list(options.keys())) == 0:
        print('Could not find datestring')
    elif len(list(options.keys())) > 1:
        print('Multiple possible locations for datestring')

    return options[0]


def find_possible_dates_negative(str_):
    """
    Finds index of possible year and month in a string if the date is of format
    yyyymm or yyyy{char}mm for years between 1900 and 2020
    """
    basename = os.path.basename(str_)
    months = ['{0:02d}'.format(i) for i in range(1, 12)]
    # years = ['{0}'.format(i) for i in range(1900, 2020)]
    years = ['{0}'.format(i) for i in range(1900, 2099)]

    options = {}
    i = 0
    for y in years:
        index1 = basename.find(y)
        index = index1 - len(basename)
        if index1 > 0:
            if basename[index + 4:index + 6] in months:
                options[i] = ([index, index + 4], [index + 4, index + 6])
                i += 1
            elif basename[index + 5:index + 7] in months:
                options[i] = ([index, index + 4], [index + 5, index + 7])
                i += 1
            else:
                options[i] = [index, index + 4]

    if len(list(options.keys())) == 0:
        print('Could not find datestring')
    elif len(list(options.keys())) > 1:
        print('Multiple possible locations for datestring')

    return options[0]


def common_dates(dates_list):
    """
    Checks for common dates between multiple lists of datetime.date objects.

    Parameters
    ----------
    dates_list : list
        Contains lists with datetime.date objects.

    Returns
    -------
    com_dates : ndarray
        Array with datetime.date objects for common dates.
    """
    com_dates = dates_list[0]
    for date_list in dates_list[1:]:
        com_dates = np.sort(list(set(com_dates).intersection(date_list)))
    return com_dates


def assert_missing_dates(dates, timescale='months', quantity=1):
    """
    Checks if a list of dates is continuous, i.e. are there temporal gaps in the dates.

    Parameters
    ----------
    dates : ndarray
        Array of datetime.date objects.
    timescale : str, optional
        Timescale to look for, default is 'months'.
    """
    current_date = dates[0]
    enddate = dates[-1]

    if timescale == 'months':
        while current_date <= enddate:
            assert current_date in dates, "{0} is missing in the dataset".format(current_date)

            current_date = current_date + relativedelta(months=quantity)
