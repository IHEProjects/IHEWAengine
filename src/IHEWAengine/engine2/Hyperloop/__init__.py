# -*- coding: utf-8 -*-
"""
Hyperloop, develooped by IHE Water Accounting team.

"""

from . import ihewaengine_pkg_version

__version__ = ihewaengine_pkg_version.__version__

try:
    from .ihewaengine import Engine
except ImportError:
    from IHEWAengine.engine2.Hyperloop.ihewaengine import Engine
__all__ = ['Engine']
