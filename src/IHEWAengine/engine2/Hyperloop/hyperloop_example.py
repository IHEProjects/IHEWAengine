# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 14:52:31 2017

@author: bec
"""
# Builtins
from __future__ import print_function
# Plot
import matplotlib.pyplot as plt
# Self
try:
    from . import sheet1_functions as sh1
    from . import sheet2_functions as sh2
    from . import sheet3_functions as sh3
    from . import sheet4_functions as sh4
    from . import sheet5_functions as sh5
    from . import hyperloop as hl
except ImportError:
    from IHEWAengine.engine2.Hyperloop import sheet1_functions as sh1
    from IHEWAengine.engine2.Hyperloop import sheet2_functions as sh2
    from IHEWAengine.engine2.Hyperloop import sheet3_functions as sh3
    from IHEWAengine.engine2.Hyperloop import sheet4_functions as sh4
    from IHEWAengine.engine2.Hyperloop import sheet5_functions as sh5
    from IHEWAengine.engine2.Hyperloop import hyperloop as hl

###
# Define basin specific parameters
###
basins = dict()

ID = 14
basins[ID] = {
    # Give name and ID of basin, set ID equal to key.
    'name': 'VGTB',

    # Give LU-map, SW-file,
    # folder with subbasin masks (name: subbasinname_ID.tif)
    'lu': r"C:\Users\bec\Desktop\HL_testcase\VGTB\VGTB_LU.tif",
    'full_basin_mask': r"C:\Users\bec\Desktop\HL_testcase\VGTB\VGTB_FBM.tif",
    'masks': r"C:\Users\bec\Desktop\HL_testcase\VGTB\VGTB_SBM",

    # Give start and enddates growingseasons, classifications to select Harvest Index and Water Content, LU-classification number
    'crops': [
        (
        'D:\\project_ADB\\subproject_Crop_Calendars\\consolidation\\seasons_basin03_crop35.csv',
        'Rice - Rainfed', 'Cereals', '-', 35.0),
        (
        'D:\\project_ADB\\subproject_Crop_Calendars\\consolidation\\seasons_perennial.csv',
        'Tea', 'Beverage crops', '-', 42.0),
        (
        'D:\\project_ADB\\subproject_Crop_Calendars\\consolidation\\seasons_basin03_crop43.csv',
        'Fodder', 'Other crops', '-', 43.0),
        (
        'D:\\project_ADB\\subproject_Crop_Calendars\\consolidation\\seasons_basin03_crop54.csv',
        'Rice - Irrigated', 'Cereals', '-', 54.0),
        (
        'D:\\project_ADB\\subproject_Crop_Calendars\\consolidation\\seasons_basin03_crop57.csv',
        'Sugar cane', 'Non-cereals', 'Sugar crops', 57.0),
    ],

    # Provide non-crop data, set to None if not available.
    'non_crop': {
        'meat': r"D:\project_ADB\validation_data\STATS_GSOV\Main\yield_per_catchment\Yearly_Yields_WPs_{0}.0_meat.csv".format(
            ID),
        'milk': r"D:\project_ADB\validation_data\STATS_GSOV\Main\yield_per_catchment\Yearly_Yields_WPs_{0}.0_milk.csv".format(
            ID),
        'timber': r"D:\project_ADB\validation_data\STATS_GSOV\Main\yield_per_catchment\Yearly_Yields_WPs_{0}.0_timber.csv".format(
            ID),
        'aquaculture': r"D:\project_ADB\validation_data\STATS_GSOV\Main\yield_per_catchment\Yearly_Yields_WPs_{0}.0_aquaculture.csv".format(
            ID)},

    # set variables needed for sheet 5 and 1. keys in dico_out and dico_in refer to subbasin-IDs, list to subbasin-IDs to the respective subbasin in or outflow point. Give most upstream subbasins the lowest value, downstream basins high values.
    'recycling_ratio': 0.02,
    'dico_in': {1: [], 2: [], 3: [], 4: [1, 2]},
    'dico_out': {1: [4], 2: [4], 3: [0], 4: [0]},
    'GRACE': r"C:\Users\bec\Desktop\HL_testcase\VGTB\basin_14_GSFC_mmwe.csv",
    'fraction_xs': [10, 50, 10, 50],
    'discharge_out_from_wp': True,
    # Value is true if WaterPix is used directly in sheet5 rather than Surfwat
    'lu_based_supply_split': False,
    # Value is True if an initial split in SW/GW supply is done based on landuse class and values in get_dictionnaries
    'grace_supply_split': True,
    # Value is True if GW/SW split is adjusted. Can be true weather or not initial split based on landuse is done. If both of these are False, all supply will be SWsupply
    'grace_split_alpha_bounds': ([0.0, 0.5, 1.], [1., 1., 12.]),
    # lower and upper bounds of trigonometric function parameters for splitting suply into sw and gw as ([alpha_l, beta_l, theta_l],[alpha_u, beta_u, theta_u]). ([0., 0., 1.], [1.0, 1.0, 12.]) are the widest bounds allowed. alpha controls the mean, beta the amplitude and theta the phase.
    'water_year_start_month': 10,
    # Start month of water year. Used to compute the yearly sheets.
    'ndm_max_original': False,
    # True will use original method to determine NDM_max (based on entire domain), false will use a different method dependent on nearby pixels of the same lu-category.
}

###
# Define output folder and WaterPix file
###
output_dir = r"C:\Users\bec\Desktop\HL_testcase"

###
# Define some paths of static data
###
data_global = dict()
data_global["equiped_sw_irrigation"] = r"K:\Products\Landuse\Global\GMIA_FAO\gmia_v5_aeisw_pct_aei_asc\gmia_v5_aeisw_pct_aei.asc"
data_global["wpl_tif"] = r"D:\Products\GreyWaterFootprint\WPL.tif"
data_global["environ_water_req"] = r"D:\Products\EF\EWR.tif"
data_global["population_tif"] = r"D:\Products\WorldPop\VNM-POP\VNM_pph_v2b_2009.tif"
data_global["dem"] = r"K:\Products\HydroSHED\DEM\HydroSHED\DEM\DEM_HydroShed_m_15s.tif"
data_global["dir"] = r"K:\Products\HydroSHED\DEM\HydroSHED\DIR\DIR_HydroShed_-_15s.tif"
data_global["waterpix"] = r"D:\Products\Waterpix\SEAsia\output_20k_v2_20171102.nc"

###
# Define paths of folders with temporal tif files (file should be named "*_yyyymm.tif") covering the entire domain (i.e. spanning across all basins)
###
# waterpix        = r"K:\Products\WATERPIX\out_SEAsia_0point075.nc"
# waterpix_in     = r"K:\Products\WATERPIX\in_SEAsia_0point075.nc"
# data_maps = dict()
# data_maps["ndm_folder"]          = r"K:\Products\MODIS_17_NDM"
# data_maps["p_folder"]            = hl.WP_NetCDF_to_Rasters(waterpix_in, 'Precipitation_M', r"K:\Products\WATERPIX\Output")
# data_maps["et_folder"]           = hl.WP_NetCDF_to_Rasters(waterpix_in, 'Evapotranspiration_M', r"K:\Products\WATERPIX\Output")
# data_maps["n_folder"]            = hl.WP_NetCDF_to_Rasters(waterpix_in, 'RainyDays_M', r"K:\Products\WATERPIX\Output")
# data_maps["lai_folder"]          = hl.WP_NetCDF_to_Rasters(waterpix_in, 'LeafAreaIndex_M', r"K:\Products\WATERPIX\Output")
# data_maps["etref_folder"]        = hl.WP_NetCDF_to_Rasters(waterpix_in, 'ReferenceET_M', r"K:\Products\WATERPIX\Output")
# data_maps["bf_folder"]           = hl.WP_NetCDF_to_Rasters(waterpix, 'Baseflow_M', r"K:\Products\WATERPIX\Output")
# data_maps["sr_folder"]           = hl.WP_NetCDF_to_Rasters(waterpix, 'SurfaceRunoff_M', r"K:\Products\WATERPIX\Output")
# data_maps["tr_folder"]           = hl.WP_NetCDF_to_Rasters(waterpix, 'TotalRunoff_M', r"K:\Products\WATERPIX\Output")
# data_maps["perc_folder"]         = hl.WP_NetCDF_to_Rasters(waterpix, 'Percolation_M', r"K:\Products\WATERPIX\Output")
# data_maps["dperc_folder"]        = hl.WP_NetCDF_to_Rasters(waterpix, 'IncrementalPercolation_M', r"K:\Products\WATERPIX\Output")
# data_maps["supply_total_folder"] = hl.WP_NetCDF_to_Rasters(waterpix, 'Supply_M', r"K:\Products\WATERPIX\Output")
# data_maps["dro"]                 = hl.WP_NetCDF_to_Rasters(waterpix, 'IncrementalRunoff_M', r"K:\Products\WATERPIX\Output")
# data_maps["etb_folder"]          = hl.WP_NetCDF_to_Rasters(waterpix, 'ETblue_M', r"K:\Products\WATERPIX\Output")
# data_maps["etg_folder"]          = hl.WP_NetCDF_to_Rasters(waterpix, 'ETgreen_M', r"K:\Products\WATERPIX\Output")

steps = dict()
steps['Reproject data'] = False
steps['Create Sheet 4 and 6'] = True
steps['Create Sheet 2'] = False
steps['Create Sheet 3'] = False
steps['Create Sheet 5'] = False
steps['Create Sheet 1'] = False

# %%
###
# Start hyperloop
###
for ID, data_meta in basins.items():

    print('Start basin {0}: {1}'.format(ID, data_meta['name']))
    plt.close("all")

    if steps['Reproject data']:
        complete_data = hl.sort_data(data_maps, data_meta, data_global, output_dir)
    else:
        complete_data = hl.sort_data_short(output_dir, data_meta)

    if steps['Create Sheet 4 and 6']:
        complete_data = sh4.create_sheet4_6(complete_data, data_meta, output_dir, data_global)

    if steps['Create Sheet 2']:
        complete_data = sh2.create_sheet2(complete_data, data_meta, output_dir)

    if steps['Create Sheet 3']:
        complete_data = sh3.create_sheet3(complete_data, data_meta, output_dir)

    if steps['Create Sheet 5']:
        complete_data = sh5.create_sheet5(complete_data, data_meta, output_dir, data_global)

    if steps['Create Sheet 1']:
        complete_data, all_sh1_results = sh1.create_sheet1(complete_data, data_meta, output_dir, data_global)
