# -*- coding: utf-8 -*-
"""

"""
# Builtins
from __future__ import print_function

import os
import glob
import calendar
# Math
import numpy as np
import pandas as pd

# GIS
try:
    import gdal
except ImportError:
    from osgeo import gdal
# Self
try:
    from . import data_conversions as DC
    from . import raster_conversions as RC
except ImportError:
    from IHEWAengine.engine2.Hyperloop.general import data_conversions as DC
    from IHEWAengine.engine2.Hyperloop.general import raster_conversions as RC


def datetime_to_date(dates, out=None):
    """
    Convert datetime.datetime objects into datetime.date objects or viceversa.

    Parameters
    ----------
    dates : ndarray or list
        List of datetime.datetime objects.
    out : str or None, optional
        string can be either 'date' or 'datetime', if out is not None, the output will always
        be date or datetime, regardless of the type of input.

    Returns
    -------
    dates : ndarray
        Array with datetime.date objects.
    """
    if out == 'date':
        dates = np.array([datetime.date(dt.year, dt.month, dt.day) for dt in dates])
    elif out == 'datetime':
        dates = np.array([datetime.datetime(date.year, date.month, date.day, 0, 0, 0) for date in dates])
    else:
        if isinstance(dates[0], datetime.datetime):
            dates = np.array([datetime.date(dt.year, dt.month, dt.day) for dt in dates])
        elif isinstance(dates[0], datetime.date):
            dates = np.array([datetime.datetime(date.year, date.month, date.day, 0, 0, 0) for date in dates])

    return dates


def xdaily_to_monthly(files, dates, out_path, name_out):
    r"""

    Parameters
    ----------
    fihs : ndarray
        Array with filehandles pointing to maps.
    dates : ndarray
        Array with datetime.date objects referring to the maps in fihs.
    out_path : str
        Folder to save results.
    name_out : str
        Output files naming convention, add curly brackets to indicate
        where the year and month should be placed, e.g. r'LAI_{0}{1}.tif'
    """

    # Make sure the fiels and dates are sequential
    files = np.array([x for _, x in sorted(zip(dates, files))])
    dates = np.array(sorted(dates))

    # Check if out_path exists
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    # Check if all maps have the same projection
    assert_proj_res_ndv([files])

    # Get geo-info
    geo_info = get_geoinfo(files[0])

    # Create tuples with date couples
    date_couples = np.array(zip(dates[0:-1], dates[1:]))

    # Loop over years and months
    for yyyy, month in np.unique([(date.year, date.month) for date in dates], axis=0):

        # Check which maps are relevant for current step
        relevant = [np.any([date1.month == month and date1.year == yyyy,
                            date2.month == month and date2.year == yyyy]) for date1, date2 in date_couples]

        # Create new empty array
        monthly = np.zeros((geo_info[3], geo_info[2]), dtype=np.float32)

        # Calculate length of month
        days_in_month = calendar.monthrange(yyyy, month)[1]

        # Loop over relevant dates
        for date1, date2 in date_couples[relevant]:

            print(date1, date2)

            # Open relevant maps
            xdaily1 = open_as_array(files[dates == date1][0])
            xdaily2 = open_as_array(files[dates == date2][0])

            # Correct dateranges at month edges
            if np.any([date1.month != month, date1.year != yyyy]):
                date1 = datetime.date(yyyy, month, 1)

            if np.any([date2.month != month, date2.year != yyyy]):
                date2 = datetime.date(yyyy, month, days_in_month) + datetime.timedelta(days=1)

            # Calculate how many relevant days there are in the current substep
            relevant_days = (date2 - date1).days

            # Add values to map
            monthly += np.sum([xdaily1, xdaily2], axis=0) * 0.5 * relevant_days

            print(date1, date2)
            print(relevant_days)

        # Calculate monthly average
        monthly /= days_in_month

        # Create output filehandle
        out_fih = os.path.join(out_path, name_out.format(yyyy, str(month).zfill(2)))

        # Save array as geotif
        create_geotiff(out_fih, monthly, *geo_info, compress="LZW")

        print("{0} {1} Created".format(yyyy, month))


def Day_to_Mnoth(Dir_in, Startdate, Enddate, Dir_out=None):
    """
    This functions calculates monthly tiff files based on the daily tiff files.
    (will calculate the total sum)

    Parameters
    ----------
    Dir_in : str
        Path to the input data
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'
    Dir_out : str
        Path to the output data, default is same as Dir_in
    """
    # Change working directory
    os.chdir(Dir_in)

    # Find all monthly files
    files = glob.glob('*daily*.tif')

    # Define end and start date
    Dates = pd.date_range(Startdate, Enddate, freq='MS')

    # Get array information and define projection
    geo_out, proj, size_X, size_Y = RC.Open_array_info(files[0])
    if int(proj.split('"')[-2]) == 4326:
        proj = "WGS84"

    # Get the No Data Value
    dest = gdal.Open(files[0])
    NDV = dest.GetRasterBand(1).GetNoDataValue()

    # Define output directory
    if Dir_out is None:
        Dir_out = Dir_in

    if not os.path.exists(Dir_out):
        os.makedirs(Dir_out)

    # loop over the months and sum the days
    for date in Dates:
        Year = date.year
        Month = date.month
        files_one_year = glob.glob('*daily*%d.%02d*.tif' % (Year, Month))

        # Create empty arrays
        Month_data = np.zeros([size_Y, size_X])

        # Get amount of days in month
        Amount_days_in_month = int(calendar.monthrange(Year, Month)[1])

        if len(files_one_year) is not Amount_days_in_month:
            print("One day is missing!!! month %s year %s" % (Month, Year))

        for file_one_year in files_one_year:
            file_path = os.path.join(Dir_in, file_one_year)

            Day_data = RC.Open_tiff_array(file_path)
            Day_data[np.isnan(Day_data)] = 0.0
            Day_data[Day_data == -9999] = 0.0
            Month_data += Day_data

        # Define output name
        output_name = os.path.join(Dir_out, file_one_year.replace('daily', 'monthly').replace('day', 'month'))

        output_name = output_name[:-14] + '%d.%02d.01.tif' % (date.year, date.month)

        # Save tiff file
        DC.Save_as_tiff(output_name, Month_data, geo_out, proj)


def Day8_to_Mnoth(Dir_in, Startdate, Enddate, Dir_out=None):
    """ 8 Daily to Monthly State

    :param Dir_in:
    :param Startdate:
    :param Enddate:
    :param Dir_out:
    :return:
    """
    # Change working directory
    os.chdir(Dir_in)

    # Find all eight daily files
    files = glob.glob('*8-daily*.tif')

    # Create array with filename and keys (DOY and year) of all the 8 daily files
    i = 0
    DOY_Year = np.zeros([len(files), 3])
    for File in files:
        # Get the time characteristics from the filename
        year = File.split('.')[-4][-4:]
        month = File.split('.')[-3]
        day = File.split('.')[-2]

        # Create pandas Timestamp
        date_file = '%s-%02s-%02s' % (year, month, day)
        Datum = pd.Timestamp(date_file)

        # Get day of year
        DOY = Datum.strftime('%j')

        # Save data in array
        DOY_Year[i, 0] = i
        DOY_Year[i, 1] = DOY
        DOY_Year[i, 2] = year

        # Loop over files
        i += 1

    # Check enddate:
    Enddate_split = Enddate.split('-')
    month_range = calendar.monthrange(int(Enddate_split[0]), int(Enddate_split[1]))[1]
    Enddate = '%d-%02d-%02d' % (
        int(Enddate_split[0]), int(Enddate_split[1]), month_range)

    # Check startdate:
    Startdate_split = Startdate.split('-')
    Startdate = '%d-%02d-01' % (int(Startdate_split[0]), int(Startdate_split[1]))

    # Define end and start date
    Dates = pd.date_range(Startdate, Enddate, freq='MS')
    DatesEnd = pd.date_range(Startdate, Enddate, freq='M')

    # Get array information and define projection
    geo_out, proj, size_X, size_Y = RC.Open_array_info(files[0])
    if int(proj.split('"')[-2]) == 4326:
        proj = "WGS84"

    # Get the No Data Value
    dest = gdal.Open(files[0])
    NDV = dest.GetRasterBand(1).GetNoDataValue()

    # Loop over months and create monthly tiff files
    i = 0
    for date in Dates:
        # Get Start and end DOY of the current month
        DOY_month_start = date.strftime('%j')
        DOY_month_end = DatesEnd[i].strftime('%j')

        # Search for the files that are between those DOYs
        year = date.year
        DOYs = DOY_Year[DOY_Year[:, 2] == year]
        DOYs_oneMonth = DOYs[np.logical_and((DOYs[:, 1] + 8) >= int(DOY_month_start), DOYs[:, 1] <= int(DOY_month_end))]

        # Create empty arrays
        Monthly = np.zeros([size_Y, size_X])
        Weight_tot = np.zeros([size_Y, size_X])
        Data_one_month = np.ones([size_Y, size_X]) * np.nan

        # Loop over the files that are within the DOYs
        for EightDays in DOYs_oneMonth[:, 1]:

            # Calculate the amount of days in this month of each file
            Weight = np.ones([size_Y, size_X])

            # For start of month
            if np.min(DOYs_oneMonth[:, 1]) == EightDays:
                Weight = Weight * int(EightDays + 8 - int(DOY_month_start))

            # For end of month
            elif np.max(DOYs_oneMonth[:, 1]) == EightDays:
                Weight = Weight * (int(DOY_month_end) - EightDays + 1)

            # For the middle of the month
            else:
                Weight = Weight * 8

            row = DOYs_oneMonth[np.argwhere(DOYs_oneMonth[:, 1] == EightDays)[0][0], :][0]

            # Open the array of current file
            input_name = os.path.join(Dir_in, files[int(row)])
            Data = RC.Open_tiff_array(input_name)

            # Remove NDV
            Weight[Data == NDV] = 0
            Data[Data == NDV] = np.nan

            # Multiply weight time data
            Data = Data * Weight

            # Calculate the total weight and data
            Weight_tot += Weight
            Monthly[~np.isnan(Data)] += Data[~np.isnan(Data)]

        # Go to next month
        i += 1

        # Calculate the average
        Data_one_month[Weight_tot != 0.] = Monthly[Weight_tot != 0.] / Weight_tot[
            Weight_tot != 0.]

        # Define output directory
        if Dir_out == None:
            Dir_out = Dir_in

        # Define output name
        output_name = os.path.join(Dir_out, files[int(row)].replace('8-daily', 'monthly'))
        output_name = output_name[:-9] + '%02d.01.tif' % (date.month)

        # Save tiff file
        DC.Save_as_tiff(output_name, Data_one_month, geo_out, proj)


def Day16_to_Mnoth(Dir_in, Startdate, Enddate, Dir_out=None):
    """ 16 Daily to Monthly State

    :param Dir_in:
    :param Startdate:
    :param Enddate:
    :param Dir_out:
    :return:
    """
    # Change working directory
    os.chdir(Dir_in)

    # Find all eight daily files
    files = glob.glob('*16-daily*.tif')

    # Create array with filename and keys (DOY and year) of all the 8 daily files
    i = 0
    DOY_Year = np.zeros([len(files), 3])
    for File in files:
        # Get the time characteristics from the filename
        year = File.split('.')[-4][-4:]
        month = File.split('.')[-3]
        day = File.split('.')[-2]

        # Create pandas Timestamp
        date_file = '%s-%02s-%02s' % (year, month, day)
        Datum = pd.Timestamp(date_file)

        # Get day of year
        DOY = Datum.strftime('%j')

        # Save data in array
        DOY_Year[i, 0] = i
        DOY_Year[i, 1] = DOY
        DOY_Year[i, 2] = year

        # Loop over files
        i += 1

    # Check enddate:
    Enddate_split = Enddate.split('-')
    month_range = calendar.monthrange(int(Enddate_split[0]), int(Enddate_split[1]))[1]
    Enddate = '%d-%02d-%02d' % (int(Enddate_split[0]), int(Enddate_split[1]), month_range)

    # Check startdate:
    Startdate_split = Startdate.split('-')
    Startdate = '%d-%02d-01' % (int(Startdate_split[0]), int(Startdate_split[1]))

    # Define end and start date
    Dates = pd.date_range(Startdate, Enddate, freq='MS')
    DatesEnd = pd.date_range(Startdate, Enddate, freq='M')

    # Get array information and define projection
    geo_out, proj, size_X, size_Y = RC.Open_array_info(files[0])
    if int(proj.split('"')[-2]) == 4326:
        proj = "WGS84"

    # Get the No Data Value
    dest = gdal.Open(files[0])
    NDV = dest.GetRasterBand(1).GetNoDataValue()

    # Loop over months and create monthly tiff files
    i = 0
    for date in Dates:
        # Get Start and end DOY of the current month
        DOY_month_start = date.strftime('%j')
        DOY_month_end = DatesEnd[i].strftime('%j')

        # Search for the files that are between those DOYs
        year = date.year
        DOYs = DOY_Year[DOY_Year[:, 2] == year]
        DOYs_oneMonth = DOYs[np.logical_and((DOYs[:, 1] + 16) >= int(DOY_month_start), DOYs[:, 1] <= int(DOY_month_end))]

        # Create empty arrays
        Monthly = np.zeros([size_Y, size_X])
        Weight_tot = np.zeros([size_Y, size_X])
        Data_one_month = np.ones([size_Y, size_X]) * np.nan

        # Loop over the files that are within the DOYs
        for EightDays in DOYs_oneMonth[:, 1]:

            # Calculate the amount of days in this month of each file
            Weight = np.ones([size_Y, size_X])

            # For start of month
            if np.min(DOYs_oneMonth[:, 1]) == EightDays:
                Weight = Weight * int(EightDays + 16 - int(DOY_month_start))

            # For end of month
            elif np.max(DOYs_oneMonth[:, 1]) == EightDays:
                Weight = Weight * (int(DOY_month_end) - EightDays + 1)

            # For the middle of the month
            else:
                Weight = Weight * 16

            row = DOYs_oneMonth[np.argwhere(DOYs_oneMonth[:, 1] == EightDays)[0][0], :][0]

            # Open the array of current file
            input_name = os.path.join(Dir_in, files[int(row)])
            Data = RC.Open_tiff_array(input_name)

            # Remove NDV
            Weight[Data == NDV] = 0
            Data[Data == NDV] = np.nan

            # Multiply weight time data (per day)
            Data = Data * Weight

            # Calculate the total weight and data
            Weight_tot += Weight
            Monthly[~np.isnan(Data)] += Data[~np.isnan(Data)]

        # Go to next month
        i += 1

        # Calculate the average
        Data_one_month[Weight_tot != 0.] = Monthly[Weight_tot != 0.] / Weight_tot[Weight_tot != 0.]

        # Define output directory
        if Dir_out == None:
            Dir_out = Dir_in

        # Define output name
        output_name = os.path.join(Dir_out, files[int(row)].replace('16-daily', 'monthly'))
        output_name = output_name[:-9] + '%02d.01.tif' % (date.month)

        # Save tiff file
        DC.Save_as_tiff(output_name, Data_one_month, geo_out, proj)


def Week_to_Mnoth(Dir_in, Startdate, Enddate, Dir_out=None):
    """ Week to Monthly Flux

    :param Dir_in:
    :param Startdate:
    :param Enddate:
    :param Dir_out:
    :return:
    """
    # Change working directory
    os.chdir(Dir_in)

    # Find all eight daily files
    files = glob.glob('*weekly*.tif')

    # Create array with filename and keys (DOY and year) of all the 8 daily files
    i = 0
    DOY_Year = np.zeros([len(files), 3])
    for File in files:
        # Get the time characteristics from the filename
        year = File.split('.')[-4][-4:]
        month = File.split('.')[-3]
        day = File.split('.')[-2]

        # Create pandas Timestamp
        date_file = '%s-%02s-%02s' % (year, month, day)
        Datum = pd.Timestamp(date_file)

        # Get day of year
        DOY = Datum.strftime('%j')

        # Save data in array
        DOY_Year[i, 0] = i
        DOY_Year[i, 1] = DOY
        DOY_Year[i, 2] = year

        # Loop over files
        i += 1

    # Check enddate:
    Enddate_split = Enddate.split('-')
    month_range = calendar.monthrange(int(Enddate_split[0]), int(Enddate_split[1]))[1]
    Enddate = '%d-%02d-%02d' % (int(Enddate_split[0]), int(Enddate_split[1]), month_range)

    # Check startdate:
    Startdate_split = Startdate.split('-')
    Startdate = '%d-%02d-01' % (int(Startdate_split[0]), int(Startdate_split[1]))

    # Define end and start date
    Dates = pd.date_range(Startdate, Enddate, freq='MS')
    DatesEnd = pd.date_range(Startdate, Enddate, freq='M')

    # Get array information and define projection
    geo_out, proj, size_X, size_Y = RC.Open_array_info(files[0])
    if int(proj.split('"')[-2]) == 4326:
        proj = "WGS84"

    # Get the No Data Value
    dest = gdal.Open(files[0])
    NDV = dest.GetRasterBand(1).GetNoDataValue()

    # Loop over months and create monthly tiff files
    i = 0
    for date in Dates:
        # Get Start and end DOY of the current month
        DOY_month_start = date.strftime('%j')
        DOY_month_end = DatesEnd[i].strftime('%j')

        # Search for the files that are between those DOYs
        year = date.year
        DOYs = DOY_Year[DOY_Year[:, 2] == year]
        DOYs_oneMonth = DOYs[np.logical_and((DOYs[:, 1] + 7) >= int(DOY_month_start), DOYs[:, 1] <= int(DOY_month_end))]

        # Create empty arrays
        Monthly = np.zeros([size_Y, size_X])
        Weight_tot = np.zeros([size_Y, size_X])
        Data_one_month = np.ones([size_Y, size_X]) * np.nan

        # Loop over the files that are within the DOYs
        for EightDays in DOYs_oneMonth[:, 1]:

            # Calculate the amount of days in this month of each file
            Weight = np.ones([size_Y, size_X])

            # For start of month
            if np.min(DOYs_oneMonth[:, 1]) == EightDays:
                Weight = Weight * int(EightDays + 7 - int(DOY_month_start))

            # For end of month
            elif np.max(DOYs_oneMonth[:, 1]) == EightDays:
                Weight = Weight * (int(DOY_month_end) - EightDays + 1)

            # For the middle of the month
            else:
                Weight = Weight * 7

            row = DOYs_oneMonth[np.argwhere(DOYs_oneMonth[:, 1] == EightDays)[0][0], :][0]

            # Open the array of current file
            input_name = os.path.join(Dir_in, files[int(row)])
            Data = RC.Open_tiff_array(input_name)

            # Remove NDV
            Weight[Data == NDV] = 0
            Data[Data == NDV] = np.nan

            # Multiply weight time data (per day)
            Data = Data / 7 * Weight

            # Calculate the total weight and data
            Weight_tot += Weight
            Monthly[~np.isnan(Data)] += Data[~np.isnan(Data)]

        # Go to next month
        i += 1

        # Calculate the average
        Data_one_month[Weight_tot != 0.] = Monthly[Weight_tot != 0.] / Weight_tot[Weight_tot != 0.]

        # Convert mm/day to mm/month
        Data_one_month = Data_one_month * calendar.monthrange(int(year), int(month))[1]

        # Define output directory
        if Dir_out == None:
            Dir_out = Dir_in

        # Define output name
        output_name = os.path.join(Dir_out, files[int(row)].replace('weekly', 'monthly').replace('week', 'month'))
        output_name = output_name[:-9] + '%02d.01.tif' % (date.month)

        # Save tiff file
        DC.Save_as_tiff(output_name, Data_one_month, geo_out, proj)


def Mnoth_to_Year(Dir_in, Startdate, Enddate, Dir_out=None):
    """ Monthly to Yearly Flux

    :param Dir_in:
    :param Startdate:
    :param Enddate:
    :param Dir_out:
    :return:
    """
    # Change working directory
    os.chdir(Dir_in)

    # Find all monthly files
    files = glob.glob('*monthly*.tif')

    # Define end and start date
    Dates = pd.date_range(Startdate, Enddate, freq='AS')

    # Get array information and define projection
    geo_out, proj, size_X, size_Y = RC.Open_array_info(files[0])
    if int(proj.split('"')[-2]) == 4326:
        proj = "WGS84"

    # Get the No Data Value
    dest = gdal.Open(files[0])
    NDV = dest.GetRasterBand(1).GetNoDataValue()

    for date in Dates:
        Year = date.year
        files_one_year = glob.glob('*monthly*%d*.tif' % Year)

        # Create empty arrays
        Year_data = np.zeros([size_Y, size_X])

        if len(files_one_year) is not int(12):
            print("One month in year %s is missing!" % Year)

        for file_one_year in files_one_year:
            file_path = os.path.join(Dir_in, file_one_year)

            Month_data = RC.Open_tiff_array(file_path)
            Month_data[np.isnan(Month_data)] = 0.0
            Month_data[Month_data == -9999] = 0.0
            Year_data += Month_data

        # Define output directory
        if Dir_out == None:
            Dir_out = Dir_in
        if not os.path.exists(Dir_out):
            os.makedirs(Dir_out)

        # Define output name
        output_name = os.path.join(Dir_out, file_one_year.replace('monthly', 'yearly').replace('month', 'year'))
        output_name = output_name[:-14] + '%d.01.01.tif' % (date.year)

        # Save tiff file
        DC.Save_as_tiff(output_name, Year_data, geo_out, proj)
