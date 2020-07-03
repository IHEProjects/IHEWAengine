# -*- coding: utf-8 -*-
"""
"""
# Builtins
import os
# Math
import numpy as np
# Self
try:
    from .. import spatial
except ImportError:
    from IHEWAengine.engine2.Hyperloop import spatial


def sw_ret_wpix(non_consumed_dsro, non_consumed_dperc, lu, ouput_dir_ret_frac):
    DSRO = spatial.basic.open_as_array(non_consumed_dsro, nan_values=True)
    DPERC = spatial.basic.open_as_array(non_consumed_dperc, nan_values=True)
    DSRO[np.isnan(DSRO)] = 0
    DPERC[np.isnan(DPERC)] = 0

    LU = spatial.basic.open_as_array(lu, nan_values=True)

    DTOT = DSRO + DPERC

    SWRETFRAC = LU * 0
    SWRETFRAC[DTOT > 0] = (DSRO / (DTOT))[DTOT > 0]

    geo_info = spatial.basic.get_geoinfo(non_consumed_dsro)

    fh = os.path.join(ouput_dir_ret_frac, 'sw_return_fraction' + os.path.basename(non_consumed_dsro)[-13:])
    spatial.basic.create_geotiff(fh, SWRETFRAC, *geo_info)
    return fh
