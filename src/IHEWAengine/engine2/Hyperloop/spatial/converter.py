# -*- coding: utf-8 -*-
"""
"""
# Builtins
from __future__ import print_function

import os
import subprocess
import collections
import datetime
import calendar
from dateutil.relativedelta import relativedelta

import csv

# Math
import numpy as np
# GIS
from geopy import distance
# Self
# Self
try:
    from . import data_conversions as DC
    from . import raster_conversions as RC
except ImportError:
    from IHEWAengine.engine2.Hyperloop.general import data_conversions as DC
    from IHEWAengine.engine2.Hyperloop.general import raster_conversions as RC
try:
    from .spatial.basic import open_as_array, get_geoinfo, create_geotiff
except ImportError:
    from IHEWAengine.engine2.Hyperloop.spatial.basic import open_as_array, get_geoinfo, create_geotiff


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


def mm_to_km3(lu_fih, var_fihs):
    """
    Convert the unit of a series of maps from mm to km3.

    Parameters
    ----------
    lu_fih : str
        Filehandle pointing to georeferenced tiff raster map.
    fihs : ndarray
        Array with filehandles pointing to maps to be used.

    Returns
    -------
    var_new_fhs : ndarray
        Array with filehandles pointing to output maps.
    """
    area = map_pixel_area_km(lu_fih)

    geo_info = get_geoinfo(lu_fih)

    var_new_fihs = np.array()
    for var_fih in var_fihs:
        var = open_as_array(var_fih)

        var_area = (var * area) / 1e6
        var_new_fih = var_fih.replace('.tif', '_km3.tif')

        create_geotiff(var_new_fih, var_area, *geo_info)

        var_new_fihs = np.append(var_new_fihs, var_new_fih)

    return var_new_fihs


def convert_to_tif(z, lat, lon, output_fh, gdal_grid_path=r'C:\Program Files\QGIS 2.18\bin\gdal_grid.exe'):
    """
    Create a geotiff with WGS84 projection from three arrays specifying (x,y,z)
    values.

    Parameters
    ----------
    z : ndarray
        Array containing the z-values.
    lat : ndarray
        Array containing the latitudes (in decimal degrees) corresponding to
        the z-values.
    lon : ndarray
        Array containing the latitudes (in decimal degrees) corresponding to
        the z-values.
    output_fh : str
        String defining the location for the output file.
    gdal_grid_path : str
        Path to the gdal_grid executable.
    """
    folder, filen = os.path.split(output_fh)

    if not os.path.exists(folder):
        os.chdir(folder)

    if np.all([lat.ndim == 2, lon.ndim == 2, z.ndim == 2]):
        csv_path = os.path.join(folder, 'temp.csv')
        with open(csv_path, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

            spamwriter.writerow(['Easting', 'Northing', 'z'])

            for xindex in range(np.shape(lat)[0]):
                for yindex in range(np.shape(lat)[1]):
                    spamwriter.writerow([lon[xindex, yindex], lat[xindex, yindex], z[xindex, yindex]])

    elif np.all([lat.ndim == 1, lon.ndim == 1, z.ndim == 1]):
        csv_path = os.path.join(folder, 'temp.csv')
        with open(csv_path, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

            spamwriter.writerow(['Easting', 'Northing', 'z'])

            for xindex in range(np.shape(lat)[0]):
                spamwriter.writerow([lon[xindex], lat[xindex], z[xindex]])

    else:
        raise ValueError("convert_to_tif is not compatible with the given \
                         dimensions of z, lat and lon.")

    vrt_path = os.path.join(folder, 'temp.vrt')
    with open(vrt_path, "w") as filen:
        filen.write('<OGRVRTDataSource>')
        filen.write('\n\t<OGRVRTLayer name="temp">')
        filen.write('\n\t\t<SrcDataSource>{0}</SrcDataSource>'.format(csv_path))
        filen.write('\n\t\t<GeometryType>wkbPoint</GeometryType>')
        filen.write('\n\t\t<GeometryField encoding="PointFromColumns" x="Easting" y="Northing" z="z"/>')
        filen.write('\n\t</OGRVRTLayer>')
        filen.write('\n</OGRVRTDataSource>')

    string = [gdal_grid_path,
              '-a_srs "+proj=longlat +datum=WGS84 +no_defs "',
              '-of GTiff',
              '-l temp',
              '-a linear:radius={0}:nodata=-9999'.format(np.max([np.max(np.diff(lon)), np.max(np.diff(lat))])),
              vrt_path,
              output_fh]

    proc = subprocess.Popen(' '.join(string), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    print(out, err)

    os.remove(csv_path)
    os.remove(vrt_path)


def classe_to_value(fih, lu_fih, classes, value):
    """
    Open a rasterfile and change certain pixels to a new value. Classes and
    lu_fih is used to create a mask. The mask is then used to set the pixel values
    in fih to value.

    Parameters
    ----------
    fih : str
        Filehandle pointing to georeferenced tiff raster map.
    lu_fih : str
        Filehandle pointing to georeferenced tiff raster map. Should have same
        dimensions as fih.
    classes : list
        List with values, the values are looked up in lu_fih, the corresponding
        pixels in fih are then changed.
    value : float or int
        Value to change the pixelvalues in fih into.
    """
    alpha = open_as_array(fih, nan_values=True)
    lulc = open_as_array(lu_fih, nan_values=True)

    mask = np.logical_or.reduce([lulc == x for x in classes])

    alpha[mask] = value

    geo_info = get_geoinfo(lu_fih)

    create_geotiff(fih, alpha, *geo_info)
