# -*- coding: utf-8 -*-
"""
A series of functions to do bulk operations on geotiffs, including
reprojections.

contact: b.coerver@un-ihe.org
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

try:
    import gdal
    import osr
except ImportError:
    from osgeo import gdal, osr
finally:
    gdal.UseExceptions()
# Plot
import matplotlib.pyplot as plt


def get_gdalwarp_info(fih, subdataset=0):
    """
    Get information in string format from a geotiff or HDF4 file for use by GDALWARP.

    Parameters
    ----------
    fih : str
        Filehandle pointing to a geotiff or HDF4 file.
    subdataset = int, optional
        Value indicating a subdataset (in case of HDF4), default is 0.

    Returns
    -------
    srs : str
        The projection of the fih.
    res : str
        Resolution of the fih.
    bbox : str
        Bounding box (xmin, ymin, xmax, ymax) of the fih.
    ndv : str
        No-Data-Value of the fih.
    """
    dataset = gdal.Open(fih, gdal.GA_ReadOnly)

    tpe = dataset.GetDriver().ShortName

    if tpe == 'HDF4':
        dataset = gdal.Open(dataset.GetSubDatasets()[subdataset][0])
    ndv = str(dataset.GetRasterBand(1).GetNoDataValue())

    if ndv == 'None':
        ndv = 'nan'

    srs = dataset.GetProjectionRef()
    if not srs:
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326).ExportToPrettyWkt()
        print("srs not defined, using EPSG4326.")

    xsize = dataset.RasterXSize
    ysize = dataset.RasterYSize

    res = ' '.join([str(xsize), str(ysize)])

    geot = dataset.GetGeoTransform()

    xmin = geot[0]
    ymin = geot[3] + geot[5] * ysize
    xmax = geot[0] + geot[1] * xsize
    ymax = geot[3]

    bbox = ' '.join([str(xmin), str(ymin), str(xmax), str(ymax)])

    return srs, res, bbox, ndv


def match_proj_res_ndv(source_file, target_fihs, output_dir, dtype='Float32'):
    """
    Matches the projection, resolution and no-data-value of a list of target-files
    with a source-file and saves the new maps in output_dir.

    Parameters
    ----------
    source_file : str
        The file to match the projection, resolution and ndv with.
    target_fihs : list
        The files to be reprojected.
    output_dir : str
        Folder to store the output.
    resample : str, optional
        Resampling method to use, default is 'near' (nearest neighbour).
    dtype : str, optional
        Datatype of output, default is 'float32'.
    scale : int, optional
        Multiple all maps with this value, default is None.

    Returns
    -------
    output_files : ndarray
        Filehandles of the created files.
    """
    ndv, xsize, ysize, geot, projection = get_geoinfo(source_file)[1:]

    type_dict = {gdal.GetDataTypeName(i): i for i in range(1, 12)}

    output_files = np.array([])

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for target_file in target_fihs:
        # TODO, 20200525-QPan, Use default GeoTiff, instead of input file extension.
        filename = os.path.split(target_file)[1]

        filename_pre = os.path.splitext(filename)[0]
        filename_ext = os.path.splitext(filename)[-1].lower()

        if filename_ext in ['.tif', '.tiff']:
            filename = '{}{}'.format(filename_pre, filename_ext)
        else:
            # https://gdal.org/drivers/raster/aaigrid.html#raster-aaigrid
            filename = '{}{}'.format(filename_pre, '.tif')

        output_file = os.path.join(output_dir, filename)
        # print('  From "{i}"\n  To   "{o}"'.format(i=target_file, o=output_file))
        options = gdal.WarpOptions(width=xsize,
                                   height=ysize,
                                   outputBounds=(geot[0], geot[3] + ysize * geot[5], geot[0] + xsize * geot[1], geot[3]),
                                   outputBoundsSRS=projection,
                                   dstSRS=projection,
                                   dstNodata=ndv,
                                   outputType=type_dict[dtype])

        # print(output_file, target_file)
        gdal.Warp(output_file, target_file, options=options)

        output_files = np.append(output_files, output_file)

    return output_files


def get_geoinfo(fih, subdataset=0):
    """
    Substract metadata from a geotiff, HDF4 or netCDF file.

    Parameters
    ----------
    fih : str
        Filehandle to file to be scrutinized.
    subdataset : int, optional
        Layer to be used in case of HDF4 or netCDF format, default is 0.

    Returns
    -------
    driver : str
        Driver of the fih.
    ndv : float
        No-data-value of the fih.
    xsize : int
        Amount of pixels in x direction.
    ysize : int
        Amount of pixels in y direction.
    geot : list
        List with geotransform values.
    Projection : str
        Projection of fih.
    """
    sourceds = gdal.Open(fih, gdal.GA_ReadOnly)

    tpe = sourceds.GetDriver().ShortName
    if tpe == 'HDF4' or tpe == 'netCDF':
        sourceds = gdal.Open(sourceds.GetSubDatasets()[subdataset][0])

    ndv = sourceds.GetRasterBand(1).GetNoDataValue()

    xsize = sourceds.RasterXSize
    ysize = sourceds.RasterYSize

    geot = sourceds.GetGeoTransform()

    projection = osr.SpatialReference()
    projection.ImportFromWkt(sourceds.GetProjectionRef())

    driver = gdal.GetDriverByName(tpe)

    return driver, ndv, xsize, ysize, geot, projection


def open_as_array(fih, bandnumber=1, nan_values=True):
    """
    Open a map as an numpy array.

    Parameters
    ----------
    fih: str
        Filehandle to map to open.
    bandnumber : int, optional
        Band or layer to open as array, default is 1.
    dtype : str, optional
        Datatype of output array, default is 'float32'.
    nan_values : boolean, optional
        Convert he no-data-values into np.nan values, note that dtype needs to
        be a float if True. Default is False.

    Returns
    -------
    array : ndarray
        array with the pixel values.
    """
    dataset = gdal.Open(fih, gdal.GA_ReadOnly)

    tpe = dataset.GetDriver().ShortName
    if tpe == 'HDF4':
        subdataset = gdal.Open(dataset.GetSubDatasets()[bandnumber][0])
        ndv = int(subdataset.GetMetadata()['_FillValue'])
    else:
        subdataset = dataset.GetRasterBand(bandnumber)
        ndv = subdataset.GetNoDataValue()

    array = subdataset.ReadAsArray()
    if nan_values:
        if len(array[array == ndv]) > 0:
            array[array == ndv] = np.nan

    return array


def create_geotiff(fih, array, driver, ndv, xsize, ysize, geot, projection, compress=None):
    """
    Creates a geotiff from a numpy array.

    Parameters
    ----------
    fih : str
        Filehandle for output.
    array: ndarray
        array to convert to geotiff.
    driver : str
        Driver of the fih.
    ndv : float
        No-data-value of the fih.
    xsize : int
        Amount of pixels in x direction.
    ysize : int
        Amount of pixels in y direction.
    geot : list
        List with geotransform values.
    Projection : str
        Projection of fih.
    """
    datatypes = {gdal.GetDataTypeName(i).lower(): i for i in range(1, 12)}

    if compress != None:
        dataset = driver.Create(fih, xsize, ysize, 1, datatypes[array.dtype.name], ['COMPRESS={0}'.format(compress)])
    else:
        dataset = driver.Create(fih, xsize, ysize, 1, datatypes[array.dtype.name])

    if ndv is None:
        ndv = -9999

    array[np.isnan(array)] = ndv
    dataset.GetRasterBand(1).SetNoDataValue(ndv)
    dataset.SetGeoTransform(geot)
    dataset.SetProjection(projection.ExportToWkt())
    dataset.GetRasterBand(1).WriteArray(array)
    dataset = None

    if "nt" not in array.dtype.name:
        array[array == ndv] = np.nan


def pixel_coordinates(lon, lat, fih):
    """
    Find the corresponding pixel to a latitude and longitude.

    Parameters
    ----------
    lon : float or int
        Longitude to find.
    lat : float or int
        Latitude to find.
    fih : str
        Filehandle pointing to the file to be searched.

    Returns
    -------
    xpixel : int
        The index of the longitude.
    ypixel : int
        The index of the latitude.
    """
    sourceds = gdal.Open(fih, gdal.GA_ReadOnly)

    xsize = sourceds.RasterXSize
    ysize = sourceds.RasterYSize
    geot = sourceds.GetGeoTransform()

    assert (lon >= geot[0]) & (lon <= geot[0] + xsize * geot[1]), 'longitude is not on the map'
    assert (lat <= geot[3]) & (lat >= geot[3] + ysize * geot[5]), 'latitude is not on the map'

    location = geot[0]
    xpixel = -1
    while location <= lon:
        location += geot[1]
        xpixel += 1

    location = geot[3]
    ypixel = -1
    while location >= lat:
        location += geot[5]
        ypixel += 1

    return xpixel, ypixel


def assert_proj_res_ndv(list_of_filehandle_lists, check_ndv=True):
    """
    Check if the projection, resolution and no-data-value of all provided filehandles are the same.

    Parameters
    ----------
    list_of_filehandle_lists : list
        List with different ndarray containing filehandles to compare.
    check_ndv : boolean, optional
        Check or ignore the no-data-values, default is True.

    Examples
    --------
    >>> assert_proj_res_ndv([et_fihs, ndm_fihs, p_fihs], check_ndv = True)
    """
    longlist = np.array([])
    for fih_list in list_of_filehandle_lists:
        if isinstance(fih_list, list):
            longlist = np.append(longlist, np.array(fih_list))

        if isinstance(fih_list, np.ndarray):
            longlist = np.append(longlist, fih_list)

        if isinstance(fih_list, str):
            longlist = np.append(longlist, np.array(fih_list))

    t_srs, t_ts, t_te, t_ndv = get_gdalwarp_info(longlist[0])
    for fih in longlist[1:]:
        s_srs, s_ts, s_te, s_ndv = get_gdalwarp_info(fih)
        if check_ndv:
            assert np.all([s_ts == t_ts, s_te == t_te, s_srs == t_srs, s_ndv == t_ndv]), "{0} does not have the same Proj/Res/ndv as {1}".format(longlist[0], fih)
        else:
            assert np.all([s_ts == t_ts, s_te == t_te, s_srs == t_srs]), "{0} does not have the same Proj/Res as {1}".format(longlist[0], fih)


