# -*- coding: utf-8 -*-
"""
"""
import numpy as np


def split_Yield(pfraction, etbfraction, a, b):
    """
    Calculate fractions to split Yield into Yield_precip and Yield _irri.

    Parameters
    ----------
    pfraction : ndarray
        Array of Precipitation devided by np.nanmax(P)
    etbfraction : ndarray
        Array of fraction of ETblue of total ET.
    a : float
        Parameter to define the fraction.
    b : float
        Parameter to define the fraction.

    Returns
    -------
    fraction : ndarray
        Array of the fraction.
    """
    fraction = -(((etbfraction - 1) * a) ** 2 - ((pfraction - 1) * b) ** 2) + 0.5
    fraction = np.where(fraction > 1.0, 1.0, fraction)
    fraction = np.where(fraction < 0.0, 0.0, fraction)
    return fraction
