# -*- coding: utf-8 -*-
"""
`Document structure <https://en.wikibooks.org/wiki/LaTeX/Document_Structure>`_

"""
# Builtins
import inspect
import os
from datetime import datetime, date
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
    # IHEClassInitError, IHEStringError, IHETypeError, IHEKeyError, IHEFileError
    from ...exception import IHEClassInitError
except ImportError:
    from IHEWAengine.exception import IHEClassInitError


class Engine(object):
    """This Engine class

    Load base.yml file.

    Args:
        conf (dict): User defined configuration data from yaml file.
    """
    def __init__(self, conf):
        """Class instantiation
        """
        template = 'ihewaengine.yml'

        install_path = os.path.dirname(__file__)
        print(install_path)
