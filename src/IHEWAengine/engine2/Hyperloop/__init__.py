# -*- coding: utf-8 -*-
"""
Hyperloop, develooped by IHE Water Accounting team.

"""

__version__ = '0.0.1'

try:
    from .ihewaengine import Engine
except ImportError:
    from IHEWAengine.engine2.Hyperloop.ihewaengine import Engine
__all__ = ['Engine']
