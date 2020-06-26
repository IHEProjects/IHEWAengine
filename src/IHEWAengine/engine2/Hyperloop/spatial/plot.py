# -*- coding: utf-8 -*-
"""
"""


def category_areas(lu_fih, categories, output_fih, area_treshold=0.01):
    """
    Plot the relative areas of landuse categories in a pie chart.

    Parameters
    ----------
    lu_fih : str
        Filehandle pointing to a landusemap
    categories : dict
        Dictionary specifying all the landuse categories.
    output_fih : str
        Filehandle indicating where to save the graph.
    area_treshold : float, optional
        Categories with a relative area lower than the treshold are not plotted
        in the pie chart. Default values is 0.01.
    """
    area_map = map_pixel_area_km(lu_fih)
    lulc = open_as_array(lu_fih)
    total_area = np.nansum(area_map[~np.isnan(lulc)])

    areas = dict()
    for key in categories.keys():
        classes = categories[key]

        mask = np.logical_or.reduce([lulc == value for value in classes])

        area = np.nansum(area_map[mask])

        if area / total_area >= area_treshold:
            areas[key] = area

    clrs = ['#6bb8cc', '#87c5ad', '#9ad28d',
            '#acd27a', '#c3b683', '#d4988b',
            '#b98b89', '#868583', '#497e7c']

    plt.figure(figsize=(15, 15))
    plt.clf()
    plt.title('Total Area ({0:.2f} ha)'.format(total_area / 100))

    plt.pie(areas.values(), labels=areas.keys(), autopct='%1.1f%%', colors=clrs)

    plt.savefig(output_fih)


