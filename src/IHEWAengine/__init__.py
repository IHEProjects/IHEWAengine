# -*- coding: utf-8 -*-
"""
IHEengine: IHE Water Accounting Engine Tools
"""


from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'IHEengine'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound

try:
    from .engine import Engine
except ImportError:
    from IHEengine.engine import Engine
__all__ = ['Engine']

# TODO, 20190931, QPan,
