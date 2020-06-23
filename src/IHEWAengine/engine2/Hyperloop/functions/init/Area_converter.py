# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Start
"""
# Builtins
from __future__ import division

from builtins import str

import os
# Math
import numpy as np
# Self
try:
    from ...general import raster_conversions as hyperloop_rc
except ImportError:
    from IHEWAengine.engine2.Hyperloop.general import raster_conversions as RC


def Degrees_to_m2(reference_data):
    """
    This functions calculated the area of each pixel in squared meter.

    Parameters
    ----------
    reference_data: str
        Path to a tiff file or nc file or memory file of which the pixel area must be defined

    Returns
    -------
    area_in_m2: array
        Array containing the area of each pixel in squared meters

    """
    try:
        # Get the extension of the example data
        filename, file_extension = os.path.splitext(reference_data)

        # Get raster information
        if str(file_extension) == '.tif':
            geo_out, proj, size_x, size_y = RC.Open_array_info(reference_data)
        elif str(file_extension) == '.nc':
            geo_out, epsg, size_x, size_y, size_z, time = RC.Open_nc_info(
                reference_data)

    except:
        geo_out = reference_data.GetGeoTransform()
        size_x = reference_data.RasterXSize()
        size_y = reference_data.RasterYSize()

    # Calculate the difference in latitude and longitude in meters
    dlat, dlon = Calc_dlat_dlon(geo_out, size_x, size_y)

    # Calculate the area in squared meters
    area_in_m2 = dlat * dlon

    return area_in_m2


def Calc_dlat_dlon(geo_out, size_x, size_y):
    """
    This functions calculated the distance between each pixel in meter.

    Parameters
    ----------
    geo_out: array
        geo transform function of the array
    size_x: int
        size of the X axis
    size_y: int
        size of the Y axis

    Returns
    -------
    dlat: array
        Array containing the vertical distance between each pixel in meters
    dlon: array
        Array containing the horizontal distance between each pixel in meters
    """

    # Create the lat/lon rasters
    lon = np.arange(size_x + 1) * geo_out[1] + geo_out[0] - 0.5 * geo_out[1]
    lat = np.arange(size_y + 1) * geo_out[5] + geo_out[3] - 0.5 * geo_out[5]

    dlat_2d = np.array([lat, ] * int(np.size(lon, 0))).transpose()
    dlon_2d = np.array([lon, ] * int(np.size(lat, 0)))

    # Radius of the earth in meters
    R_earth = 6371000

    # Calculate the lat and lon in radians
    lonRad = dlon_2d * np.pi / 180
    latRad = dlat_2d * np.pi / 180

    # Calculate the difference in lat and lon
    lonRad_dif = abs(lonRad[:, 1:] - lonRad[:, :-1])
    latRad_dif = abs(latRad[:-1] - latRad[1:])

    # Calculate the distance between the upper and lower pixel edge
    a = np.sin(latRad_dif[:, :-1] / 2) * np.sin(latRad_dif[:, :-1] / 2)
    clat = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a));
    dlat = R_earth * clat

    # Calculate the distance between the eastern and western pixel edge
    b = np.cos(latRad[1:, :-1]) * np.cos(latRad[:-1, :-1]) * np.sin(
        lonRad_dif[:-1, :] / 2) * np.sin(lonRad_dif[:-1, :] / 2)
    clon = 2 * np.arctan2(np.sqrt(b), np.sqrt(1 - b));
    dlon = R_earth * clon

    return dlat, dlon
