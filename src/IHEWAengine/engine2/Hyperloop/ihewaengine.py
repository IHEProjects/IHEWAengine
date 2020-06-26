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
    from . import ihewaengine_pkg_version

    from . import sheet1 as sh1
    from . import sheet2 as sh2
    from . import sheet3 as sh3
    from . import sheet4 as sh4
    from . import sheet5 as sh5
    from . import sheet7 as sh7
    from . import hyperloop as hl
except ImportError:
    from IHEWAengine.engine2.Hyperloop import ihewaengine_pkg_version

    from IHEWAengine.engine2.Hyperloop import sheet1 as sh1
    from IHEWAengine.engine2.Hyperloop import sheet2 as sh2
    from IHEWAengine.engine2.Hyperloop import sheet3 as sh3
    from IHEWAengine.engine2.Hyperloop import sheet4 as sh4
    from IHEWAengine.engine2.Hyperloop import sheet5 as sh5
    from IHEWAengine.engine2.Hyperloop import sheet7 as sh7
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
        self.version = 'v{}'.format(ihewaengine_pkg_version.__version__)

        self.__conf = conf

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
                'input': {},
                'output': {},
                'parameters': {}
            }
        }

        self._conf()

        # ============ #
        # Engine input #
        # ============ #
        self.path_input = self.__conf['workspace']
        self.path_output = self.__conf['folder']['engine2']['res']
        print(self.path_output)

        # v1.0.0, Bert
        self.basins = {}
        self.data_meta = {}
        self.data = {}
        self.data_global = {}

        if self.__status['code'] == 0:
            self.run()

    def _conf(self):
        # fun_name = inspect.currentframe().f_code.co_name

        f_in = os.path.join(self.__conf['workspace'], self.conf['path'], self.conf['fname'])

        if os.path.exists(f_in):
            conf = yaml.load(open(f_in, 'r', encoding='UTF8'), Loader=yaml.FullLoader)

            for key in self.conf['engine'].keys():
                try:
                    self.conf['engine'][key] = conf[self.version][key]
                except KeyError:
                    self.__status['code'] = 1
                    raise IHEKeyError(key, f_in) from None
                else:
                    self.__status['code'] = 0
        else:
            self.__status['code'] = 1
            raise IHEFileError(f_in)from None

        if self.__conf['data']['engines']['engine2']['version'] not in list(conf.keys()):
            raise IHEClassInitError('Hyperloop') from None

    def run(self):
        fun_name = inspect.currentframe().f_code.co_name
        # data:
        #    basins
        #       Test:
        #         id:
        #         parameter:
        #         series:
        print('input_dir')
        engine_data = self.__conf['data']['engines']['engine2']['data']

        basins = engine_data['basins']
        basin_maps = engine_data['maps']

        for basin_name, basin_val in basins.items():
            print('Start basin {0}: {1}'.format(basin_val['id'], basin_name))
            plt.close('all')

            basin_id = basin_val['id']
            basin_step = basin_val['steps']
            basin_para = basin_val['parameter']
            basin_series = basin_val['series']
            # path
            pseries = os.path.join(self.path_input, basin_series['path'])
            pstatic = os.path.join(self.path_input, basin_maps['static']['path'])
            premote = os.path.join(self.path_input, basin_maps['remote']['path'])
            phydsim = os.path.join(self.path_input, basin_maps['hydsim']['path'])
            # file
            fseries = basin_series['file']
            fstatic = basin_maps['static']['file']
            fremote = basin_maps['remote']['file']
            fhydsim = basin_maps['hydsim']['file']

            # =========== #
            # Engine init #
            # =========== #
            # Give start and enddates growingseasons, classifications
            # to select Harvest Index and Water Content, LU-classification number
            crops = []
            for key, val in fseries['crops'].items():
                crops.append(
                    (os.path.join(pseries, val[0]), val[1], val[2], val[3], val[4])
                )
            # Provide non-crop data, set to None if not available.
            # 'non_crop': {
            #     'meat':        None,
            #     'milk':        None,
            #     'timber':      None,
            #     'aquaculture': None,
            # },
            if fseries['non_crop'] is not None:
                non_crop = {}
                for key, val in fseries['non_crop'].items():
                    non_crop[key] = None
            else:
                non_crop = None
            # 'masks': {
            #     1:(name,fh,[inflow_files],[transfer_files]),
            #     2:(name,fh,[inflow_files],[transfer_files])),
            #     ...
            # }
            masks = {}
            for key, val in fstatic['masks'].items():
                masks[key] = (val[0], os.path.join(pstatic, val[1]), val[2], val[3],
                )
            # meta
            data_meta = {
                'name': basin_name,
                'id': basin_id,

                'alpha_min': basin_para['alpha_min'],
                'recycling_ratio': basin_para['recycling_ratio'],
                'discharge_out_from_wp': basin_para['discharge_out_from_wp'],
                'fraction_xs': basin_para['fraction_xs'],
                'lu_based_supply_split': basin_para['lu_based_supply_split'],
                'grace_supply_split': basin_para['grace_supply_split'],
                'water_year_start_month': basin_para['water_year_start_month'],
                'ndm_max_original': basin_para['ndm_max_original'],
                'grace_split_alpha_bounds': basin_para['grace_split_alpha_bounds'],

                'dico_in': basin_para['dico_in'],
                'dico_out': basin_para['dico_out'],

                # Time series
                'crops': crops,
                'non_crop': non_crop,
                'GRACE': os.path.join(pseries, fseries['GRACE']),
                # Static map
                'lu': os.path.join(pstatic, fstatic['lu']),
                'full_basin_mask': os.path.join(pstatic, fstatic['full_basin_mask']),
                'masks': masks,
            }
            # global
            data_global = {
                'equiped_sw_irrigation': os.path.join(pstatic, fstatic['equiped_sw_irrigation']),
                'wpl_tif': os.path.join(pstatic, fstatic['wpl_tif']),
                'environ_water_req': os.path.join(pstatic, fstatic['environ_water_req']),
                'population_tif': os.path.join(pstatic, fstatic['population_tif']),
                'cattle': os.path.join(pstatic, fstatic['cattle']),
                'dem': os.path.join(pstatic, fstatic['dem']),
                'dir': os.path.join(pstatic, fstatic['dir']) if fstatic['dir'] is not None else None,

                'root_depth': os.path.join(phydsim, fhydsim['root_depth'])
            }
            # maps
            data_maps = {
                'ndm_folder': os.path.join(premote, fremote['ndm']),
                'p_folder': os.path.join(premote, fremote['p']),
                'et_folder': os.path.join(premote, fremote['et']),
                'n_folder': os.path.join(premote, fremote['n']),
                'lai_folder': os.path.join(premote, fremote['lai']),
                'etref_folder': os.path.join(premote, fremote['etref']),

                'bf_folder': os.path.join(phydsim, fhydsim['bf']),
                'sr_folder': os.path.join(phydsim, fhydsim['sr']),
                'tr_folder': os.path.join(phydsim, fhydsim['tr']),
                'perc_folder': os.path.join(phydsim, fhydsim['perc']),
                'dperc_folder': os.path.join(phydsim, fhydsim['dperc']),
                'supply_total_folder': os.path.join(phydsim, fhydsim['supply_total']),
                'dro_folder': os.path.join(phydsim, fhydsim['dro']),
                'etb_folder': os.path.join(phydsim, fhydsim['etb']),
                'etg_folder': os.path.join(phydsim, fhydsim['etg']),
                'rzsm_folder': os.path.join(phydsim, fhydsim['rzsm'])
            }
            # pickle
            fpickle = {
                'init': 'complete_data_init.pickle',
                'sheet46': 'complete_data_sheet46.pickle',
                'sheet2': 'complete_data_sheet2.pickle',
                'sheet3': 'complete_data_sheet3.pickle',
                'sheet5': 'complete_data_sheet5.pickle',
            }
            # ############## #
            # Reproject data #
            # ############## #
            if basin_step['Reproject data']:
                # TODO, 20200622-QPan, Can be replaced by NetCDF
                #  data_complete = {'p': [["D:/"], [2008-01-01]], ... }
                data_complete = hl.sort_data(data_maps, data_meta, data_global, self.path_output)

                # sort_var(data_maps, data_meta, data_global, output_dir, key, data_complete, time_var='time_yyyymm')

                pickle_out = open(os.path.join(self.path_output, data_meta['name'], fpickle['init']), 'wb')
                pickle.dump(data_complete, pickle_out)
                pickle_out.close()
                print('Finish init input maps.\n')
            else:
                if os.path.exists(os.path.join(self.path_output, data_meta['name'], fpickle['init'])):
                    pickle_in = open(os.path.join(self.path_output, data_meta['name'], fpickle['init']), 'rb')
                    data_complete = pickle.load(pickle_in)
                    pickle_in.close()
                else:
                    data_complete = hl.sort_data_short(self.path_output, data_meta)
                print('Finish init input maps.\n')

            # ############# #
            # Sheet 4 and 6 #
            # ############# #
            if basin_step['Create Sheet 4 and 6']:
                data_complete = sh4.supply_return_natural_lu(data_meta, data_complete)

                data_complete = sh4.create_sheet4_6(data_complete, data_meta, self.path_output, data_global)

                pickle_out = open(os.path.join(self.path_output, data_meta['name'], fpickle['sheet46']), 'wb')
                pickle.dump(data_complete, pickle_out)
                pickle_out.close()
                print('Finish sheet46.\n')

            # ####### #
            # Sheet 2 #
            # ####### #
            if basin_step['Create Sheet 2']:
                pickle_in = open(os.path.join(self.path_output, data_meta['name'], fpickle['sheet46']), 'rb')

                data_complete = pickle.load(pickle_in)
                pickle_in.close()

                data_complete = sh2.create_sheet2(data_complete, data_meta, self.path_output)
                pickle_out = open(os.path.join(self.path_output, data_meta['name'], fpickle['sheet2']), 'wb')
                pickle.dump(data_complete, pickle_out)
                pickle_out.close()

            # ####### #
            # Sheet 3 #
            # ####### #
            if basin_step['Create Sheet 3']:
                pickle_in = open(os.path.join(self.path_output, data_meta['name'], fpickle['sheet2']), 'rb')

                data_complete = pickle.load(pickle_in)
                pickle_in.close()

                data_complete = sh3.create_sheet3(data_complete, data_meta, self.path_output)
                pickle_out = open(os.path.join(self.path_output, data_meta['name'], fpickle['sheet3']), 'wb')
                pickle.dump(data_complete, pickle_out)
                pickle_out.close()

            # ####### #
            # Sheet 5 #
            # ####### #
            if basin_step['Create Sheet 5']:
                pickle_in = open(os.path.join(self.path_output, data_meta['name'], fpickle['sheet46']), 'rb')

                data_complete = pickle.load(pickle_in)
                pickle_in.close()

                data_complete = sh5.create_sheet5(data_complete, data_meta, self.path_output, data_global)
                pickle_out = open(os.path.join(self.path_output, data_meta['name'], fpickle['sheet5']), 'wb')
                pickle.dump(data_complete, pickle_out)
                pickle_out.close()

            # Sheet 1
            if basin_step['Create Sheet 1']:
                pickle_in = open(os.path.join(self.path_output, data_meta['name'], fpickle['sheet5']), 'rb')

                data_complete = pickle.load(pickle_in)
                pickle_in.close()

                data_complete, all_sh1_results = sh1.create_sheet1(data_complete, data_meta, self.path_output, data_global)

            # Sheet 7
            if basin_step['Create Sheet 7']:
                pickle_in = open(os.path.join(self.path_output, data_meta['name'], fpickle['sheet5']), 'rb')

                data_complete = pickle.load(pickle_in)
                pickle_in.close()

                data_complete = sh7.create_sheet7(data_complete, data_meta, self.path_output, data_global, data_maps)

        print('End: {}'.format(fun_name))
