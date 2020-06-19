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

    from . import sheet1_functions as sh1
    from . import sheet2_functions as sh2
    from . import sheet3_functions as sh3
    from . import sheet4_functions as sh4
    from . import sheet5_functions as sh5
    from . import sheet7_functions as sh7
    from . import hyperloop as hl
except ImportError:
    from IHEWAengine.engine2.Hyperloop import ihewaengine_pkg_version

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
        self.version = 'v{}'.format(ihewaengine_pkg_version.__version__)

        self.__conf = conf

        self.pout = self.__conf['folder']['engine2']['res']
        print(self.pout)

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
                'output': {}
            }
        }

        self._conf()

        if self.__status['code'] == 0:
            self.run()

    def _conf(self):
        # fun_name = inspect.currentframe().f_code.co_name

        f_in = os.path.join(self.__conf['workspace'],
                            self.conf['path'],
                            self.conf['fname'])

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
            basin_id = basin_val['id']
            basin_para = basin_val['parameter']
            basin_series = basin_val['series']
            path = {
                'series': os.path.join(self.pout, basin_series['path']),
                'static': os.path.join(self.pout, basin_maps['static']['path']),
                'remote': os.path.join(self.pout, basin_maps['remote']['path']),
                'hydsim': os.path.join(self.pout, basin_maps['hydsim']['path']),
            }

            print('\t{}'.format(basin_name))
            for pkey, pval in path.items():
                print('\t\t{}: {}'.format(pkey, pval))

        print('End: {}'.format(fun_name))



