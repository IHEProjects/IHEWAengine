# -*- coding: utf-8 -*-
"""
`Document structure <https://en.wikibooks.org/wiki/LaTeX/Document_Structure>`_

"""
# Builtins
import inspect
import os
import pickle
# 3rd
import yaml
# Math
import numpy as np
import pandas as pd
# GIS
# Plot
import matplotlib
# Not to use X server. For TravisCI.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# Self
try:
    # IHEClassInitError, IHEStringError, IHETypeError
    from ...exception import IHEClassInitError, IHEKeyError, IHEFileError
except ImportError:
    from IHEWAengine.exception import IHEClassInitError, IHEKeyError, IHEFileError

try:
    from . import sheet1_functions as sh1
    from . import sheet2_functions as sh2
    from . import sheet3_functions as sh3
    from . import sheet4_functions as sh4
    from . import sheet5_functions as sh5
    from . import sheet7_functions as sh7
    from . import hyperloop as hl
except ImportError:
    from IHEWAengine.engine2.Hyperloop import sheet1_functions as sh1
    from IHEWAengine.engine2.Hyperloop import sheet2_functions as sh2
    from IHEWAengine.engine2.Hyperloop import sheet3_functions as sh3
    from IHEWAengine.engine2.Hyperloop import sheet4_functions as sh4
    from IHEWAengine.engine2.Hyperloop import sheet5_functions as sh5
    from IHEWAengine.engine2.Hyperloop import sheet7_functions as sh7
    from IHEWAengine.engine2.Hyperloop import hyperloop as hl


class Engine(object):
    """This Engine class

    Load base.yml file.

    Args:
        conf (dict): User defined configuration data from yaml file.
    """
    def __init__(self, conf):
        """Class instantiation
        """
        self.__conf = conf
        self.pout = self.__conf['folder']['engine2']['res']
        print('output_dir', self.pout)

        self.__status = {
            'messages': {
                0: 'S: WA.Engine2  {f:>20} : status {c}, {m}',
                1: 'E: WA.Engine2  {f:>20} : status {c}: {m}',
                2: 'W: WA.Engine2  {f:>20} : status {c}: {m}',
            },
            'code': 0,
            'message': '',
            'is_print': True
        }

        self.conf = {
            'path': os.path.dirname(__file__),
            'fname': 'ihewaengine.yml',
            'engine': {
                'basins': {},
                'datasets': {}
            }
        }

        self._conf()

        if self.__status['code'] == 0:
            self.run()

        print(self.conf['engine']['basins'])

    def _conf(self):
        fun_name = inspect.currentframe().f_code.co_name
        f_in = os.path.join(self.__conf['workspace'],
                            self.conf['path'],
                            self.conf['fname'])
        if os.path.exists(f_in):
            conf = yaml.load(open(f_in, 'r', encoding='UTF8'), Loader=yaml.FullLoader)

            for key in self.conf['engine'].keys():
                try:
                    self.conf['engine'][key] = conf[key]
                except KeyError:
                    self.__status['code'] = 1
                    raise IHEKeyError(key, f_in) from None
                else:
                    self.__status['code'] = 0
        else:
            self.__status['code'] = 1
            raise IHEFileError(f_in)from None

    def run(self):
        pstat = os.path.join(self.__conf['workspace'], self.conf['engine']['datasets']['static']['path'])
        prsds = os.path.join(self.__conf['workspace'], self.conf['engine']['datasets']['remote']['path'])
        psimu = os.path.join(self.__conf['workspace'], self.conf['engine']['datasets']['model']['path'])

        ###
        # Define basin specific parameters
        ###
        basins = dict()
        ID = 0
        basins[ID] = {
            # Give name and ID of basin, set ID equal to key.
            'name': 'Cimanuk',
            'id': ID,

            'lu': os.path.join(pstat, "Cimanuk.tif"),

            'full_basin_mask': os.path.join(pstat, "Cimanuk.tif"),
            'masks': {1: ('Full',
                          os.path.join(pstat, "1_subbasin.tif"),
                          [], [])},
            #            'masks': {
            #                         1:(name,fh,[inflow_files],[transfer_files]),
            #                         2:(name,fh,[inflow_files],[transfer_files])),
            #                         ...
            #                     }

            'alpha_min': None,

            # Give start and enddates growingseasons, classifications
            # to select Harvest Index and Water Content, LU-classification number
            'crops': [
                (
                os.path.join(pstat, "growing seasons", "palm_perennial.txt"),
                'Palm Oil', 'Other crops', '-', 52.0),
                (
                os.path.join(pstat, "growing seasons", "palm_perennial.txt"),
                'Palm Oil', 'Other crops', '-', 33.0),
                (os.path.join(pstat, "growing seasons",
                              "rice_irrigated_java.txt"),
                 'Rice - Irrigated', 'Cereals', '-', 54.0),
                (
                os.path.join(pstat, "growing seasons", "rice_rain_java.txt"),
                'Rice - Rainfed', 'Cereals', '-', 35.0)
            ],

            # Provide non-crop data, set to None if not available.
            'non_crop': None,
            #            'non_crop':                 {'meat':        None,
            #                                         'milk':        None,
            #                                         'timber':      None,
            #                                         'aquaculture': None,
            #                                         },
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

            'GRACE': os.path.join(pstat, "Cimanuk_GSFC_average_mmwe.csv"),

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
            "equiped_sw_irrigation": os.path.join(pstat, "GMIA_FAO\GMIA_FAO\gmia_v5_aeisw_pct_aei_asc\gmia_v5_aeisw_pct_aei.asc"),
            "wpl_tif":               os.path.join(pstat, "WPL_Max1.tif"),
            "environ_water_req":     os.path.join(pstat, "EWR.tif"),
            "population_tif":        os.path.join(pstat, "IDN_pph_v2b_2010_UNadj_calc_CimanukClip.tif"),
            "cattle":                os.path.join(pstat, "Glb_Cattle_CC2006_AD_CimanukClip.tif"),
            "dem":                   os.path.join(pstat, "HydroSHED\DEM\DEM_HydroShed_m_3s.tif"),
            "dir": None,
            "root_depth":            os.path.join(psimu, 'RootDepth.tif')
        }

        ###
        # Define paths of folders with temporal tif files (file should be named "*_yyyymm.tif")
        # covering the entire domain (i.e. spanning across all basins)
        ###
        data = {
            "ndm_folder":   os.path.join(prsds, "NDM"),
            "p_folder":     os.path.join(prsds, "Precipitation"),
            "et_folder":    os.path.join(prsds, "Evaporation"),
            "n_folder":     os.path.join(prsds, "Rainy_Days"),
            "lai_folder":   os.path.join(prsds, "LAI"),
            "etref_folder": os.path.join(prsds, "ETref"),
            "bf_folder":    os.path.join(psimu, 'Baseflow_M'),
            "sr_folder":    os.path.join(psimu, 'SurfaceRunoff_M'),
            "tr_folder":    os.path.join(psimu, 'TotalRunoff_M'),
            "perc_folder":  os.path.join(psimu, 'Percolation_M'),
            "dperc_folder": os.path.join(psimu, 'IncrementalPercolation_M'),
            "supply_total_folder": os.path.join(psimu, 'Supply_M'),
            "dro_folder":   os.path.join(psimu, 'IncrementalRunoff_M'),
            "etb_folder":   os.path.join(psimu, 'ETblue_M'),
            "etg_folder":   os.path.join(psimu, 'ETgreen_M'),
            "rzsm_folder":  os.path.join(psimu, 'RootDepthSoilMoisture_M')
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
        # %%
        ###
        # Start hyperloop
        ###
        for ID, metadata in basins.items():

            print('Start basin {0}: {1}'.format(ID, metadata['name']))
            plt.close("all")

            # Reproject data
            if steps['Reproject data']:
                complete_data = hl.sort_data(data, metadata, global_data, self.pout)

                pickle_out = open(
                    os.path.join(self.pout, metadata['name'],
                                 "complete_data_step1.pickle"),
                    "wb")
                pickle.dump(complete_data, pickle_out)
                pickle_out.close()
            else:
                if os.path.exists(os.path.join(self.pout,
                                               metadata['name'],
                                               "complete_data_step1.pickle")):
                    pickle_in = open(os.path.join(self.pout,
                                                  metadata['name'],
                                                  "complete_data_step1.pickle"), "rb")
                    complete_data = pickle.load(pickle_in)
                    pickle_in.close()
                else:
                    complete_data = hl.sort_data_short(self.pout, metadata)

            # Sheet 4 and 6
            if steps['Create Sheet 4 and 6']:
                complete_data = sh4.supply_return_natural_lu(metadata,
                                                             complete_data)

                complete_data = sh4.create_sheet4_6(complete_data,
                                                    metadata,
                                                    self.pout,
                                                    global_data)
                pickle_out = open(
                    os.path.join(self.pout,
                                 metadata['name'],
                                 "complete_data_sheet46.pickle"), "wb")
                pickle.dump(complete_data, pickle_out)
                pickle_out.close()

            # Sheet 2
            if steps['Create Sheet 2']:
                pickle_in = open(
                    os.path.join(self.pout,
                                 metadata['name'],
                                 "complete_data_sheet46.pickle"), "rb")

                complete_data = pickle.load(pickle_in)
                pickle_in.close()

                complete_data = sh2.create_sheet2(complete_data,
                                                  metadata,
                                                  self.pout)
                pickle_out = open(
                    os.path.join(self.pout,
                                 metadata['name'],
                                 "complete_data_sheet2.pickle"), "wb")
                pickle.dump(complete_data, pickle_out)
                pickle_out.close()

            # Sheet 3
            if steps['Create Sheet 3']:
                pickle_in = open(
                    os.path.join(self.pout,
                                 metadata['name'],
                                 "complete_data_sheet2.pickle"), "rb")

                complete_data = pickle.load(pickle_in)
                pickle_in.close()

                complete_data = sh3.create_sheet3(complete_data,
                                                  metadata,
                                                  self.pout)
                pickle_out = open(
                    os.path.join(self.pout,
                                 metadata['name'],
                                 "complete_data_sheet3.pickle"), "wb")
                pickle.dump(complete_data, pickle_out)
                pickle_out.close()

            # Sheet 5
            if steps['Create Sheet 5']:
                pickle_in = open(
                    os.path.join(self.pout,
                                 metadata['name'],
                                 "complete_data_sheet46.pickle"), "rb")

                complete_data = pickle.load(pickle_in)
                pickle_in.close()

                complete_data = sh5.create_sheet5(complete_data,
                                                  metadata, self.pout,
                                                  global_data)
                pickle_out = open(
                    os.path.join(self.pout,
                                 metadata['name'],
                                 "complete_data_sheet5.pickle"), "wb")
                pickle.dump(complete_data, pickle_out)
                pickle_out.close()

            # Sheet 1
            if steps['Create Sheet 1']:
                pickle_in = open(
                    os.path.join(self.pout,
                                 metadata['name'],
                                 "complete_data_sheet5.pickle"), "rb")

                complete_data = pickle.load(pickle_in)
                pickle_in.close()

                complete_data, all_sh1_results = sh1.create_sheet1(complete_data,
                                                                   metadata,
                                                                   self.pout,
                                                                   global_data)

            # Sheet 7
            if steps['Create Sheet 7']:
                pickle_in = open(
                    os.path.join(self.pout,
                                 metadata['name'],
                                 "complete_data_sheet5.pickle"), "rb")

                complete_data = pickle.load(pickle_in)
                pickle_in.close()

                complete_data = sh7.create_sheet7(complete_data,
                                                  metadata,
                                                  self.pout,
                                                  global_data,
                                                  data)

            print('End')

