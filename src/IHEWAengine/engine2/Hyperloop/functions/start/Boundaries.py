# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 09:22:07 2017

@author: tih
"""
# Builtins
from __future__ import print_function

import os
# Math
import numpy as np
# GIS
try:
    import gdal
except ImportError:
    from osgeo import gdal
import shapefile


def Determine(basin, home_folder):
    shape_file_name_shp = os.path.join(home_folder, 'Basins', basin + '.shp')
    if not os.path.exists(shape_file_name_shp):
        print('%s is missing' % shape_file_name_shp)
    shape_file_name_dbf = os.path.join(home_folder, 'Basins', basin + '.dbf')
    if not os.path.exists(shape_file_name_dbf):
        print('%s is missing' % shape_file_name_dbf)

    basin_shp = shapefile.Reader(shape_file_name_shp, shape_file_name_dbf)
    shapes = basin_shp.shapes()
    bbox = shapes[0].bbox
    boundaries = dict()
    # boundaries['Lonmin'] = np.floor(bbox[0]) - 0.1
    # boundaries['Lonmax'] = np.ceil(bbox[2]) + 0.1
    # boundaries['Latmin'] = np.floor(bbox[1]) - 0.1
    # boundaries['Latmax'] = np.ceil(bbox[3]) + 0.1
    boundaries['Lonmin'] = round(np.floor((bbox[0] * 10.) - 1.)) / 10.
    boundaries['Lonmax'] = round(np.ceil((bbox[2] * 10.) + 1.)) / 10.
    boundaries['Latmin'] = round(np.floor((bbox[1] * 10.) - 1.)) / 10.
    boundaries['Latmax'] = round((np.ceil(bbox[3] * 10.) + 1.)) / 10.
    return boundaries, shape_file_name_shp


def Determine_LU_Based(file_LU, home_folder):
    #    file_LU = os.path.join(home_folder,'LU', basin + '.tif')
    if not os.path.exists(file_LU):
        print('%s is missing' % file_LU)

    dest = gdal.Open(file_LU)
    Transform = dest.GetGeoTransform()
    sizeX = dest.RasterXSize
    sizeY = dest.RasterYSize

    # boundaries['Lonmin'] = np.floor(bbox[0]) - 0.1
    # boundaries['Lonmax'] = np.ceil(bbox[2]) + 0.1
    # boundaries['Latmin'] = np.floor(bbox[1]) - 0.1
    # boundaries['Latmax'] = np.ceil(bbox[3]) + 0.1
    boundaries = dict()
    boundaries['Lonmin'] = round(np.floor((Transform[0] * 10.) - 1.)) / 10.
    boundaries['Lonmax'] = round(
        np.ceil(((Transform[0] + sizeX * Transform[1]) * 10.) + 1.)) / 10.
    boundaries['Latmin'] = round(
        np.floor(((Transform[3] + sizeY * Transform[5]) * 10.) - 1.)) / 10.
    boundaries['Latmax'] = round((np.ceil(Transform[3] * 10.) + 1.)) / 10.

    return boundaries, file_LU
