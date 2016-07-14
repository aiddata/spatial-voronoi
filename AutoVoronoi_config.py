'''
Please read the following description before editing configuration parameters down below

Please keep this configuration placed in the same folder with AutoVoronoi_AidData_seperate_land.py andc

attribute filter dictionary format:
{'field name':str OR int OR list (, 'field name': str OR int OR list, ...)}
-str: to get records containing this value in the field 'field name'
-int: to get records containing this value in the field 'field name'
-list: the list can have several (or just one) str variables or int variables, these variables works as same as above.
       searching records containing one of variables in the list
Example:
    __dict_filter = {'sector': [311,310,998], 'donors_iso3': ['USA']}
    Explanation: in this sample above, there is two conditions to find records fulfilling all conditions. The first is
    to find records has 311 or 310 or 998 in the field 'sector'. The second is to find records containing USA in 'donors_iso3'.

    __dict_filter = {'aaa':['USA']}
    Explanation: Even only one word is search for field 'aaa', make the word in a list

    __dict_filter = {'donors_iso3':'USA'}
    Explanation: The value can be only a string value

time filter dictionary format:
{'any word':{'start field name': ####, 'end field name'}}
Example:
    __time_filter = {'example':{'start_actual_isodate':2006, 'end_actual_isodate': 2009}}
    Example: 'example' does not mean anything. The field with the start year of time span is 'start_actual_isodate',
    and the condition is 2006. In the same way to explain, 'end_actual_isodate' is the field name about the end year of
    time span we are looking at. The end year here is 2009.

# choosing voronoi mode:
# 0 - records not fitting filter will be ignored.
# 1 - all records are involved in voronoi analysis, but highlight those fitting against the others
# 2 - Pair-wise comparison. checking one country and those others countries has connection with it.
    # PS: the connectiong of donating money to the same place or city.
'''
level1_fullpath = None
boundary_fullpath = None
output_polygon_fullpath = None
output_point_fullpath = None
attribute_csv_fullpath = None
# for time filter:
# boolean
allow_empty_time_record = None
# voronoi mode
voronoi_mode = None
# two kinds of filters
dict_filter = None
time_filter = None



'''
please revise input parameter below
'''
__level1_fullpath = '/Users/EugeneWang/Desktop/AidData/Spatial Voronoi/spatial-voronoi/TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1/data/level_1a.csv'
__boundary_fullpath = '/Users/EugeneWang/Desktop/AidData/project1/TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1/TLS_adm_shp/TLS_adm0.shp'
__output_polygon_fullpath = 'TEST_USA.shp'
__output_point_fullpath = 'Test_USA_point.shp'

# if setting csv file is default
__attribute_csv_fullpath = 'default'

# if dict_filter remain {}, no record will be filtered.
__dict_filter = {}
__dict_filter['donors_iso3'] = 'USA'
# __dict_filter['ad_sector_codes'] = 311

__time_filter = {}
# __time_filter['example'] = {'start':2006, 'end':2010}


__voronoi_mode = 0

__allow_empty_time_record = False
'''
please revise input parameter above.
'''


def load_input():
    try:
        level1_fullpath = str(__level1_fullpath)
        boundary_fullpath = str(__boundary_fullpath)
        output_point_fullpath = str(__output_point_fullpath)
        output_polygon_fullpath = str(__output_polygon_fullpath)
        attribute_csv_fullpath = str(__attribute_csv_fullpath)
    except:
        raise ImportError('Please check all input fullpath parameters are writen correctly in Input Configuration file')

    try:
        dict_filter = dict(__dict_filter)
        time_filter = dict(__time_filter)
    except:
        raise ImportError('Please check filter dictionray has been inputted properly in input configuration file.')

    try:
        voronoi_mode = int(__voronoi_mode)
    except:
        raise ImportError('Please check voronoi mode has been inputted properly under instruction.')

    try:
        allow_empty_time_record = bool(__allow_empty_time_record)
    except:
        raise ImportError('Please check allow_empty_time_record has been inputted properly under instruction.')






