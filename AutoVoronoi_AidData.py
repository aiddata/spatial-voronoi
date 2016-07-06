"""
Author: Eugene Wang
This code can be found in this Github Address: https://github.com/itpir/spatial-voronoi
Established at Jun 23 2016
"""
import pandas as pd
import numpy as np
import os
from shapely.geometry import LineString, MultiPoint, mapping, shape
from scipy.spatial import Voronoi
import fiona
from fiona.crs import from_epsg
import shapely.ops

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
    if setting_csv_address == 'default':
        df_csv = read_setting('default_setting_voronoi.csv')
    else:
        try:
            filename, file_ext = os.path.splitext(setting_csv_address)
            if os.path.isfile(setting_csv_address) & file_ext == ('.csv'):
                df_csv = read_setting(setting_csv_address)
            else:
                print 'This input setting file is not wrong. It should be a .csv file'
        except:
            print 'The setting file has an incorrect address or incorrect format'
    # input_df = pd.read_csv(input_address, encoding= 'utf-8')

    # this function is not debugged or test fully yet
    # filter the dataframe with filter_dict
    filtered_subset = filter_dataframe(input_address, filter_dict)

    # get dataframe with only the fields listed in the setting file
    title_field = ['latitude','longitude']
    title_field_additional = []
    for i in df_csv['field_name']:
        title_field.append(str(i))
        title_field_additional.append(str(i))
    filtered_subset = filtered_subset.loc[:, title_field]

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

        # set a list to store a list of unique values
        list_content_field = []
        # handling with every field, looping all field
        for str_field in title_field_additional:
            # get them to list
            # get unique values by using 'set'
            set_field = set(subset_overlapping[str_field].tolist())
            for e in set_field:
                temp_list_field = str(e).split('|')
                list_field = combineTwoList(list_content_field, temp_list_field)

            list_field.sort()
            str_field_content = "|".join(list_field)

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
    csvfile_name = 'filtered_aggregated_data.csv'
    cleaned_data.to_csv(csvfile_name, encoding='utf-8')
    print ('information has been aggregated to ' + csvfile_name)

    return cleaned_data


'''
function 1.1: read_setting()
description: load setting csv into dataframe
input: csv(Setting CSV address or 'default')
return: dataframe (dataframe of setting)
'''
def read_setting(csv):
    dataframe = pd.read_csv(csv, encoding='utf-8')
    return dataframe

'''
function 1.2: filter_dataframe()
description: filter dataframe based on certain conditions in filter_dict
input: input_dfadd(an address of input file), filter_dict(a dictionary, key is field name and values are conditions)
return: filtered_subset



sample of filter_dict:      #lat and long will be used without any statement
{'sector': [311,310,998], 'donors_iso3': ['USA']}
{'aaa':['USA']}  Even only one word is search for field 'aaa', make the word in a list
{'donors_iso3':'USA'} The value can be only a string value
'''
def filter_dataframe(input_dfadd, filter_dict):

    subset_overlapping = pd.read_csv(input_dfadd, encoding='utf-8')
    if filter_dict is None:
        return subset_overlapping

    list_keys = filter_dict.keys()
    list_values = filter_dict.values()
    condition_key = None
    condition_all = None


    # loop every key and value to complete boolean value
    for i in range(len(list_keys)):
        key = list_keys[i]
        value = list_values[i]
        condition_key = get_condition_key(value,key,input_dfadd)
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
        print 'processing filter: field \'%s\' contain %s' %(key_filter, value_filter)
        if condition_key is None:
            condition_key = input_df[key_filter].str.contains(value_filter, na=False)
        else:
            new_boolean = input_df[key_filter].str.contains(value_filter, na= False)
            condition_key = condition_key | new_boolean
    elif type(value_filter) is int:
        print 'processing filter: field \'%s\' contain %d' %(key_filter, value_filter)
        if condition_key is None:
            condition_key = input_df[key_filter].str.contains(str(value_filter), na=False)
        else:
            new_boolean = input_df[key_filter] == value_filter
            condition_key = condition_key | new_boolean
    elif type(value_filter) is float:
        print 'processing filter: \'%s\' contain %d' % (key_filter, value_filter)
        if condition_key is None:
            condition_key = input_df[key_filter] == input_df[key_filter].str.contains(str(value_filter), na=False)
        else:
            new_boolean = input_df[key_filter] == value_filter
            condition_key = condition_key | new_boolean
    elif type(value_filter) is list:
        # this algorithm make all element in a list equal to each other.
        # Even elements in another list wrapped within this list
        stack_condition = None
        for counter, item in enumerate(value_filter):
            new_condition = get_condition_key(item, key_filter, input_dfadd)
            if counter == 0:
                stack_condition = new_condition
            else:
                stack_condition = stack_condition | new_condition
        condition_key = stack_condition

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
function 2: polygonize_list()
# description:
# input: vor(Scipy.Voronoi() object )
# return: list_polygon [if times allow, planning to make my own class including polygon and its attributes]
'''
def polygonize_list(vor, attri):
    # convert it to line objects


    return

'''
# function 3: output_clipped_voronoi()
# desciption: clip voronoi polygon by mask of country, spatially join fields to polygons.
# input:cleaned_df, list_polygon,
# return: none
# output: ESRI shapefile
'''
def output_clipped_voronoi():



    return


'''
# function 4:
# desciption: based on aggregated dataframe, output voronoi analysis in shapefile and fields as attribute
# input:
# return:
'''

#####################################################################################################################
'''
This function is executed only when this script will be run directly.
'''
def main():
    # read level1 csv data
    input_address = os.getcwd()+'/TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1/data/level_1a.csv'
    dcsv = pd.read_csv(input_address)

    '''testing code for dict_filter'''
    dict_filter = {}
    dict_filter['donors_iso3'] = ['USA', 'SWE']
    '''testing. Shoule be deleted when dict_filter is loaded from outside file'''
    clean_df = aggregate_lv1_by_location(input_address,filter_dict=dict_filter)

    # get the numpy array of latitude and longitude
    att_lon_lat = clean_df.loc[:, ['longitude', 'latitude']].values

    # append some points to set up bound the whole voronoi so unbounded polygon ban be shown in SHP
    # with (5000, 5000) and other three corners
    extra_point = np.array([[5000, 5000], [5000, -5000], [-5000, -5000], [-5000, 5000]])
    att_lon_lat = np.concatenate((att_lon_lat, extra_point))
    vor = Voronoi(att_lon_lat)

    # get lines of voronoi polygon
    lines = [
        LineString(vor.vertices[line])
        for line in vor.ridge_vertices
        if -1 not in line
        ]

    areas = list(shapely.ops.polygonize(lines))

    # load coordinates into multipoints object
    mtpoints = MultiPoint(att_lon_lat)

    # use list(points.geoms) or list(points) to access each point in MultiPoint object
    list_points = list(mtpoints.geoms)

    # spatially joined data
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
    # the input shapefile of boundary
    boundary_address = '/Users/EugeneWang/Desktop/AidData/project1/TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1/TLS_adm_shp/TLS_adm0.shp'

    '''
        filter(bbox=None)
        Returns an iterator over records, but filtered by a test for spatial intersection with
        the provided bbox, a (minx, miny, maxx, maxy) tuple.
    '''


    with fiona.collection(boundary_address,'r') as layer_boundary:
        # loop through bounary polygon
        for record_boundary in layer_boundary.filter():
            polygon_boundary = shape(record_boundary['geometry'])
            # LOOP FILTERED TABLE TO GET TITLE AS KEY AND VALUE AS VALUE IN DICT
            with fiona.collection('TEST_agri.shp','w','ESRI Shapefile', outSchema,crs) as output:
                for polygon in areas:
                    attribute_each_record = {}
                    # see if country boundary intersect with this voronoi polygon
                    if polygon_boundary.intersects(polygon):
                        # the polygon clipped
                        intersection_polygon = polygon.intersection(polygon_boundary)

                        for point in list_points:
                            if point.within(intersection_polygon):
                                is_same_lat = clean_df.latitude == point.y
                                is_same_lon = clean_df.longitude == point.x

                                dict_properties = {}
                            # fill each field with their value
                                for ii in list_attribute_title:
                                    value = str(clean_df[is_same_lat & is_same_lon].head(1)[ii].values[0])
                                    attribute_each_record[ii] = value

                                output.write({
                                    'properties':attribute_each_record,
                                    'geometry':mapping(intersection_polygon)
                                })
                            else:
                                continue
                    else:
                        continue









if __name__ ==  '__main__':
    main()