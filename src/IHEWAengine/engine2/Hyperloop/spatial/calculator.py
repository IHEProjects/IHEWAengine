# -*- coding: utf-8 -*-
"""
"""


def map_pixel_area_km(fih, approximate_lengths=False):
    """
    Calculate the area of the pixels in a geotiff.

    Parameters
    ----------
    fih : str
        Filehandle pointing to a geotiff.
    approximate_lengths : boolean, optional
        Give the approximate length per degree [km/deg] instead of the area [km2], default is False.

    Returns
    -------
    map_area : ndarray
        The area per cell.
    """
    xsize, ysize, geot = get_geoinfo(fih)[2:-1]
    area_column = np.zeros((ysize, 1))
    for y_pixel in range(ysize):
        pnt1 = (geot[3] + y_pixel * geot[5], geot[0])
        pnt2 = (pnt1[0], pnt1[1] + geot[1])
        pnt3 = (pnt1[0] - geot[1], pnt1[1])
        pnt4 = (pnt1[0] - geot[1], pnt1[1] + geot[1])

        u = distance.distance(pnt1, pnt2).km
        l = distance.distance(pnt3, pnt4).km
        h = distance.distance(pnt1, pnt3).km

        area_column[y_pixel, 0] = (u + l) / 2 * h

    map_area = np.repeat(area_column, xsize, axis=1)

    if approximate_lengths:
        pixel_approximation = np.sqrt(abs(geot[1]) * abs(geot[5]))

        map_area = np.sqrt(map_area) / pixel_approximation

    return map_area


def mean_std(fihs):
    """
    Calculate the mean and the standard deviation per pixel for a serie of maps.

    Parameters
    ----------
    fihs : ndarray
        Array with filehandles pointing to maps to be used.

    Returns
    -------
    std : ndarray
        Array with the standard deviation for each pixel.
    mean : ndarray
        Array with the mean for each pixel.
    """
    data_sum = data_count = np.zeros_like(open_as_array(fihs[0]))

    for fih in fihs:
        data = open_as_array(fih)
        data_sum = np.nansum([data_sum, data], axis=0)

        count = np.ones_like(data)
        count[np.isnan(data)] = 0
        data_count += count

    mean = data_sum / data_count
    data_sum = np.zeros_like(data)

    for fih in fihs:
        data = (open_as_array(fih) - mean) ** 2 / data_count
        data_sum += data

    std = np.sqrt(data_sum)

    return std, mean


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


def series_average(tifs, dates, length, output_folder, para_name='Average', categories=None, lu_fih=None, timescale='months'):
    """
    Compute moving averages for multiple maps.

    Parameters
    ----------
    tifs : ndarray
        Array of strings pointing to maps.
    dates : ndarray
        Array with datetime.date object referring to the dates of tifs.
    length : dict or int
        Length of moving average. When dictionary, different lengths can be used for different
        landuse categories.
    output_folder : str
        Folder to store results.
    para_name : str, optional
        Name used for output tifs. Default is 'Average'.
    categories : dict, optional
        Dictionary describing the different landuse categories, keys should be identical to keys
        in length. Default is None.
    lu_fih : str, optional
        Landuse map, default is None.
    timescale : str, optional
        Timescale of the maps in tifs. Default is 'months'.

    Returns
    -------
    output_tifs : ndarray
        Array with paths to the new maps.
    dates : ndarray
        Array with datetime.date object reffering to the dates of output_tifs.
    """
    assert_missing_dates(dates, timescale=timescale)

    masked_average = False

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if isinstance(length, dict):
        max_length = np.max(length.values())

        masked_average = True

        assert_same_keys([length, categories])
        assert_proj_res_ndv([tifs, np.array(lu_fih)])
    else:
        max_length = length

        assert_proj_res_ndv([tifs])

    geo_info = get_geoinfo(tifs[0])

    output_tifs = np.array([])

    for date in dates[(max_length - 1):]:
        if masked_average:
            array = masked_moving_average(date, tifs, dates, lu_fih, length, categories)

        if not masked_average:
            array = moving_average(date, tifs, dates, moving_avg_length=length)

        tif = os.path.join(output_folder, '{0}_{1}{2}.tif'.format(para_name, date.year, str(date.month).zfill(2)))

        create_geotiff(tif, array, *geo_info)

        output_tifs = np.append(output_tifs, tif)

    return output_tifs, dates[(max_length - 1):]


def moving_average(date, filehandles, filedates, moving_avg_length=5, method='tail'):
    """
    Compute a moving (tail) average from a series of maps.

    Parameters
    ----------
    date : object
        Datetime.date object for which the average should be computed
    filehandles : ndarray
        Filehandles of the maps.
    filedates : ndarray
        Datetime.date objects corresponding to filehandles
    moving_average_length : int, optional
        Length of the tail, default is 3.
    method : str, optional
        Select wether to calculate the 'tail' average or 'central' average.

    Returns
    -------
    summed_data : ndarray
        The averaged data.
    """
    indice = np.where(filedates == date)[0][0]

    if method == 'tail':
        assert (indice + 1) >= moving_avg_length, "Not enough data available to calculate average of length {0}".format(moving_avg_length)

        to_open = filehandles[indice - (moving_avg_length - 1):(indice + 1)]
    elif method == 'central':
        assert (moving_avg_length % 2 != 0), "Please provide an uneven moving_avg_length"
        assert indice >= (moving_avg_length - 1) / 2, "Not enough data available to calculate central average of length {0}".format(moving_avg_length)
        assert indice < len(filedates) - (moving_avg_length - 1) / 2, "Not enough data available to calculate central average of length {0}".format(moving_avg_length)

        to_open = filehandles[indice - (moving_avg_length - 1) / 2:indice + (moving_avg_length - 1) / 2 + 1]

    summed_data = open_as_array(filehandles[indice]) * 0

    for fih in to_open:
        data = open_as_array(fih)
        summed_data += data
    summed_data /= len(to_open)

    return summed_data


def moving_average_masked(date, fihs, dates, lu_fih, moving_avg_length, categories, method='tail'):
    """
    Calculate temporal trailing averages dependant on landuse categories.

    Parameters
    ----------
    date : object
        datetime.date object indicating for which month the average needs to be calculated.
    fihs : ndarray
        Array with filehandles pointing to maps.
    dates : ndarray
        Array with datetime.date objects referring to the maps in fihs.
    lu_fih : str
        Filehandle pointing to a landusemaps.
    moving_avg_length : dict
        Dictionary indicating the number of months needed to calculate the temporal
        trailing average.
    categories : dict
        Dictionary indicating which landuseclasses belong to which category. Should
        have the same keys as moving_avg_length.

    Returns
    -------
    AVG : ndarray
        Array with the averaged values.
    """

    # https://stackoverflow.com/a/40857703/4288201
    def flatten(l):
        for el in l:
            if isinstance(el, collections.Iterable) and not isinstance(el, str):
                for sub in flatten(el):
                    yield sub
            else:
                yield el

    assert_same_keys([moving_avg_length, categories])

    lulc = open_as_array(lu_fih)

    xsize, ysize = get_geoinfo(lu_fih)[2:4]

    avg = np.zeros((ysize, xsize)) * np.nan

    for length in np.unique(moving_avg_length.values()):
        key_list = [key for key in moving_avg_length.keys() if moving_avg_length[key] is int(length)]

        classes = list(flatten([categories[key] for key in key_list]))

        mask = np.logical_or.reduce([lulc == value for value in classes])

        avg[mask] = moving_average(date, fihs, dates, moving_avg_length=length, method=method)[mask]

    return avg
