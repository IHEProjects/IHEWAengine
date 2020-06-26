# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 14:45:36 2020

@author: cmi001
"""
import pytest

import os
import pickle

import matplotlib.pyplot as plt

# import IHEWAengine
try:
    from IHEWAengine.engine2.Hyperloop import sheet1 as sh1
    from IHEWAengine.engine2.Hyperloop import sheet2 as sh2
    from IHEWAengine.engine2.Hyperloop import sheet3 as sh3
    from IHEWAengine.engine2.Hyperloop import sheet4 as sh4
    from IHEWAengine.engine2.Hyperloop import sheet5 as sh5
    from IHEWAengine.engine2.Hyperloop import sheet7 as sh7
    from IHEWAengine.engine2.Hyperloop import hyperloop as hl
except ImportError as err:
    raise 'Error: {err}'.format(err)

if __name__ == '__main__':

    #####
    # If you have downloaded the example datasets, the paths path_output and path_input
    # are the only ones you should need to change to be able to run the WA+ sheets
    ####
    path = os.path.dirname(os.path.abspath(__file__))

    path_input = os.path.join(path, 'data', 'engine2', 'Hyperloop')

    path_input_series = os.path.join(path_input, 'series')
    path_input_static = os.path.join(path_input, 'static')
    path_input_remote = os.path.join(path_input, 'remote')
    path_input_hydsim = os.path.join(path_input, 'hydsim')

    path_output = os.path.join(path_input, 'Output')  # directory to save output

    ###
    # Define basin specific parameters
    #
    # TODO, 20200616-QPan, Why there is no simulation period input?
    ###
    basins = dict()
    ID = 0
    basins[ID] = {
        # Give name and ID of basin, set ID equal to key.
        'name': 'Example{}'.format(ID),
        'id': ID,

        'lu': os.path.join(path_input_static, 'LU.tif'),

        'full_basin_mask': os.path.join(path_input_static, 'LU.tif'),
        'masks': {
            1: ('Full',
                os.path.join(path_input_static, 'SubBasin.tif'),
                [], [])},
        # 'masks': {
        #     1:(name,fh,[inflow_files],[transfer_files]),
        #     2:(name,fh,[inflow_files],[transfer_files])),
        #     ...
        # }

        'alpha_min': None,

        # Give start and enddates growingseasons, classifications
        # to select Harvest Index and Water Content, LU-classification number
        'crops': [
            (os.path.join(path_input_series, 'Growing Seasons/palm_perennial.txt'),
             'Palm Oil',
             'Other crops',
             '-',
             52.0),
            (os.path.join(path_input_series, 'Growing Seasons/palm_perennial.txt'),
             'Palm Oil',
             'Other crops',
             '-',
             33.0),
            (os.path.join(path_input_series, 'Growing Seasons/rice_irrigated_java.txt'),
             'Rice - Irrigated',
             'Cereals',
             '-',
             54.0),
            (os.path.join(path_input_series, 'Growing Seasons/rice_rainfed_java.txt'),
             'Rice - Rainfed',
             'Cereals',
             '-',
             35.0)
        ],

        # Provide non-crop data, set to None if not available.
        'non_crop': None,
        # 'non_crop': {
        #     'meat':        None,
        #     'milk':        None,
        #     'timber':      None,
        #     'aquaculture': None,
        # },
        # set variables needed for sheet 5 and 1.
        # keys in dico_out and dico_in refer to subbasin-IDs,
        # list to subbasin-IDs to the respective subbasin in or outflow point.
        # Give most upstream subbasins the lowest value, downstream basins high values.
        #
        # variables needed for sheet 5 and 1.
        # keys in dico_out and dico_in refer to subbasin-IDs,
        # list to subbasin-IDs to the respective subbasin in or outflow point.
        # Give most upstream subbasins the lowest value, downstream basins high values.

        'recycling_ratio': 0.02,

        'dico_in': {1: []},
        'dico_out': {1: [0]},

        'GRACE': os.path.join(path_input_series, 'GRACE/GSFC-average_mmwe.csv'),

        'discharge_out_from_wp': True,
        'fraction_xs': [4, 25, 4, 25],
        'lu_based_supply_split': True,
        'grace_supply_split': True,
        'water_year_start_month': 1,
        'ndm_max_original': True,
        'grace_split_alpha_bounds': ([0.0, 0.5, 0.9999],
                                     [0.0001, 1., 1.])

        # lower and upper bounds of trigonometric function parameters for splitting suply
        # into sw and gw as
        # (
        #   [alpha_l, beta_l, theta_l],
        #   [alpha_u, beta_u, theta_u]
        # ). (
        #   [0., 0., 1.],
        #   [1.0, 1.0, 12.]
        # )
        # are the widest bounds allowed.
        # alpha controls the mean, beta the amplitude and theta the phase.
    }

    ###
    # Define some paths of static data
    ###
    global_data = {
        'equiped_sw_irrigation': os.path.join(path_input_static, 'GMIA-aeisw_pct_aei_v5.asc'),
        'wpl_tif':               os.path.join(path_input_static, 'WPL.tif'),
        'environ_water_req':     os.path.join(path_input_static, 'EWR.tif'),
        'population_tif':        os.path.join(path_input_static, 'Population.tif'),
        'cattle':                os.path.join(path_input_static, 'Cattle.tif'),
        'dem':                   os.path.join(path_input_static, 'DEM-HydroShed_m_3s.tif'),
        'dir':                   None,

        'root_depth':            os.path.join(path_input_hydsim, 'RootDepth.tif')
    }

    ###
    # Define paths of folders with temporal tif files
    # (file should be named '*_yyyymm.tif')
    # covering the entire domain (i.e. spanning across all basins)
    ###
    data = {
        'ndm_folder':   os.path.join(path_input_remote, 'NDM'),
        'p_folder':     os.path.join(path_input_remote, 'Precipitation'),
        'et_folder':    os.path.join(path_input_remote, 'Evaporation'),
        'n_folder':     os.path.join(path_input_remote, 'RainyDays'),
        'lai_folder':   os.path.join(path_input_remote, 'LAI'),
        'etref_folder': os.path.join(path_input_remote, 'ETref'),

        'bf_folder':    os.path.join(path_input_hydsim, 'Baseflow'),
        'sr_folder':    os.path.join(path_input_hydsim, 'SurfaceRunoff'),
        'tr_folder':    os.path.join(path_input_hydsim, 'TotalRunoff'),
        'perc_folder':  os.path.join(path_input_hydsim, 'Percolation'),
        'dperc_folder': os.path.join(path_input_hydsim, 'IncrementalPercolation'),
        'supply_total_folder': os.path.join(path_input_hydsim, 'Supply'),
        'dro_folder':   os.path.join(path_input_hydsim, 'IncrementalRunoff'),
        'etb_folder':   os.path.join(path_input_hydsim, 'ETblue'),
        'etg_folder':   os.path.join(path_input_hydsim, 'ETgreen'),
        'rzsm_folder':  os.path.join(path_input_hydsim, 'RootDepthSoilMoisture')
    }

    # Sheets to run
    steps = {
        'Reproject data': True,
        'Create Sheet 4 and 6': True,
        'Create Sheet 2': True,
        'Create Sheet 3': True,
        'Create Sheet 5': True,
        'Create Sheet 1': True,
        'Create Sheet 7': True
    }
    # steps = {
    #     'Reproject data':       True,
    #     'Create Sheet 4 and 6': True,
    #     'Create Sheet 2':       True,
    #     'Create Sheet 3':       True,
    #     'Create Sheet 5':       True,
    #     'Create Sheet 1':       True,
    #     'Create Sheet 7':       True
    # }
    # %%
    ###
    # Start hyperloop
    ###
    for ID, metadata in basins.items():

        print('Start basin {0}: {1}'.format(ID, metadata['name']))
        plt.close('all')

        # Reproject data
        if steps['Reproject data']:
            complete_data = hl.sort_data(data, metadata, global_data, path_output)
            # sort_var(data, metadata, global_data, output_dir, key, complete_data,
            #          time_var='time_yyyymm')

            pickle_out = open(
                os.path.join(path_output, metadata['name'],
                             'complete_data_step1.pickle'),
                'wb')
            pickle.dump(complete_data, pickle_out)
            pickle_out.close()
        else:
            if os.path.exists(os.path.join(path_output,
                                           metadata['name'],
                                           'complete_data_step1.pickle')):
                pickle_in = open(os.path.join(path_output,
                                              metadata['name'],
                                              'complete_data_step1.pickle'), 'rb')
                complete_data = pickle.load(pickle_in)
                pickle_in.close()
            else:
                complete_data = hl.sort_data_short(path_output, metadata)

        # Sheet 4 and 6
        if steps['Create Sheet 4 and 6']:
            complete_data = sh4.supply_return_natural_lu(metadata,
                                                         complete_data)

            complete_data = sh4.create_sheet4_6(complete_data,
                                                metadata,
                                                path_output,
                                                global_data)
            pickle_out = open(
                os.path.join(path_output,
                             metadata['name'],
                             'complete_data_sheet46.pickle'), 'wb')
            pickle.dump(complete_data, pickle_out)
            pickle_out.close()

        # Sheet 2
        if steps['Create Sheet 2']:
            pickle_in = open(
                os.path.join(path_output,
                             metadata['name'],
                             'complete_data_sheet46.pickle'), 'rb')

            complete_data = pickle.load(pickle_in)
            pickle_in.close()

            complete_data = sh2.create_sheet2(complete_data,
                                              metadata,
                                              path_output)
            pickle_out = open(
                os.path.join(path_output,
                             metadata['name'],
                             'complete_data_sheet2.pickle'), 'wb')
            pickle.dump(complete_data, pickle_out)
            pickle_out.close()

        # Sheet 3
        if steps['Create Sheet 3']:
            pickle_in = open(
                os.path.join(path_output,
                             metadata['name'],
                             'complete_data_sheet2.pickle'), 'rb')

            complete_data = pickle.load(pickle_in)
            pickle_in.close()

            complete_data = sh3.create_sheet3(complete_data,
                                              metadata,
                                              path_output)
            pickle_out = open(
                os.path.join(path_output,
                             metadata['name'],
                             'complete_data_sheet3.pickle'), 'wb')
            pickle.dump(complete_data, pickle_out)
            pickle_out.close()

        # Sheet 5
        if steps['Create Sheet 5']:
            pickle_in = open(
                os.path.join(path_output,
                             metadata['name'],
                             'complete_data_sheet46.pickle'), 'rb')

            complete_data = pickle.load(pickle_in)
            pickle_in.close()

            complete_data = sh5.create_sheet5(complete_data,
                                              metadata, path_output,
                                              global_data)
            pickle_out = open(
                os.path.join(path_output,
                             metadata['name'],
                             'complete_data_sheet5.pickle'), 'wb')
            pickle.dump(complete_data, pickle_out)
            pickle_out.close()

        # Sheet 1
        if steps['Create Sheet 1']:
            pickle_in = open(
                os.path.join(path_output,
                             metadata['name'],
                             'complete_data_sheet5.pickle'), 'rb')

            complete_data = pickle.load(pickle_in)
            pickle_in.close()

            complete_data, all_sh1_results = sh1.create_sheet1(complete_data,
                                                               metadata,
                                                               path_output,
                                                               global_data)

        # Sheet 7
        if steps['Create Sheet 7']:
            pickle_in = open(
                os.path.join(path_output,
                             metadata['name'],
                             'complete_data_sheet5.pickle'), 'rb')

            complete_data = pickle.load(pickle_in)
            pickle_in.close()

            complete_data = sh7.create_sheet7(complete_data,
                                              metadata,
                                              path_output,
                                              global_data,
                                              data)

        print('End')
