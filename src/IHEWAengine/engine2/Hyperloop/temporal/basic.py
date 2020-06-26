# -*- coding: utf-8 -*-
"""
"""


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
