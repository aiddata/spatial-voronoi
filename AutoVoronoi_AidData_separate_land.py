"""
Author: Eugene Wang
This code can be found in this Github Address: https://github.com/itpir/spatial-voronoi
Established at Jul 8 2016. Inherited from AutoVoronoi_AidData.py
Latest Update: August 2, 2016
"""
import pandas as pd
import numpy as np
import os
from shapely.geometry import LineString, MultiPoint, mapping, shape
from scipy.spatial import Voronoi
import fiona
from fiona.crs import from_epsg
import shapely.ops
import datetime
import AutoVoronoi_config


'''
# function 1: aggregate_lv1_by_location()
# description: Aggregate records from level1 by location
# input: input_address ( input address of file containing level1 data), setting_csv_address = 'default' ( a csv file only showing
    which fields should be included), filter_field (To choose a specific field to filter the file), filter_value
    (the specific value wanted from filter_field)
# return:cleaned_df(cleaned dataframe)
'''
def aggregate_lv1_by_location(input_address, setting_csv_address = 'default', filter_dict = None):

    # read setting file to get a list of fields needed.
    df_csv = read_setting(setting_csv_address)

    # this function is not debugged or test fully yet
    # filter the dataframe with filter_dict
    filtered_level1 = filter_dataframe(input_address, filter_dict)

    # get dataframe with only the fields listed in the setting file
    title_field = ['latitude','longitude']
    title_field_additional = []
    for i in df_csv['field_name']:
        title_field.append(str(i))
        title_field_additional.append(str(i))
    filtered_subset = filtered_level1.loc[:, title_field]

    comparing_index = filtered_subset.head(1).index[0]
    count_total = len(filtered_subset)

    # since repeatly use pandas.append() to add a row is a performance hit
    # As suggested, I will insert row content as a dictionary to a list
    list_rows = []

    # when there is still records in dataframe
    while len(filtered_subset) > 0:
        # get the latitude and longitude to compare with others
        lat_comparing = filtered_subset.head(1).latitude[comparing_index]
        lon_comparing = filtered_subset.head(1).longitude[comparing_index]
        is_nan_lat = str(lat_comparing) == 'nan'
        is_nan_lon = str(lon_comparing) == 'nan'

        # to judge if the position is the same with comparing record
        is_lat = filtered_subset.latitude == lat_comparing
        is_lon = filtered_subset.longitude == lon_comparing

        # exclude records with position of NaN
        if (is_nan_lat | is_nan_lon):
            filtered_subset = filtered_subset[is_lat | is_lon]
            if len(filtered_subset) == 0:
                break
            comparing_index = filtered_subset.head(1).index[0]
            count_now = len(filtered_subset)
            print "The progress of aggrecating data by lcation : %s / %s" % (count_now, count_total)
            continue

        dict_cleaned_record = {'latitude':lat_comparing, 'longitude':lon_comparing}

        # get dataframe of overlaping points with comparing point
        subset_overlapping = filtered_subset[is_lat & is_lon]


        # handling with every field, looping all field
        for str_field in title_field_additional:
            # get them to list
            # get unique values by using 'set'
            # set a list to store a list of unique values
            list_content_field = []
            set_field = set(subset_overlapping[str_field].tolist())
            for e in set_field:
                temp_list_field = str(e).split('|')
                list_content_field = combineTwoList(list_content_field, temp_list_field)

            list_content_field.sort()
            str_field_content = "|".join(list_content_field)

            # get them into a dictionary
            dict_cleaned_record[str_field] = str_field_content

        # attach the dict of a record in one record in a list
        list_rows.append(dict_cleaned_record)

        # next loop will check the rest of records not checked yet
        filtered_subset = filtered_subset[~(is_lat & is_lon)]
        # have a new index to compare with the rest records.
        comparing_index = filtered_subset.head(1).index[0]

        count_now = len(filtered_subset)
        print "The progress of aggrecating data by lcation : %s / %s" % (count_now, count_total)
        # use this list to create cleaned CSV

    # create the dataframe with all rows of information about positions
    cleaned_data = pd.DataFrame(list_rows)
    # csvfile_name = 'filtered_aggregated_data_all.csv'
    # cleaned_data.to_csv(csvfile_name, encoding='utf-8')
    # print ('information has been aggregated to ' + csvfile_name)

    return cleaned_data
'''
function 1.1: read_setting()
description: load setting csv into dataframe
input: csv(Setting CSV address or 'default')
return: dataframe (dataframe of setting)
'''
def read_setting(csv):
    if csv == 'default':
        df_csv = pd.read_csv('default_setting_voronoi.csv', encoding='utf-8')
    else:
        try:
            filename, file_ext = os.path.splitext(csv)
            if os.path.isfile(csv) & file_ext == ('.csv'):
                df_csv = pd.read_csv(csv, encoding='utf-8')
            else:
                raise ImportError('This input setting file is not wrong. It should be a .csv file')
        except:
            raise ImportError('The setting file has an incorrect address or incorrect format')

    return df_csv

'''
function 1.2: filter_dataframe()
description: filter dataframe based on certain conditions in filter_dict
input: input_dfadd(an address of input file), filter_dict(a dictionary, key is field name and values are conditions)
return: filtered_subset



sample of filter_dict:      #lat and long will be used without any statement
{'sector': [311,310,998], 'donors_iso3': ['USA']}
{'aaa':['USA']}  Even only one word is search for field 'aaa', make the word in a list
{'donors_iso3':'USA'} The value can be only a string value
{'year_duration':{'starting year':####, 'ending year':####}} PS: for searching time duration, the field_name are keys.
                                                                Starting point first, ending point last.
'''
def filter_dataframe(input_dfadd, filter_dict):

    subset_overlapping = pd.read_csv(input_dfadd, encoding='utf-8')
    if filter_dict is None:
        return subset_overlapping
    elif filter_dict == {}:
        return subset_overlapping

    list_keys = filter_dict.keys()
    list_values = filter_dict.values()
    condition_key = None
    condition_all = None

    # loop every key and value to complete boolean value
    for i in range(len(list_keys)):
        key = list_keys[i]
        value = list_values[i]
        condition_key = get_condition_key(value, key, input_dfadd)
        if condition_all is None:
            condition_all = condition_key
        else:
            # even conditions in the same key will work together. Logical OR
            # conditions of different key only work if they have somethin in common. Logical AND.
            condition_all = condition_all & condition_key

    # dataframe that satisfy all conditions
    filtered_subset = subset_overlapping[condition_all]
    if len(filtered_subset) == 0:
        print 'No such a record is found.'
        quit()

    return filtered_subset


'''
function 1.2.1 get_condition_key()
description: return a proper condition_key based on the type of parameter.
input: value_filter( a value a filter is dealing with), key_filter(the key a filter is looking at), input_dfadd(an input
    address of dataframe-like file (e.g. CSV))
output: condition_key (a boolean series / array)
'''
def get_condition_key(value_filter, key_filter, input_dfadd):

    input_df = pd.read_csv(input_dfadd, encoding= 'utf-8')
    condition_key = None

    # get condition_key by the type of value
    if type(value_filter) is str:
        # searching one string
        print 'processing filter: field \'%s\' contain %s' %(key_filter, value_filter)
        if condition_key is None:
            condition_key = input_df[key_filter].str.contains(value_filter, na=False)
        else:
            new_boolean = input_df[key_filter].str.contains(value_filter, na= False)
            condition_key = condition_key | new_boolean
    elif type(value_filter) is int:
        # searching one value
        print 'processing filter: field \'%s\' contain %d' %(key_filter, value_filter)
        if condition_key is None:
            condition_key = input_df[key_filter].str.contains(str(value_filter), na=False)
        else:
            new_boolean = input_df[key_filter].str.contains(str(value_filter), na=False)
            condition_key = condition_key | new_boolean
    elif type(value_filter) is float:
        # searching one value
        print 'processing filter: \'%s\' contain %d' % (key_filter, value_filter)
        if condition_key is None:
            condition_key = input_df[key_filter].str.contains(str(value_filter), na=False)
        else:
            new_boolean = input_df[key_filter].str.contains(str(value_filter), na=False)
            condition_key = condition_key | new_boolean
    elif type(value_filter) is list:
        # searching multiple values
        stack_condition = None
        for counter, item in enumerate(value_filter):
            new_condition = get_condition_key(item, key_filter, input_dfadd)
            if counter == 0:
                stack_condition = new_condition
            else:
                stack_condition = stack_condition | new_condition
        condition_key = stack_condition
    elif type(value_filter) is dict:
        # list a time span in the filter to limit the records.
        start_year = value_filter.values()[0]
        end_year = value_filter.values()[1]
        start_field = value_filter.keys()[0]
        end_field = value_filter.keys()[1]

        input_df[start_field] = pd.to_datetime(input_df[start_field])
        input_df[end_field] = pd.to_datetime(input_df[end_field])
        try:
            # records not end before filter starts
            not_early = input_df[end_field] >= pd.Timestamp(datetime.date(int(start_year), 1, 1))

            # records not start later filter ends.
            not_late = input_df[start_field] <= pd.Timestamp(datetime.date(int(end_year), 12, 31))

            condition_key = not_early & not_late

            # exclude where start_field and end_field both empty if configuration allows
            if AutoVoronoi_config.allow_empty_time_record is True:
                null_start = input_df[start_field].isnull()
                null_end = input_df[end_field].isnull()
                new_condition = null_start & null_end
                if condition_key is None:
                    condition_key = new_condition
                else:
                    condition_key = condition_key | new_condition
            #condition_start = input_df[start_field] > int(start_year)
            #condition_end = input_df[end_field] < int(end_year)
        except:
            raise NameError('Please check time-related field name has been correctly inputted and'
                            ' the year value should be integer')
    return condition_key

'''
function 1.3: combineTwoList()
description: combine latter list into the first list while no same element will be added.
# input: l1 -- the list to have new elements added, l2 -- the list to contribute elements
# output: list -- the new-element-added list
'''
def combineTwoList(l1, l2):
    if len(l1) == 0:
        l1 = l2
        return l1
    else:
        for str in l2:
            if str in l1:
                continue
            else:
                l1.append(str)
                continue
    return l1

'''
function 2: get_clipped_voronoi
description : This function will do :
                records seperation based on islands,then do voronoi analysis based on different
                groups of seperated records,
                polygonize voronoi,
                clip voronoi based on country boundary
                and finally put each clipped polygon into a list
# input: boundary_fullpath, list_points_original
# output: a list of clipped polygon
'''
def get_clipped_voronoi(boundary_fullpath, list_points):
    # with boundary shapefile 'r' as boundary:
    with fiona.collection(boundary_fullpath, 'r') as layer_boundary:

        list_seperate_points = []  # list to store points seperated by continents or lands
        list_seperate_coordinates = []  # list to store coordinates seperated by continents or lands
        list_boundary_polygon = []  # list to store polygons of boundary polygons
        list_voronoi_polygon = []  # polygon to store polygons by voronoi analysis

        # and all lists here is under a order of elements responding to lands of country boundary

        list_clipped_polygon = []

        # get list of boundary polygon
        for item in layer_boundary.filter():
            polygon_item = shape(item['geometry'])

            # decompose Multipolygon to polygons
            if polygon_item.geom_type == "MultiPolygon":
                list_boundary_polygon.extend(list(polygon_item))
            elif polygon_item.geom_type == 'Polygon':
                list_boundary_polygon.append(polygon_item)

        # get a list of project location seperated by lands
        for polyboun in list_boundary_polygon:
            points_in_polygon = []
            coordinate_in_polygon = []
            # loop through boundary polygon to seperate points located in different lands
            for point in list_points:
                if point.within(polyboun):
                    points_in_polygon.append(point)
                    coordinate_in_polygon.append([point.x, point.y])
                else:
                    continue
            list_seperate_points.append(points_in_polygon)
            list_seperate_coordinates.append(coordinate_in_polygon)

        # get a list of voronoi polygon in order of lands
        for list_group in list_seperate_coordinates:
            # append some points to set up bound the whole voronoi so unbounded polygon ban be shown in SHP
            # with (5000, 5000) and other three corners
            extra_point = np.array([[5000, 5000], [5000, -5000], [-5000, -5000], [-5000, 5000]])

            # if no point in a land
            if len(list_group) == 0:
                vor = Voronoi(extra_point)
                lines = [
                    LineString(vor.vertices[line])
                    for line in vor.ridge_vertices
                    if -1 not in line
                    ]
                # polygonize varonoi
                areas = list(shapely.ops.polygonize(lines))
            else:
                arr = np.array(list_group)
                arr_position_extend = np.concatenate((arr, extra_point))
                vor = Voronoi(arr_position_extend)
                lines = [
                    LineString(vor.vertices[line])
                    for line in vor.ridge_vertices
                    if -1 not in line
                    ]
                areas = list(shapely.ops.polygonize(lines))
            list_voronoi_polygon.append(areas)
            # each value in the list above is voronoi surface based on points in different lands

        # clip these polygons with respondant boundary polygon
        for i in range(len(list_boundary_polygon)):
            boundary = list_boundary_polygon[i]
            v_polygon = list_voronoi_polygon[i]
            # if no point in a land
            if len(v_polygon) == 0:
                list_clipped_polygon.append(boundary)
            for patch in v_polygon:
                if boundary.intersects(patch):
                    list_clipped_polygon.append(boundary.intersection(patch))

        return list_clipped_polygon


'''
function 3: merge_two_dicts()
description: merge two dictionary without changing original dict.
'''
def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z

'''
function 4: create_folder()
description: create a folder by name,  if existed ,add an extention name
input: dirname (folder name)
output: none
'''
def create_folder(dirname):
    if os.path.exists(dirname):
        dirname = dirname + '_new'
        dirname = create_folder(dirname)
    else:
        os.mkdir(dirname)
        return dirname
    return dirname
#####################################################################################################################
'''
This function is executed only when this script will be run directly.
'''
def main():
    output_polygon_name = AutoVoronoi_config.output_polygon_fullpath
    output_point_name = AutoVoronoi_config.output_point_fullpath
    dict_filter = AutoVoronoi_config.dict_filter

    # read level1 csv data
    input_address = AutoVoronoi_config.level1_fullpath
    # the input shapefile of boundary
    boundary_address = AutoVoronoi_config.boundary_fullpath
    setcsv_fullpath = AutoVoronoi_config.attribute_csv_fullpath
    ###############


    clean_df = aggregate_lv1_by_location(input_address,setting_csv_address=setcsv_fullpath, filter_dict=dict_filter)

    # get the numpy array of latitude and longitude
    att_lon_lat_origin = clean_df.loc[:, ['longitude', 'latitude']].values

    # load coordinates into multipoints object
    mtpoints_original = MultiPoint(att_lon_lat_origin)

    # use list(points.geoms) or list(points) to access each point in MultiPoint object
    list_points_origional = list(mtpoints_original.geoms)

    list_clipped_polygon = get_clipped_voronoi(boundary_address, list_points_origional)


    # create a schema for ESRI shapefile
    outSchema = {'geometry': 'Polygon', 'properties': {}}

    # some title has been excluded to be added in the attribute table of voronoi output shapefile
    list_attribute_title = [
        str(clean_df.columns[ii])
        for ii in range(len(clean_df.columns))
        if 'Unnamed: 0' != clean_df.columns[ii]
        if 'latitude' != clean_df.columns[ii]
        if 'longitude' != clean_df.columns[ii]
        ]

    for ii in list_attribute_title:
        outSchema['properties'][ii] = 'str'

    # use WGS 84 , longlat , the kind of global use of Coordinate Reference System
    crs = from_epsg(4326)

    '''
        filter(bbox=None)
        Returns an iterator over records, but filtered by a test for spatial intersection with
        the provided bbox, a (minx, miny, maxx, maxy) tuple.
    '''

    with fiona.collection(output_polygon_name, 'w', 'ESRI Shapefile', outSchema,crs) as output:
        for polygon in list_clipped_polygon:
            is_att_assign = False
            attribute_each_record = {}
            # extracting attribute from point to polygon and output.
            # IF no point belongs to it, make it the whole polygon (void)
            for point in list_points_origional:
                # spatially join data from point to polygon
                if point.within(polygon):
                    is_same_lat = clean_df.latitude == point.y
                    is_same_lon = clean_df.longitude == point.x
                    # fill each field with their value
                    for ii in list_attribute_title:
                        value = str(clean_df[is_same_lat & is_same_lon].head(1)[ii].values[0])
                        attribute_each_record[ii] = value
                    output.write({
                        'properties': attribute_each_record,
                        'geometry': mapping(polygon)
                    })
                    is_att_assign = True
            # if polygon still has no match to record points after all points has been looped.
            if is_att_assign:
                continue
            else:
                for ii in list_attribute_title:
                    value = ''
                    attribute_each_record[ii] = value
                output.write({
                    'properties': attribute_each_record,
                    'geometry': mapping(polygon)
                })

    # test to see points
    outSchema['geometry'] = 'Point'
    with fiona.collection(output_point_name, 'w', 'ESRI Shapefile', outSchema, crs) as output_point:
        for point in list_points_origional:
            attribute_each_record = {}
            is_same_lat = clean_df.latitude == point.y
            is_same_lon = clean_df.longitude == point.x
            try:
                for ii in list_attribute_title:
                    value = str(clean_df[is_same_lat & is_same_lon].head(1)[ii].values[0])
                    attribute_each_record[ii] = value
            except:
                # continue if point is one of points used to wrap voronoi polygon E.G.(5000, 5000), (
                continue
            output_point.write({
                'properties': attribute_each_record,
                'geometry': mapping(point)
            })

'''
function: hightlight_mode
desciption: In this mode, all records are involved in voronoi analysis, but highlight those fitting the filter, against the others
# input:  nothing
# output: nothing
# export: shapefile of voronoi analysis, with a field featuring if records fulfill requirement.
'''
def highlight_mode():

    # check input parameter and load them
    output_polygon_name = AutoVoronoi_config.output_polygon_fullpath
    output_point_name = AutoVoronoi_config.output_point_fullpath
    dict_filter = AutoVoronoi_config.dict_filter
    # read level1 csv data
    input_address = AutoVoronoi_config.level1_fullpath
    # the input shapefile of boundary
    boundary_address = AutoVoronoi_config.boundary_fullpath
    setcsv_fullpath = AutoVoronoi_config.attribute_csv_fullpath
    timefilter = AutoVoronoi_config.time_filter

    #######################################
    # time filter set up
    clean_df = aggregate_lv1_by_location(input_address, setcsv_fullpath, timefilter)

    # get the numpy array of latitude and longitude
    att_lon_lat_origin = clean_df.loc[:, ['longitude', 'latitude']].values

    # load coordinates into multipoints object
    mtpoints_original = MultiPoint(att_lon_lat_origin)

    list_points_origional = list(mtpoints_original.geoms)

    list_clipped_polygon = get_clipped_voronoi(boundary_address, list_points_origional)

    # plus attribute filter right now.
    filter_both = merge_two_dicts(timefilter, dict_filter)
    request_df = aggregate_lv1_by_location(input_address, setcsv_fullpath, filter_both)

    requested_lon_lat = request_df.loc[:,['longitude', 'latitude']].values
    list_requested_points = list(MultiPoint(requested_lon_lat).geoms)

    # create a schema for ESRI shapefile
    outSchema = {'geometry': 'Polygon', 'properties': {}}

    # some title has been excluded to be added in the attribute table of voronoi output shapefile
    list_attribute_title = [
        str(clean_df.columns[ii])
        for ii in range(len(clean_df.columns))
        if 'Unnamed: 0' != clean_df.columns[ii]
        if 'latitude' != clean_df.columns[ii]
        if 'longitude' != clean_df.columns[ii]
        ]

    # for ii in list_attribute_title:
    #     outSchema['properties'][ii] = 'str'
    # add one new property
    outSchema['properties']['requested'] = 'int'
    outSchema['properties']['att_fil'] = 'str'
    outSchema['properties']['time_fil'] = 'str'
    for i in list_attribute_title:
        outSchema['properties'][i] = 'str'

    # use WGS 84 , longlat , the kind of global use of Coordinate Reference System
    crs = from_epsg(4326)

    with fiona.collection(output_polygon_name, 'w', 'ESRI Shapefile', outSchema,crs) as output:
        for polygon in list_clipped_polygon:
            is_att_assign = False
            for point in list_requested_points:
                attribute_each_record = {}
                if point.within(polygon):
                    attribute_each_record['requested'] = 1
                    attribute_each_record['att_fil'] = str(dict_filter)
                    attribute_each_record['time_fil'] = str(timefilter)

                    is_same_lat = clean_df.latitude == point.y
                    is_same_lon = clean_df.longitude == point.x
                    # fill each field with their value
                    for ii in list_attribute_title:
                        value = str(clean_df[is_same_lat & is_same_lon].head(1)[ii].values[0])
                        attribute_each_record[ii] = value
                    output.write({
                        'properties': attribute_each_record,
                        'geometry': mapping(polygon)
                    })
                    is_att_assign = True
                else:
                    continue

            if is_att_assign:
                continue
            else:
                attribute_each_record['requested'] = 0
                attribute_each_record['att_fil'] = str(dict_filter)
                attribute_each_record['time_fil'] = str(timefilter)
                for ii in list_attribute_title:
                    value = ''
                    attribute_each_record[ii] = value
                output.write({
                    'properties': attribute_each_record,
                    'geometry': mapping(polygon)
                })



def pairwise_mode():
    # check input parameter and load them
    output_polygon_name = AutoVoronoi_config.output_polygon_fullpath
    output_point_name = AutoVoronoi_config.output_point_fullpath
    dict_filter = AutoVoronoi_config.dict_filter
    # read level1 csv data
    input_address = AutoVoronoi_config.level1_fullpath
    # the input shapefile of boundary
    boundary_address = AutoVoronoi_config.boundary_fullpath
    setcsv_fullpath = AutoVoronoi_config.attribute_csv_fullpath
    timefilter = AutoVoronoi_config.time_filter

    comparing_country = AutoVoronoi_config.comparing_country_iso

#######################################################################
    all_dict = merge_two_dicts(dict_filter, timefilter)

    #1 get aggregated dataframe based on time filter:
    aftertime_df = aggregate_lv1_by_location(input_address, setcsv_fullpath, all_dict)
    #2 get countries donating money to the same regions as comparing countries did
    set_field = set(aftertime_df['donors_iso3'].tolist())
    list_donors = []
    for i in set_field:
        temp_list_donor = str(i).split('|')
        list_donors = combineTwoList(list_donors, temp_list_donor)

    filter_others = {}
    list_others = []
    for i in list_donors:
        # exclude comparing countries in it.
        if i == comparing_country:
            continue
        list_others.append(i)
    filter_others['donors_iso3'] = filter_others

    if not os.path.isdir(output_polygon_name):
        dirname = comparing_country +' vs others'
        dirname = create_folder(dirname)
        output_polygon_name = os.getcwd()+'/' + dirname + '/'
        print 'output polygon path is not a folder, polygon output has been placed in '+ output_polygon_name

    if not os.path.isdir(output_point_name):
        dirname = comparing_country + ' vs others_points'
        dirname = create_folder(dirname)
        output_point_name = os.getcwd()+'/' + dirname + '/'
        print 'output point path is not a folder, point output has been placed in ' + output_point_name

    #loop each other donor, each shapefile will be produced for each comparision between other donor and comparing donor
    for other in list_others:
        #get selection of records of conflicting areas and none conflicting areas
        # records donated by one of the other countries
        condition_other = aftertime_df['donors_iso3'].str.contains(str(other), na=False)
        # records donated by the comparing country
        condition_comparing = aftertime_df['donors_iso3'].str.contains(str(comparing_country), na= False)
        # records donated by the both countries
        condition_conflict = condition_other & condition_comparing
        condition_both = condition_comparing | condition_other
        condition_against_conflict = ~condition_conflict
        # records
        condition_non_conconflict = condition_both & condition_against_conflict


        df_two_country = aftertime_df[condition_other | condition_comparing]

        #4 create voronoi polygon
        lonlat_two_country = df_two_country.loc[:, ['longitude', 'latitude']].values
        point_two_country = MultiPoint(lonlat_two_country)
        list_points = list(point_two_country.geoms)
        list_clipped_polygon = get_clipped_voronoi(boundary_address, list_points)

        #5 check each polygon (or records in dataframe of #3) to see if there is conflicts between comparing countries
        #  and the other countries
        # create a schema for ESRI shapefile
        outSchema = {'geometry': 'Polygon', 'properties': {}}

        # some title has been excluded to be added in the attribute table of voronoi output shapefile
        list_attribute_title = [
            str(aftertime_df.columns[ii])
            for ii in range(len(aftertime_df.columns))
            if 'Unnamed: 0' != aftertime_df.columns[ii]
            if 'latitude' != aftertime_df.columns[ii]
            if 'longitude' != aftertime_df.columns[ii]
            ]

        outSchema['properties']['vs_code'] = 'int'
        # 0 - the region only occupied by comparing donor, 1 - by both, conflicting
        # -1 - void, not occupied by none of the donors
        # 2 - occupied by the other country
        outSchema['properties']['vs_status'] = 'str'
        outSchema['properties']['donor_iso'] = 'str'
        outSchema['properties']['watch_iso'] = 'str'

        for i in list_attribute_title:
            outSchema['properties'][i] = 'str'

        # use WGS 84 , longlat , the kind of global use of Coordinate Reference System
        crs = from_epsg(4326)

        polygon_shp = comparing_country + ' to ' + other+ '_voronoi.shp'
        output_polygon_fullpath = output_polygon_name + polygon_shp

        point_shp = comparing_country + ' to ' + other+ '_point.shp'
        output_point_fullpath = output_point_name + point_shp

        with fiona.collection(output_polygon_fullpath,'w', 'ESRI Shapefile', outSchema,crs) as output:
            for polygon in list_clipped_polygon:
                is_att_assign = False
                attribute_each_record = {}
                # nonconflict & the comparing country (the one comparing with others)
                df_noncon_comparing = aftertime_df[condition_non_conconflict & condition_comparing]
                lonlat_noncon_compare = df_noncon_comparing.loc[:, ['longitude', 'latitude']]
                point_noncon_compare = list(MultiPoint(lonlat_noncon_compare.values).geoms)

                for point in point_noncon_compare:
                    if point.within(polygon):
                        # 0 for non-conflicting
                        attribute_each_record['vs_code'] = 0
                        attribute_each_record['vs_status'] = 'non-conflicting'
                        attribute_each_record['donor_iso'] = comparing_country
                        attribute_each_record['watch_iso'] = comparing_country

                        is_same_lat = aftertime_df.latitude == point.y
                        is_same_lon = aftertime_df.longitude == point.x
                        # fill each field with their value
                        for ii in list_attribute_title:
                            value = str(aftertime_df[is_same_lat & is_same_lon].head(1)[ii].values[0])
                            attribute_each_record[ii] = value
                        output.write({
                            'properties': attribute_each_record,
                            'geometry': mapping(polygon)
                        })
                        is_att_assign = True
                        break
                    else:
                        continue

                # if polygon has found matching point, continue to the next polygon
                if is_att_assign:
                    continue

                # nonconflict & one of the others

                df_non_other = aftertime_df[condition_non_conconflict & condition_other]
                lonlat_noncon_other = df_non_other.loc[:, ['longitude', 'latitude']]
                point_noncon_other = list(MultiPoint(lonlat_noncon_other.values).geoms)

                for point in point_noncon_other:
                    if point.within(polygon):
                        # 0 for non-conflicting
                        attribute_each_record['vs_code'] = 2
                        attribute_each_record['vs_status'] = 'non-conflicting'
                        attribute_each_record['donor_iso'] = other
                        attribute_each_record['watch_iso'] = comparing_country


                        is_same_lat = aftertime_df.latitude == point.y
                        is_same_lon = aftertime_df.longitude == point.x
                        # fill each field with their value
                        for ii in list_attribute_title:
                            value = str(aftertime_df[is_same_lat & is_same_lon].head(1)[ii].values[0])
                            attribute_each_record[ii] = value
                        output.write({
                            'properties': attribute_each_record,
                            'geometry': mapping(polygon)
                        })
                        is_att_assign = True
                        break
                    else:
                        continue

                if is_att_assign:
                    continue

                # conflicting
                df_con = aftertime_df[condition_conflict]
                lonlat_con = df_con.loc[:, ['longitude', 'latitude']]
                point_con = list(MultiPoint(lonlat_con.values).geoms)

                for point in point_con:
                    if point.within(polygon):
                        # 0 for non-conflicting
                        attribute_each_record['vs_code'] = 1

                        attribute_each_record['donor_iso'] = other + '|' +comparing_country

                        is_same_lat = aftertime_df.latitude == point.y
                        is_same_lon = aftertime_df.longitude == point.x
                        # fill each field with their value
                        for ii in list_attribute_title:
                            value = str(aftertime_df[is_same_lat & is_same_lon].head(1)[ii].values[0])
                            attribute_each_record[ii] = value
                        output.write({
                            'properties': attribute_each_record,
                            'geometry': mapping(polygon)
                        })
                        is_att_assign = True
                        break
                    else:
                        continue

                if is_att_assign:
                    continue
                else:
                    attribute_each_record['vs_code'] = -1
                    attribute_each_record['vs_status'] = 'void'
                    attribute_each_record['vs_status'] = 'void'
                    attribute_each_record['donor_iso'] = 'void'
                    for ii in list_attribute_title:
                        value = ''
                        attribute_each_record[ii] = value
                    output.write({
                        'properties': attribute_each_record,
                        'geometry': mapping(polygon)
                    })

        print output_polygon_fullpath + ' is created'

        outSchema = {'geometry': 'Point', 'properties': {}}

        # some title has been excluded to be added in the attribute table of voronoi output shapefile
        list_attribute_title = [
            str(aftertime_df.columns[ii])
            for ii in range(len(aftertime_df.columns))
            if 'Unnamed: 0' != aftertime_df.columns[ii]
            if 'latitude' != aftertime_df.columns[ii]
            if 'longitude' != aftertime_df.columns[ii]
            ]

        for i in list_attribute_title:
            outSchema['properties'][i] = 'str'

        with fiona.collection(output_point_fullpath,'w', 'ESRI Shapefile', outSchema,crs) as output:
            for point in point_two_country:
                attribute_each_record = {}
                is_same_lat = aftertime_df.latitude == point.y
                is_same_lon = aftertime_df.longitude == point.x
                try:
                    for ii in list_attribute_title:
                        value = str(aftertime_df[is_same_lat & is_same_lon].head(1)[ii].values[0])
                        attribute_each_record[ii] = value
                except:
                    # continue if point is one of points used to wrap voronoi polygon E.G.(5000, 5000), (
                    continue
                output.write({
                    'properties': attribute_each_record,
                    'geometry': mapping(point)
                })
        print output_point_fullpath + ' is created'









#######################################################################

# make sure only run this script directly will have all functions work

if __name__ == '__main__':
    AutoVoronoi_config.load_input()
    if AutoVoronoi_config.voronoi_mode == 0:
        main()
    elif AutoVoronoi_config.voronoi_mode == 1:
        highlight_mode()
    elif AutoVoronoi_config.voronoi_mode == 2:
        pairwise_mode()

