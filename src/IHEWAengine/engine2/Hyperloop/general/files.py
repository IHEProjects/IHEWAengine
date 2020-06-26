# -*- coding: utf-8 -*-
"""
"""


def scan(folder, extension='tif'):
    """
    List the files in a folder with a specified extension.

    Parameters
    ----------
    folder : str
        Folder to be scrutinized.
    extension : str, optional
        Type of files to look for in folder, default is 'tif'.

    Returns
    -------
    list_of_files : list
        List with filehandles of the files found in folder with extension.
    """
    list_of_files = [os.path.join(folder, fn) for fn in next(os.walk(folder))[2] if fn.split('.')[-1] == extension]
    return list_of_files


def sort(input_dir, year_position, month_position=None, day_position=None, doy_position=None, extension='tif'):
    r"""
    Substract metadata from multiple filenames.

    Parameters
    ----------
    input_dir : str
        Folder containing files.
    year_position : list
        The indices where the year is positioned in the filenames, see example.
    month_position : list, optional
        The indices where the month is positioned in the filenames, see example.
    day_position : list, optional
        The indices where the day is positioned in the filenames, see example.
    doy_position : list, optional
        The indices where the doy is positioned in the filenames, see example.
    extension : str
        Extension of the files to look for in the input_dir.

    Returns
    -------
    filehandles : ndarray
        The files with extension in input_dir.
    dates : ndarray
        The dates corresponding to the filehandles.
    years : ndarray
        The years corresponding to the filehandles.
    months : ndarray
        The years corresponding to the filehandles.
    days :ndarray
        The years corresponding to the filehandles.
    """
    dates = np.array([])
    years = np.array([])
    months = np.array([])
    days = np.array([])
    filehandles = np.array([])

    files = list_files_in_folder(input_dir, extension=extension)
    for fil in files:
        filehandles = np.append(filehandles, fil)
        year = int(fil[year_position[0]:year_position[1]])

        month = 1
        if month_position is not None:
            month = int(fil[month_position[0]:month_position[1]])

        day = 1
        if day_position is not None:
            day = int(fil[day_position[0]:day_position[1]])

        if doy_position is not None:
            date = datetime.date(year, 1, 1) + datetime.timedelta(int(fil[doy_position[0]:doy_position[1]]) - 1)
            month = date.month
            day = date.day
        else:
            date = datetime.date(year, month, day)

        years = np.append(years, year)
        months = np.append(months, month)
        days = np.append(days, day)

        dates = np.append(dates, date)

    return filehandles, dates, years, months, days
