# -*- coding: utf-8 -*-
"""
"""

__version__ = '0.1'

try:
    from .ihewaengine import Engine
except ImportError:
    from IHEWAengine.engine1.ETmonitor.ihewaengine import Engine
__all__ = ['Engine']
