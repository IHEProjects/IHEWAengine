# -*- coding: utf-8 -*-
"""
`Document structure <https://en.wikibooks.org/wiki/LaTeX/Document_Structure>`_

"""
import inspect
import os
from datetime import datetime, date
import yaml

import matplotlib
# Not to use X server. For TravisCI.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

from pylatex import \
    Package, Document, Command, NoEscape, \
    PageStyle, Head, Foot, \
    Section, Subsection, Subsubsection, NewPage, NewLine, LineBreak, \
    Itemize, \
    Label, Ref, \
    LongTabu, LongTable, MultiColumn, MultiRow, Table, Tabular, \
    TikZ, Axis, Plot, Figure, SubFigure, Alignat, \
    Math, Matrix, VectorName, Quantity
from pylatex.utils import italic, bold, make_temp_dir, rm_temp_dir

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
        print(template, conf)
