# -*- coding: utf-8 -*-
"""
"""
# Builtins
from builtins import zip
import os
import glob
import shutil
import tempfile as tf
import datetime
import calendar
# Math
import numpy as np
import pandas as pd

# Self
try:
    from .. import general
    from .. import spatial
    from .. import temporal
except ImportError:
    from IHEWAengine.engine2.Hyperloop import general
    from IHEWAengine.engine2.Hyperloop import spatial
    from IHEWAengine.engine2.Hyperloop import temporal


def sum_ts(flow_csvs):
    flows = list()
    dates = list()

    for cv in flow_csvs:
        coordinates, flow_ts, station_name, unit = general.pairwise_validation.create_dict_entry(cv)

        # print(flow_ts)
        flow_dates, flow_values = list(zip(*flow_ts))
        flow_dates = temporal.converter.datetime_to_date(flow_dates)

        if unit == 'm3/s':
            flow_values = np.array([flow_values[flow_dates == date] * 60 * 60 * 24 * calendar.monthrange(date.year, date.month)[1] / 1000 ** 3 for date in flow_dates])[:, 0]

        flows.append(flow_values)
        dates.append(flow_dates)

    common_dates = temporal.basic.common_dates(dates)

    data = np.zeros(np.shape(common_dates))
    for flow_values, flow_dates in zip(flows, dates):
        add_data = np.array([np.array(flow_values)[flow_dates == date][0] for date in common_dates])

        data += add_data

    return data, common_dates


def get_transfers(sheet5_csv_folder):
    csv_files = glob.glob(sheet5_csv_folder + '\\sheet5_*.csv')

    transfer_data = []
    transfer_date = []
    for f in csv_files:
        fn = os.path.split(f)[1]

        year = int(fn.split('sheet5_')[1].split('.csv')[0][:4])
        month = int(fn.split('sheet5_')[1].split('.csv')[0][-2:])
        date = datetime.date(year, month, 1)

        df = pd.read_csv(f, sep=';')
        df_basin = df.loc[df.SUBBASIN == 'basin']
        df_tran = df_basin.loc[df_basin.VARIABLE == 'Interbasin Transfer'].VALUE

        if float(df_tran) > 0:
            transfer_data.append(-float(df_tran))
        else:
            transfer_data.append(0)

        transfer_date.append(date)

    return transfer_data, transfer_date


def get_ts(all_results, key):
    """
    Subtract a array with values from a list containing multiple dictionaries.

    Parameters
    ----------
    all_results : list
        List of dictionaries.
    key : str
        Key to be extracted out of the dictionaries.

    Returns
    -------
    ts : ndarray
        Array with the extracted values.
    """
    ts = np.array([dct[key] for dct in all_results])
    return ts


def calc_ETs(ET, lu_fh, sheet1_lucs):
    """
    Calculates the sums of the values within a specified landuse category.

    Parameters
    ----------
    ET : ndarray
        Array of the data for which the sum needs to be calculated.
    lu_fh : str
        Filehandle pointing to landusemap.
    sheet1_lucs : dict
        Dictionary with landuseclasses per category.

    Returns
    -------
    et : dict
        Dictionary with the totals per landuse category.
    """
    LULC = spatial.basic.open_as_array(lu_fh, nan_values=True)
    et = dict()
    for key in sheet1_lucs:
        classes = sheet1_lucs[key]

        mask = np.logical_or.reduce([LULC == value for value in classes])

        et[key] = np.nansum(ET[mask])

    return et


def calc_utilizedflow(incremental_et, other, non_recoverable, other_fractions, non_recoverable_fractions):
    """
    Calculate the utilized flows per landuse category from total incremental ET, non_recoverable water and other.

    Parameters
    ----------
    incremental_et : dict
        Incremental ET per landuse category (i.e. Protected, Utilized, Modified and Managed).
    other : dict
        Other water consumptions per landuse category (i.e. Protected, Utilized, Modified and Managed).
    non_recoverable : dict
        Non recoverable water consumption per landuse category (i.e. Protected, Utilized, Modified and Managed).
    other_fractions : dict
        Fractions describing how much of other water consumption should be assigned to each category.
    non_recoverable_fractions : dict
        Fractions describing how much of non_recoverable water consumption should be assigned to each category.

    Returns
    -------
    uf_plu : float
        Utilized Flow for Protected LU.
    uf_ulu : float
        Utilized Flow for Utilized LU.
    uf_mlu : float
        Utilized Flow for Modified LU.
    uf_mwu : float
        Utilized Flow for Managed Water Use.
    """
    assert np.sum(list(
        other_fractions.values())) == 1.00, "Fractions for other should sum to 1.00."
    assert np.sum(list(
        non_recoverable_fractions.values())) == 1.00, "Fractions for non_recoverable should sum to 1.00."

    np.array(list(incremental_et.values())) + np.array(
        list(other_fractions.values())) * other + np.array(
        list(non_recoverable_fractions.values())) * non_recoverable

    uf_plu = incremental_et['Protected'] + other_fractions['Protected'] * other + non_recoverable_fractions['Protected'] * non_recoverable
    uf_ulu = incremental_et['Utilized'] + other_fractions['Utilized'] * other + non_recoverable_fractions['Utilized'] * non_recoverable
    uf_mlu = incremental_et['Modified'] + other_fractions['Modified'] * other + non_recoverable_fractions['Modified'] * non_recoverable
    uf_mwu = incremental_et['Managed'] + other_fractions['Managed'] * other + non_recoverable_fractions['Managed'] * non_recoverable

    return uf_plu, uf_ulu, uf_mlu, uf_mwu


def calc_wb(P, ET, q_outflow, recycling_ratio, q_in_sw=0, q_in_gw=0, q_in_desal=0, q_out_sw=0, q_out_gw=0):
    """
    Calculate the water balance given the relevant terms.

    Parameters
    ----------
    P : ndarray
        Array with the precipitation in volume per pixel.
    ET : ndarray
        Array with the evapotranspiration in volume per pixel.
    q_outflow : float
        Outflow volume.
    recycling_ratio : float
        Value indicating the recycling ratio.
    q_in_sw : float, optional
        Surfacewater inflow into the basin. Default is 0.0.
    q_in_gw : float, optional
        Groundwater inflow into the basin. Default is 0.0.
    q_in_desal : float, optional
        Desalinised water inflow into the basin. Default is 0.0.
    q_out_sw : float, optional
        Additional surfacewater outflow from basin. Default is 0.0.
    q_out_gw : float, optional
        Groundwater outflow from the basin. Default is 0.0.

    Returns
    -------
    et_advection : float
        The volume of ET advected out of the basin.
    p_advection : float
        The volume of precipitation advected into the basin.
    p_recycled : float
        The volume of ET recycled as P within the basin.
    dS : float
        The change in storage.
    """
    et_advection = (1 - recycling_ratio) * np.nansum(ET)

    p_total = np.nansum(P)

    p_recycled = min(recycling_ratio * np.nansum(ET), p_total)

    et_advection = np.nansum(ET) - p_recycled

    p_advection = p_total - p_recycled

    dS = q_outflow + et_advection + q_out_sw + q_out_gw - p_advection - q_in_sw - q_in_gw - q_in_desal

    return et_advection, p_advection, p_recycled, dS


def calc_non_utilizable(P, ET, fractions_fh):
    """
    Calculate non utilizable outflow.

    Parameters
    ----------
    P : ndarray
        Array with the volumes of precipitation per pixel.
    ET : ndarray
        Array with the volumes of evapotranspiration per pixel.
    fractions_fh : str
        Filehandle pointing to a map with fractions indicating how much of the
        (P-ET) difference is non-utilizable.

    Returns
    -------
    non_utilizable_runoff : float
        The total volume of non_utilizable runoff.
    """
    fractions = spatial.basic.open_as_array(fractions_fh, nan_values=True)

    non_utilizable_runoff = np.nansum((P - ET) * fractions)

    return non_utilizable_runoff


def calc_basinmean(perc_fh, lu_fh):
    """
    Calculate the mean of a map after masking out the areas outside an basin defined by
    its landusemap.

    Parameters
    ----------
    perc_fh : str
        Filehandle pointing to the map for which the mean needs to be determined.
    lu_fh : str
        Filehandle pointing to landusemap.

    Returns
    -------
    percentage : float
        The mean of the map within the border of the lu_fh.
    """
    output_folder = tf.mkdtemp()

    perc_fh = spatial.basic.match_proj_res_ndv(lu_fh, np.array([perc_fh]), output_folder)

    EWR = spatial.basic.open_as_array(perc_fh[0], nan_values=True)
    LULC = spatial.basic.open_as_array(lu_fh, nan_values=True)

    EWR[np.isnan(LULC)] = np.nan

    percentage = np.nanmean(EWR)

    shutil.rmtree(output_folder)
    return percentage
