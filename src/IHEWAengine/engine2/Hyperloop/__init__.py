# -*- coding: utf-8 -*-
"""
"""

__version__ = '0.0.1'

try:
    from .ihewaengine import Engine
except ImportError:
    from IHEWAengine.engine2.Hyperloop.ihewaengine import Engine
__all__ = ['Engine']
