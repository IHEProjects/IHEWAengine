# -*- coding: utf-8 -*-

import pytest

import os

# IHEWAcollect Modules
import IHEWAengine

__author__ = "Quan Pan"
__copyright__ = "Quan Pan"
__license__ = "apache"

__path = os.path.dirname(os.path.realpath(__file__))
__path_data = os.path.join(__path, 'data')


def test_Hyperloop():
    path = __path

    engine = IHEWAengine.Engine(path, 'test_engine.yml')

# import inspect
# import os
#
# import yaml
# import fnmatch
# import pandas as pd
#
# import IHEWAengine
#
#
if __name__ == "__main__":
    print('\nEngine\n=====')
    test_Hyperloop()
#
#     path = os.path.join(
#         os.getcwd(),
#         os.path.dirname(
#             inspect.getfile(
#                 inspect.currentframe()))
#     )
#     print(path)
#
#     # path = os.path.dirname(os.path.abspath(__file__))
#     # print(path)
#
#     engine = IHEWAengine.Engine(path, 'test_engine.yml')
#     # print(engine._Engines__conf)
