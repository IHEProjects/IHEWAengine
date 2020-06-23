# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 13:28:17 2017

@author: bec
"""
# Builtins
from __future__ import print_function

from builtins import zip
from builtins import str
from builtins import range

import os
import glob
import warnings
import subprocess
import datetime
from shutil import copyfile

import csv
# Math
import numpy as np
# GIS
import netCDF4

try:
    import gdal
    import osr
except ImportError:
    from osgeo import gdal, osr
# Plot
import matplotlib.pyplot as plt

# Self
try:
    from . import becgis
    from . import find_possible_dates
except ImportError:
    from IHEWAengine.engine2.Hyperloop import becgis
    from IHEWAengine.engine2.Hyperloop import find_possible_dates


def create_csv_yearly(input_folder, output_folder, sheetnb,
                      start_month, year_position=[-11, -7], month_position=[-6, -4],
                      header_rows=1, header_columns=1, minus_header_colums=None):
    """
    Calculate yearly csvs from monthly csvs for complete years (i.e. with 12 months of data available).

    Parameters
    ----------
    input_folder : str
        Folder containing monthly csv-files.
    output_folder : str
        Folder to store the yearly csv-files.
    year_position : list, optional
        The indices where the year is positioned in the filenames. Default connects to
        the filenames generated by create_sheet4_csv.
    month_position : list, optional
        The indices where the month is positioned in the filenames. Default connects to
        the filenames generated by create_sheet4_csv.
    header_rows : int
        The number of fixed rows at the top of the csv without any numerical data.
    header_columns : int
        The number of fixed columns at the left side of the csv without any numerical data.

    Returns
    -------
    output_fhs : ndarray
        Array with filehandles pointing to the generated yearly csv-files.
    """
    fhs, dates = becgis.sort_files(input_folder, year_position, month_position=month_position, extension='csv')[0:2]

    water_dates = np.copy(dates)
    for w in water_dates:
        if w.month < start_month:
            water_dates[water_dates == w] = datetime.date(w.year - 1, w.month, w.day)

    years, years_counts = np.unique([date.year for date in water_dates], return_counts=True)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    reader = csv.reader(open(fhs[0], 'r'), delimiter=';')
    template = np.array(list(reader))
    shape = np.shape(template)

    output_fhs = np.array([])

    data = list()
    for date in water_dates:
        if date.year in years[years_counts == 12]:

            reader = csv.reader(open(fhs[water_dates == date][0], 'r'), delimiter=';')
            data.append(np.array(list(reader))[header_rows:, header_columns:minus_header_colums].astype(np.float))

            if len(data) == 12:
                data_stack = np.stack(data)
                yearly_data = np.sum(data_stack, axis=0)
                data = list()
                template[header_rows:, header_columns:minus_header_colums] = yearly_data.astype(np.str)

                fh = os.path.join(output_folder, 'sheet_{1}_{0}.csv'.format(date.year, sheetnb))
                csv_file = open(fh, 'w')
                writer = csv.writer(csv_file, delimiter=';', lineterminator='\n')

                for row_index in range(shape[0]):
                    writer.writerow(template[row_index, :])
                output_fhs = np.append(output_fhs, fh)
                csv_file.close()

    return output_fhs


def diagnosis_wp(data_meta, complete_data, dir_output, waterpix):
    dir_output = os.path.join(dir_output)
    if not os.path.exists(dir_output):
        os.makedirs(dir_output)

    LU = becgis.open_as_array(data_meta['lu'], nan_values=True)

    #    S = SortWaterPix(waterpix, 'Supply_M', dir_output)
    #    becgis.match_proj_res_ndv(data_meta['lu'], becgis.list_files_in_folder(S), os.path.join(dir_output, "s_matched"))
    #    complete_data['supply'] = becgis.sort_files(os.path.join(dir_output, "s_matched"), [-10,-6], month_position = [-6,-4])[0:2]

    common_dates = becgis.common_dates(
        [complete_data['p'][1], complete_data['et'][1], complete_data['tr'][1], complete_data['etb'][1]])

    becgis.assert_proj_res_ndv(
        [complete_data['p'][0], complete_data['et'][0], complete_data['tr'][0]])

    balance_km3 = np.array([])

    p_km3 = np.array([])
    et_km3 = np.array([])
    ro_km3 = np.array([])

    balance_mm = np.array([])

    p_mm = np.array([])
    et_mm = np.array([])
    ro_mm = np.array([])

    area = becgis.map_pixel_area_km(data_meta['lu'])

    for date in common_dates:
        print(date)

        P = complete_data['p'][0][complete_data['p'][1] == date][0]
        ET = complete_data['et'][0][complete_data['et'][1] == date][0]
        RO = complete_data['tr'][0][complete_data['tr'][1] == date][0]

        factor = 0.001 * 0.001 * area

        p = becgis.open_as_array(P, nan_values=True)
        et = becgis.open_as_array(ET, nan_values=True)
        ro = becgis.open_as_array(RO, nan_values=True)

        p[np.isnan(LU)] = et[np.isnan(LU)] = ro[np.isnan(LU)] = np.nan

        balance_km3 = np.append(balance_km3, np.nansum(p * factor) - np.nansum(et * factor) - np.nansum(ro * factor))

        p_km3 = np.append(p_km3, np.nansum(p * factor))
        et_km3 = np.append(et_km3, np.nansum(et * factor))
        ro_km3 = np.append(ro_km3, np.nansum(ro * factor))

        balance_mm = np.append(balance_mm, np.nanmean(p) - np.nanmean(et) - np.nanmean(ro))

        p_mm = np.append(p_mm, np.nanmean(p))
        et_mm = np.append(et_mm, np.nanmean(et))
        ro_mm = np.append(ro_mm, np.nanmean(ro))

    relative_storage = np.cumsum(balance_km3) / np.mean(p_km3)

    ##
    # BASIC BASINSCALE WATERBALANCE (PRE-SHEETS)
    ##
    fig = plt.figure(1, figsize=(9, 6))
    plt.clf()
    fig.patch.set_alpha(0.7)

    ax2 = plt.gca()
    ax = ax2.twinx()

    ax2.bar(common_dates, relative_storage, width=25, color='#3ee871')
    ax2.grid(b=True, which='Major', color='0.65', linestyle='--', zorder=0)

    ax.bar([common_dates[0]], [0], label='$\sum dS / \overline{P}$', color='#3ee871')
    ax.plot(common_dates, np.cumsum(balance_km3), label='$\sum dS$')
    ax.plot(common_dates, np.cumsum(p_km3), label='$\sum (P)$')
    ax.plot(common_dates, np.cumsum(et_km3) + np.cumsum(ro_km3), label='$\sum (ET + RO)$')

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
    ax2.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=5)

    plt.suptitle('$\sum P = {0:.1f}\;{4}, \\ \sum ET = {1:.1f}\;{4}, \sum RO = {2:.1f}\;{4}, \sum dS = {3:.1f}\;{4}$'.format(
        np.sum(p_km3), np.sum(et_km3), np.sum(ro_km3), np.sum(balance_km3), r"km^{3}"))
    plt.title('{0}, ${5} = {2:.3f}\;{6}, {7} = {3:.3f}, dt = {4}\;months$'.format(
        data_meta['name'], np.sum(balance_km3), np.mean(balance_km3), np.mean(relative_storage), len(p_km3), r"\overline{dS}", r"km^{3}", r"\overline{\sum dS / \overline{P}}"))
    plt.xlabel('Time')

    ax2.set_ylabel('Relative Storage [months of $\overline{P}$]')
    ax.set_ylabel('Stock [$km^{3}$]')
    # plt.savefig(os.path.join(dir_output, 'balance_{0}'.format(data_meta['name'])))

    fig = plt.figure(2)
    plt.clf()

    ax2 = plt.gca()
    ax = ax2.twinx()

    ax2.plot(common_dates, p_mm, common_dates, et_mm, common_dates, ro_mm)
    ax.plot(common_dates, np.cumsum(balance_mm), 'k')


# def diagnosis(data_meta, complete_data, dir_output, all_results, waterpix):
#
#    dir_output = os.path.join(dir_output, data_meta['name'], "diagnosis")
#    if not os.path.exists(dir_output):
#        os.makedirs(dir_output)
#
#    S = SortWaterPix(waterpix, 'Supply_M', dir_output)
#    becgis.match_proj_res_ndv(data_meta['lu'], becgis.list_files_in_folder(S), os.path.join(dir_output, "s_matched"))
#    complete_data['supply'] = becgis.sort_files(os.path.join(dir_output, "s_matched"), [-10,-6], month_position = [-6,-4])[0:2]
#
#    LU = becgis.open_as_array(data_meta['lu'], nan_values = True)
#
#    common_dates = becgis.common_dates([complete_data['p'][1],complete_data['et'][1],complete_data['tr'][1], complete_data['etb'][1]])
#
#    becgis.assert_proj_res_ndv([complete_data['p'][0],complete_data['et'][0],complete_data['tr'][0]])
#
#    balance = np.array([])
#    balance2 = np.array([])
#
#    p_y = np.array([])
#    et_y = np.array([])
#    ro_y = np.array([])
#    bf_y = np.array([])
#    supply_y = np.array([])
#
#    ds_y = np.array([])
#
#    area = becgis.map_pixel_area_km(data_meta['lu'])
#
#    for date in common_dates:
#
#        P = complete_data['p'][0][complete_data['p'][1] == date][0]
#        ET = complete_data['et'][0][complete_data['et'][1] == date][0]
#        RO = complete_data['tr'][0][complete_data['tr'][1] == date][0]
#        BF = complete_data['bf'][0][complete_data['bf'][1] == date][0]
#        DS = complete_data['ds'][0][complete_data['ds'][1] == date][0]
#        supply = complete_data['supply'][0][complete_data['supply'][1] == date][0]
#
#        p = becgis.open_as_array(P, nan_values = True) * 0.001 * 0.001 * area
#        et = becgis.open_as_array(ET, nan_values = True) * 0.001 * 0.001 * area
#        ro = becgis.open_as_array(RO, nan_values = True) * 0.001 * 0.001 * area
#        bf = becgis.open_as_array(BF, nan_values = True) * 0.001 * 0.001 * area
#        ds = becgis.open_as_array(DS, nan_values = True) * 0.001 * 0.001 * area
#        supply = becgis.open_as_array(supply, nan_values = True) * 0.001 * 0.001 * area
#
#        p[np.isnan(LU)] = et[np.isnan(LU)] = ro[np.isnan(LU)] = bf[np.isnan(LU)] = ds[np.isnan(LU)] = supply[np.isnan(LU)] =  np.nan
#
#        balance = np.append(balance, np.nansum(p) - np.nansum(et) - np.nansum(ro))
#        balance2 = np.append(balance2, np.nansum(p) + np.nansum(supply) - np.nansum(et) - np.nansum(ro) - np.nansum(bf))
#
#        p_y = np.append(p_y, np.nansum(p))
#        et_y = np.append(et_y, np.nansum(et))
#        ro_y = np.append(ro_y, np.nansum(ro))
#        bf_y = np.append(bf_y, np.nansum(bf))
#        ds_y = np.append(ds_y, np.nansum(ds))
#        supply_y = np.append(supply_y, np.nansum(supply))
#
#    ###
#    # CHECK ET
#    ###
#    plt.figure(2)
#    plt.clf()
#    et = sh1.get_ts(all_results, 'et_advection') + sh1.get_ts(all_results, 'p_recycled')
#    plt.scatter(et_y, et)
#    plt.xlabel('ETens [km3/month]')
#    plt.ylabel('Sheet1 [km3/month]')
#    nash = pwv.nash_sutcliffe(et_y, et)
#    plt.title('EVAPO, NS = {0}'.format(nash))
#    plt.savefig(os.path.join(dir_output, "CHECK_ET.jpg"))
#
#    ##
#    #CHECK P
#    ##
#    plt.figure(3)
#    plt.clf()
#    p = sh1.get_ts(all_results, 'p_advection') + sh1.get_ts(all_results, 'p_recycled')
#    plt.scatter(p_y, p)
#    plt.xlabel('CHIRPS [km3/month]')
#    plt.ylabel('Sheet1 [km3/month]')
#    nash = pwv.nash_sutcliffe(p_y, p)
#    plt.title('PRECIPITATION, NS = {0}'.format(nash))
#    plt.savefig(os.path.join(dir_output, "CHECK_P.jpg"))
#
#    ##
#    # CHECK Q
#    ##
#    #correction = calc_missing_runoff_fractions(data_meta)['full']
#    plt.figure(4)
#    plt.clf()
#
#     q = sh1.get_ts(all_results, 'q_out_sw') - \
#         sh1.get_ts(all_results, 'q_in_sw') + \
#         sh1.get_ts(all_results, 'q_out_gw') - \
#         sh1.get_ts(all_results, 'q_in_gw') + \
#         sh1.get_ts(all_results, 'q_outflow') - \
#         sh1.get_ts(all_results, 'q_in_desal')
#
#    plt.scatter(ro_y, q, label = 'original')
#    #plt.scatter(ro_y * correction, q, label = 'corrected')
#    plt.legend()
#    plt.xlabel('Waterpix_runoff [km3/month]')
#    plt.ylabel('Sheet1 [km3/month]')
#    nash = pwv.nash_sutcliffe(ro_y, q)
#    #nash2 = pwv.nash_sutcliffe(ro_y * correction, q)
#    plt.title('RUNOFF, NS = {0}'.format(nash))
#    plt.savefig(os.path.join(dir_output, "CHECK_Q.jpg"))
#
#    ###
#    # CHECK dS
#    ###
#    plt.figure(5)
#    plt.clf()
#    ds = sh1.get_ts(all_results, 'dS')
#    plt.scatter(balance, ds * -1)
#    plt.xlabel('CHIRPS, ETens, WPrunoff [km3/month]')
#    plt.ylabel('Sheet1')
#    nash = pwv.nash_sutcliffe(balance, ds * -1)
#    plt.title('dS, NS = {0}'.format(nash))
#    plt.savefig(os.path.join(dir_output, "CHECK_dS.jpg"))
#
#    ###
#    # CHECK WATERBALANCE (POST-SHEET1)
#    ###
#    balance_sheet1 = p - et - q
#    plt.figure(6)
#    plt.clf()
#
#    plt.plot(common_dates, np.cumsum(balance), label = 'dS [CHIRPS, ETens, WPro]')
#    plt.plot(common_dates, np.cumsum(balance_sheet1), label = 'dS [P(sh1), ET(sh1) + Q(sh1)]')
#    plt.plot(common_dates, np.cumsum(ds) * -1, label = 'dS [sh1]')
#
#    plt.plot(common_dates, np.cumsum(p_y), label = 'CHIRPS')
#    plt.plot(common_dates, np.cumsum(p), label = 'P [sh1]')
#
#    plt.plot(common_dates, np.cumsum(et_y) + np.cumsum(ro_y), label = 'ETens + WPro')
#    plt.plot(common_dates, np.cumsum(et) + np.cumsum(q), label = 'ET [sh1] + Q [sh1]')
#
#    plt.legend()
#    plt.xlabel('Months')
#    plt.ylabel('Flux [km3/month]')
#    plt.savefig(os.path.join(dir_output, "CHECK_WB.jpg"))

def scale_factor(scale_test):
    scale = 0
    while np.all([scale_test < 10.000, scale_test != 0.0]):
        scale_test *= 10
        scale += 1
    scale = float(np.min([2, scale]))
    return scale


def prepareSurfWatLoop(data, data_global):
    data_needed = ["etref_folder", "et_folder", "p_folder"]

    data_dst = {"etref_folder": r"ETref\Monthly",
                "et_folder": r"Evaporation\ETensV1_0",
                "p_folder": r"Precipitation\CHIRPS\Monthly"}

    for data_name in data_needed:
        print(data_name)
        files, dates = becgis.sort_files(data[data_name], [-10, -6], month_position=[-6, -4])[0:2]

        for f, d in zip(files, dates):

            fp = os.path.split(f)[1]

            dst = os.path.join(os.environ["WA_HOME"], 'Loop_SW', data_dst[data_name], fp[:-4] + "_monthly_{0}.{1}.01.tif".format(d.year, str(d.month).zfill(2)))

            folder = os.path.split(dst)[0]

            if not os.path.exists(folder):
                os.makedirs(folder)

            copyfile(f, dst)

    pt = os.path.join(os.environ["WA_HOME"], 'Loop_SW', 'HydroSHED', 'DIR')

    if not os.path.exists(pt):
        os.makedirs(pt)

    copyfile(data_global['dir'], os.path.join(pt, "DIR_HydroShed_-_15s.tif"))


# def LoopSurfWat(waterpix, data_meta, data_global, big_basins = None):
#
#    dst = os.path.join(os.environ["WA_HOME"], "LU", "Loop_SW.tif")
#    if os.path.exists(dst):
#        os.remove(dst)
#
#    copyfile(data_meta['full_basin_mask'], dst)
#
#    Basin = 'Loop_SW'
#
#    P_Product = 'CHIRPS'
#    ET_Product = 'ETensV1_0'
#    Inflow_Text_Files = []
#    Reservoirs_GEE_on_off = 0
#    Supply_method = "Fraction"
#    ID = data_meta['id']
#
#    pt = os.path.join(os.environ["WA_HOME"], 'Loop_SW', 'HydroSHED', 'DEM')
#    pt2 = os.path.join(os.environ["WA_HOME"], 'Loop_SW', 'HydroSHED', 'DIR')
#
#    if os.path.exists(os.path.join(pt, "DEM_HydroShed_m_15s.tif")):
#        os.remove(os.path.join(pt, "DEM_HydroShed_m_15s.tif"))
#    if os.path.exists(os.path.join(pt2, "DIR_HydroShed_-_15s.tif")):
#        os.remove(os.path.join(pt2, "DIR_HydroShed_-_15s.tif"))
#
#    start = str(netCDF4.Dataset(waterpix).variables["time_yyyymm"][:][0])
#    end = str(netCDF4.Dataset(waterpix).variables["time_yyyymm"][:][-1])
#
#    Startdate = "{0}-{1}-01".format(start[0:4], start[4:6])
#    Enddate = "{0}-{1}-31".format(end[0:4], end[4:6])
#
#    print Startdate, Enddate
#
#    if ID in big_basins:
#
#        surfwater_path = list()
#
#        years = range(int(Startdate[0:4]), int(Enddate[0:4])+1)
#
#        ID = ID * 100
#
#        for year in years:
#
#            ID += 1
#            Startdate = "{0}-01-01".format(year)
#            Enddate = "{0}-12-31".format(year)
#
#            filename = os.path.join(os.environ["WA_HOME"],
#                                    "Loop_SW",
#                                    "Simulations",
#                                    "Simulation_{0}".format(ID),
#                                    "Sheet_5",
#                                    "Discharge_CR1_Simulation{0}_monthly_"
#                                    "m3_01{1}_12{1}.nc".format(ID, int(year)))
#
#            if not os.path.exists(filename):
#                Sheet5.Calculate(Basin,
#                                 P_Product,
#                                 ET_Product,
#                                 Inflow_Text_Files,
#                                 waterpix,
#                                 Reservoirs_GEE_on_off,
#                                 Supply_method,
#                                 Startdate,
#                                 Enddate,
#                                 ID)
#                os.remove(os.path.join(pt, "DEM_HydroShed_m_15s.tif"))
#                os.remove(os.path.join(pt2, "DIR_HydroShed_-_15s.tif"))
#
#            else:
#                pass
#
#            surfwater_path.append(filename)
#
#    else:
#
#        surfwater_path = os.path.join(os.environ["WA_HOME"], "Loop_SW", "Simulations", "Simulation_{0}".format(ID), "Sheet_5", "Discharge_CR1_Simulation{0}_monthly_m3_012003_122014.nc".format(ID))
#
#        if not os.path.exists(surfwater_path):
#            Sheet5.Calculate(Basin,
#                             P_Product,
#                             ET_Product,
#                             Inflow_Text_Files,
#                             waterpix,
#                             Reservoirs_GEE_on_off,
#                             Supply_method,
#                             Startdate,
#                             Enddate,
#                             ID)
#            os.remove(os.path.join(pt, "DEM_HydroShed_m_15s.tif"))
#            os.remove(os.path.join(pt2, "DIR_HydroShed_-_15s.tif"))
#        else:
#            pass
#
#
#    return surfwater_path

def sort_data_short(dir_output, data_meta):
    data = ['p', 'et', 'n', 'ndm', 'lai', 'etref', 'etb', 'etg', 'i', 't', 'r', 'bf', 'sr', 'tr', 'perc', 'dperc', 'supply_total', 'dro']
    complete_data = dict()
    for datatype in data:
        try:
            folder = os.path.join(dir_output, data_meta['name'], 'data', datatype)
            for fn in glob.glob(folder + "\\*_km3.tif"):
                os.remove(fn)
            if datatype in ['ETblueWP', 'ETgreenWP']:
                files, dates = becgis.sort_files(folder, [-8, -4])[0:2]
            else:
                files, dates = becgis.sort_files(folder, [-10, -6], month_position=[-6, -4])[0:2]
            complete_data[datatype] = (files, dates)
        except BaseException:
            # traceback.print_exc()
            print(datatype)
            continue

    data_2dict = {'supply_sw': 'supply_sw',
                  'supply_gw': 'supply_gw',
                  'return_gwsw': 'return_flow_gw_sw',
                  'return_swsw': 'return_flow_sw_sw',
                  'return_gwgw': 'return_flow_gw_gw',
                  'return_swgw': 'return_flow_sw_gw',
                  r'fractions\fractions': 'fractions'
                  }

    for datatype in list(data_2dict.keys()):
        try:
            folder = os.path.join(dir_output, data_meta['name'], 'data', datatype)
            for fn in glob.glob(folder + "\\*_km3.tif"):
                os.remove(fn)
            files, dates = becgis.sort_files(folder, [-11, -7], month_position=[-6, -4])[0:2]
            complete_data[data_2dict[datatype]] = (files, dates)
        except BaseException:
            # traceback.print_exc()
            print(datatype)
            continue

    return complete_data


def sort_data(data_maps, data_meta, data_global, dir_output):
    dir_output = os.path.join(dir_output, data_meta['name'])
    if not os.path.exists(dir_output):
        os.makedirs(dir_output)

    complete_data = dict()
    for key in list(data_maps.keys()):
        complete_data = sort_var(data_maps, data_meta, data_global, dir_output, key, complete_data)

    # complete_data['fractions'] = sh5.calc_fractions(complete_data['p'][0],
    #                                                 complete_data['p'][1],
    #                                                 os.path.join(dir_output, 'data_maps', 'fractions'),
    #                                                 data_global['dem'], data_meta['lu'])
    #
    # i_files, i_dates, t_files, t_dates = sh2.splitET_ITE(complete_data['et'][0],
    #                                                      complete_data['et'][1],
    #                                                      complete_data['lai'][0],
    #                                                      complete_data['lai'][1],
    #                                                      complete_data['p'][0],
    #                                                      complete_data['p'][1],
    #                                                      complete_data['n'][0],
    #                                                      complete_data['n'][1],
    #                                                      complete_data['ndm'][0],
    #                                                      complete_data['ndm'][1],
    #                                                      os.path.join(dir_output, 'data_maps'),
    #                                                      ndm_max_original=False,
    #                                                      plot_graph=False, save_e=False)
    #
    # complete_data['i'] = (i_files, i_dates)
    # complete_data['t'] = (t_files, t_dates)

    if np.all(['etb_folder' in list(data_maps.keys()), 'etg_folder' in list(data_maps.keys())]):
        complete_data = sort_var(data_maps, data_meta, data_global, dir_output, 'etb_folder', complete_data)

        complete_data = sort_var(data_maps, data_meta, data_global, dir_output, 'etg_folder', complete_data)

        # else:
        #     gb_cats, mvg_avg_len = gd.get_bluegreen_classes(version='1.0')
        #     etblue_files, etblue_dates, \
        #     etgreen_files, etgreen_dates = sh3.splitET_BlueGreen(
        #         complete_data['et'][0],
        #         complete_data['et'][1],
        #         complete_data['etref'][0],
        #         complete_data['etref'][1],
        #         complete_data['p'][0],
        #         complete_data['p'][1],
        #         data_meta['lu'],
        #         os.path.join(dir_output, 'data_maps'),
        #         moving_avg_length=mvg_avg_len,
        #         green_blue_categories=gb_cats,
        #         plot_graph=False,
        #         method='tail', scale=1.1, basin=data_meta['name'])
        #
        #     complete_data['etb'] = (etblue_files, etblue_dates)
        #     complete_data['etg'] = (etgreen_files, etgreen_dates)

    return complete_data


def WP_NetCDF_to_Rasters(input_nc, ras_variable, root_dir,
                         time_var='time_yyyymm'):
    ds = netCDF4.Dataset(input_nc)
    time = ds.variables[time_var][:]

    out_dir = os.path.join(root_dir, ras_variable)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for i, t in enumerate(time):
        i += 1

        out_fh = os.path.join(out_dir, '{0}_{1}.tif'.format(ras_variable, t))
        in_fh = r'NETCDF:"{0}":{1}'.format(input_nc, ras_variable)

        string = 'gdal_translate -a_srs epsg:4326 ' \
                 '-b {0} -of GTiff {1} {2}'.format(i, in_fh, out_fh)

        proc = subprocess.Popen(string, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()

    return out_dir


# def sort_var(data_maps, data_meta, data_global, dir_output, key, complete_data,
#              time_var='time_yyyymm'):
#     print
#     key
#     if time_var == 'time_yyyymm':
#         try:
#             files, dates = becgis.sort_files(data_maps[key], [-10, -6],
#                                              month_position=[-6, -4])[0:2]
#         except:
#             files, dates = becgis.sort_files(data_maps[key], [-14, -10],
#                                              month_position=[-9, -7])[0:2]
#     else:
#         files, dates = becgis.sort_files(data_maps[key], [-8, -4])[0:2]
#     var_name = key.split('_folder')[0]
#     files = becgis.match_proj_res_ndv(data_meta['lu'], files,
#                                       os.path.join(dir_output, 'data_maps', var_name),
#                                       resample='near', dtype='float32')
#     complete_data[var_name] = (files, dates)
#     return complete_data


def sort_var(data_maps, data_meta, data_global, dir_output, key, complete_data, time_var='time_yyyymm'):
    print('{:>24s}: "{}"'.format(key, data_maps[key]))

    str_template = glob.glob(os.path.join(data_maps[key], '*.tif'))[0]
    (year_pos, month_pos) = find_possible_dates.find_possible_dates_negative(str_template)

    if time_var == 'time_yyyymm':
        files, dates = becgis.sort_files(data_maps[key], year_pos, month_position=month_pos)[0:2]
    else:
        files, dates = becgis.sort_files(data_maps[key], year_pos)[0:2]

    var_name = key.split('_folder')[0]

    files = becgis.match_proj_res_ndv(data_meta['lu'], files, os.path.join(dir_output, 'data_maps', var_name), dtype='Float32')

    complete_data[var_name] = (files, dates)
    return complete_data


def Spatial_Reference(epsg, return_string=True):
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    if return_string:
        return srs.ExportToWkt()
    else:
        return srs


def gdaltype_from_dtype(d_type):
    # gdal field type
    if 'int8' == d_type.name:
        gdal_data_type = 1
    elif 'uint16' == d_type.name:
        gdal_data_type = 2
    elif 'int16' == d_type.name:
        gdal_data_type = 3
    elif 'uint32' == d_type.name:
        gdal_data_type = 4
    elif 'int32' == d_type.name:
        gdal_data_type = 5
    elif 'float32' == d_type.name:
        gdal_data_type = 6
    elif 'float64' == d_type.name:
        gdal_data_type = 7
    elif 'bool' in d_type.name:
        gdal_data_type = 1
    elif 'int' in d_type.name:
        gdal_data_type = 5
    elif 'float' in d_type.name:
        gdal_data_type = 7
    elif 'complex' == d_type.name:
        gdal_data_type = 11
    else:
        warnings.warn('"{0}" is not recognized. '
                      '"Unknown" data type used'.format(d_type))
        gdal_data_type = 0
    return gdal_data_type


def NetCDF_to_Raster(input_nc, output_tiff, ras_variable,
                     x_variable='longitude', y_variable='latitude',
                     crs={'variable': 'crs', 'wkt': 'crs_wkt'}, time=None):
    # Input
    inp_nc = netCDF4.Dataset(input_nc, 'r')
    inp_values = inp_nc.variables[ras_variable]
    x_index = inp_values.dimensions.index(x_variable)
    y_index = inp_values.dimensions.index(y_variable)

    if not time:
        inp_array = inp_values[:]
    else:
        time_variable = time['variable']
        time_value = time['value']
        t_index = inp_values.dimensions.index(time_variable)
        time_index = list(inp_nc.variables[time_variable][:]).index(time_value)
        if t_index == 0:
            inp_array = inp_values[time_index, :, :]
        elif t_index == 1:
            inp_array = inp_values[:, time_index, :]
        elif t_index == 2:
            inp_array = inp_values[:, :, time_index]
        else:
            raise Exception("The array has more dimensions than expected")

    # Transpose array if necessary
    if y_index > x_index:
        inp_array = np.transpose(inp_array)

    # Additional parameters
    gdal_datatype = gdaltype_from_dtype(inp_array.dtype)
    # NoData_value = 9.96920996839e+36 # inp_nc.variables[ras_variable]._FillValue

    if type(crs) == str:
        srs_wkt = crs
    else:
        crs_variable = crs['variable']
        crs_wkt = crs['wkt']
        exec('srs_wkt = str(inp_nc.variables["{0}"].{1})'.format(crs_variable, crs_wkt))

    inp_x = inp_nc.variables[x_variable]
    inp_y = inp_nc.variables[y_variable]

    cellsize_x = abs(np.mean([inp_x[i] - inp_x[i - 1] for i in range(1, len(inp_x))]))
    cellsize_y = -abs(np.mean([inp_y[i] - inp_y[i - 1] for i in range(1, len(inp_y))]))

    # Output
    out_driver = gdal.GetDriverByName('GTiff')

    if os.path.exists(output_tiff):
        out_driver.Delete(output_tiff)

    y_ncells, x_ncells = inp_array.shape

    out_source = out_driver.Create(output_tiff, x_ncells, y_ncells, 1, gdal_datatype)
    out_band = out_source.GetRasterBand(1)
    # out_band.SetNoDataValue(pd.np.asscalar(NoData_value))

    out_top_left_x = inp_x[0] - cellsize_x / 2.0
    if inp_y[-1] > inp_y[0]:
        out_top_left_y = inp_y[-1] - cellsize_y / 2.0
        inp_array = np.flipud(inp_array)
    else:
        out_top_left_y = inp_y[0] - cellsize_y / 2.0

    out_source.SetGeoTransform((out_top_left_x, cellsize_x, 0,
                                out_top_left_y, 0, cellsize_y))
    out_source.SetProjection(srs_wkt)
    out_band.WriteArray(inp_array)
    out_band.ComputeStatistics(True)

    # Save and/or close the data sources
    inp_nc.close()
    out_source = None

    # Return
    return output_tiff


def SortWaterPix(nc, variable, output_folder, time_var='time_yyyymm'):
    spa_ref = Spatial_Reference(4326)
    nc1 = netCDF4.Dataset(nc)
    time = nc1.variables[time_var][:]
    for time_value in time:
        dir_output = os.path.join(output_folder, variable)
        output_tif = os.path.join(dir_output, "{0}_{1}.tif".format(variable, time_value))
        if not os.path.exists(dir_output):
            os.makedirs(dir_output)
        NetCDF_to_Raster(input_nc=nc,
                         output_tiff=output_tif,
                         ras_variable=variable,
                         x_variable='longitude', y_variable='latitude',
                         crs=spa_ref,
                         time={'variable': time_var, 'value': time_value})
    return dir_output

# def calc_missing_runoff_fractions(data_meta):
#
#    ID = data_meta['id']
#    accum = r"D:\WA_HOME\Loop_SW\Simulations\Simulation_{0}\Sheet_5\Acc_Pixels_CR_Simulation{0}_.nc".format(ID)
#
#    outlets = r"D:\project_ADB\subproject_Catchment_Map\outlets\Basins_outlets_basin_{0}.shp".format(ID)
#    inlets = r"D:\project_ADB\subproject_Catchment_Map\inlets\Basins_inlets_basin_{0}.shp".format(ID)
#
#    basin_mask = r"D:\WA_HOME\Loop_SW\Simulations\Simulation_{0}\Sheet_5\Basin_CR_Simulation{0}_.nc".format(ID)
#
#    sb_vector = r"D:/project_ADB/subproject_Catchment_Map/Basins_large/Subbasins_dissolved/dissolved_ID{0}.shp".format(ID)
#
#    dico_in = data_meta['dico_in']
#    dico_out =  data_meta['dico_out']
#
#    output_fh =  r"C:\Users\bec\Desktop\03_test\empty.tif"
#
#    geo_out, epsg, size_X, size_Y, size_Z, Time = RC.Open_nc_info(basin_mask)
#
#    LA.Save_as_tiff(output_fh, np.zeros((size_Y, size_X)), geo_out, epsg)
#
#    string = "gdal_rasterize -a Subbasins {0} {1}".format(sb_vector, output_fh)
#
#    proc = subprocess.Popen(string, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    out, err = proc.communicate()
#
#    subs = becgis.open_as_array(output_fh, nan_values = True)
#    total_size = np.nansum(subs[subs != 0] / subs[subs != 0])
#
#    sizes = dict()
#    total_out = dict()
#    total_in = dict()
#    ratios = dict()
#
#    accumsin_boundary = list()
#    accumsout_boundary = list()
#
#    for sb in np.unique(subs[subs!=0]):
#
#        sizes[sb] = np.nansum(subs[subs == sb]) / sb
#
#        accumsin = list()
#        accumsout = list()
#
#        nc = netCDF4.Dataset(accum)
#        driver = ogr.GetDriverByName('ESRI Shapefile')
#        dataSource = driver.Open(outlets, 0)
#        layer = dataSource.GetLayer()
#        featureCount = layer.GetFeatureCount()
#        for pt in range(featureCount):
#            feature = layer.GetFeature(pt)
#            subbasin = feature.GetField("id")
#            if sb == int(subbasin):
#                geometry = feature.GetGeometryRef()
#                x = geometry.GetX()
#                y = geometry.GetY()
#                pos_x = (np.abs(nc.variables['longitude'][:]-x)).argmin()
#                pos_y = (np.abs(nc.variables['latitude'][:]-y)).argmin()
#                accumsout.append(nc.variables['Acc_Pixels_CR'][pos_y,pos_x])
#                if 0 in dico_out[sb]:
#                    accumsout_boundary.append(nc.variables['Acc_Pixels_CR'][pos_y,pos_x])
#            if subbasin in dico_in[sb]:
#                geometry = feature.GetGeometryRef()
#                x = geometry.GetX()
#                y = geometry.GetY()
#                pos_x = (np.abs(nc.variables['longitude'][:]-x)).argmin()
#                pos_y = (np.abs(nc.variables['latitude'][:]-y)).argmin()
#                accumsin.append(nc.variables['Acc_Pixels_CR'][pos_y,pos_x])
#
#        total_out[sb] = np.sum(accumsout)
#
#        if os.path.exists(inlets):
#
#            nc = netCDF4.Dataset(accum)
#            driver = ogr.GetDriverByName('ESRI Shapefile')
#            dataSource = driver.Open(inlets, 0)
#            layer = dataSource.GetLayer()
#            featureCount = layer.GetFeatureCount()
#            for pt in range(featureCount):
#                feature = layer.GetFeature(pt)
#                subbasin = feature.GetField("id")
#                if sb == int(subbasin):
#                    geometry = feature.GetGeometryRef()
#                    x = geometry.GetX()
#                    y = geometry.GetY()
#                    pos_x = (np.abs(nc.variables['longitude'][:]-x)).argmin()
#                    pos_y = (np.abs(nc.variables['latitude'][:]-y)).argmin()
#                    accumsin.append(nc.variables['Acc_Pixels_CR'][pos_y,pos_x])
#                    accumsin_boundary.append(nc.variables['Acc_Pixels_CR'][pos_y,pos_x])
#
#        if len(accumsin) >= 1:
#            total_in[sb] = np.sum(accumsin)
#        else:
#            total_in[sb] = 0.0
#
#        ratios[sb] = (total_out[sb] - total_in[sb]) / sizes[sb]
#
#    ratios['full'] = (np.sum(accumsout_boundary) - np.sum(accumsin_boundary)) / total_size
#
#    return ratios
