"""
READ ME:
Please read the following description before editing configuration parameters down below

* Please keep this configuration placed in the same folder with AutoVoronoi_AidData_seperate_land.py and
default_setting_voronoi.csv.

* To change or set up configuration, please change variables with __, do not touch variables without please.
For example, to set up the input path of level 1 data, just revise __level1_fullpath.

    Config Variable Explanation:

1. level1_fullpath : sets up the fullpath, a string value, of level 1 data which contains information you need to analyze
    it in a voronoi result.

2. boundary_fullpath : allows you to set up the fullpath, a string value, of a shapefile of country boundary, the region
     level 1 data are about. Those data are categorized based on countries, right?

3. output_polygon_fullpath: allows you to set up the fullpath, a string value, of an output shapefile of voronoi polygon
    with attributes demanded in setting file. PS: setting file will be explained below.

    If you want this output to be saved in the same folder with this file and python script, just type the filename and .shp
    extension, as a string value, of course.

    PS: For pair-wise mode, please indicate an existing folder as fullpath. Otherwise, all files will be placed in a new
    folder under the folder where the running script and this this file are.

    For example:
        for pair-wise mode, this fullpath should be set up like this below :
            _output_polygon_fullpath = '/Users/EugeneWang/Desktop/AidData/Spatial Voronoi/spatial-voronoi/USA vs others_new/'
        for other modes, this fullpath variable should be like this below :
            __boundary_fullpath = '/Users/EugeneWang/Desktop/AidData/project1/TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1/TLS_adm_shp/TLS_adm0.shp'

4. output_point_fullpath: the point version of output_point_fullpath

5. attribute_csv_fullpath: allows you to set up the fullpath, a string value, of a setting csv file.

    These file allows you to specify fields in level 1 data to be convert to their correspondant point / polygon in output
     shapefile, as fields in a record.

    to use a default setting csv file, just specify as 'default', then the default setting csv file 'default_setting_voronoi.csv'
     will be loaded.

6. allow_empty_time_record: When records are filtered by time filter, those records without both start date and end
    date in the record will be allowed as satisfied if this variable 'allow_empty_time_records' is set to be True.

7. voronoi_mode
    # choosing voronoi mode:
    # 0 - records not fitting filter will be ignored.
    # 1 - all records are involved in voronoi analysis, but highlight those fitting against the others
    # 2 - Pair-wise comparison. checking one country and those others countries has connection with it.
    # PS: the connectiong of donating money to the same place or city.


8. dict_filter: allow you to narrow records involved in Voronoi Analysis based on records' part of (int, float,
                str) attribute, or several of these.

    attribute filter dictionary format:
    {'field name':str OR int OR list (, 'field name': str OR int OR list, ...)}
    -str: to get records containing this value in the field 'field name'
    -int: to get records containing this value in the field 'field name'
    -list: the list can have several (or just one) str variables or int variables, these variables works as same as above.
       searching records containing one of variables in the list
    Example:
    __dict_filter = {'sector': [311,310,998], 'donors_iso3': 'USA'}
    Explanation: in this sample above, there is two conditions to find records fulfilling all conditions. The first is
    to find records has 311 or 310 or 998 in the field 'sector'. The second is to find records containing USA in 'donors_iso3'.

    __dict_filter = {'aaa':['USA']}
    Explanation: Even only one word is search for field 'aaa', make the word in a list.

    __dict_filter = {'donors_iso3':'USA'}
    Explanation: The value can be only a string value

    PS: if you know dictionary in Python, you can do this:
    __dict_filter = {}
    __dict_filter['sector'] = [311, 310, 998]
    __dict_filter['donors_iso3'] = 'USA'

    This works as same as:
    __dict_filter = {'sector': [311,310,998], 'donors_iso3': 'USA'}

    Even though it takes more time to type, but you don't need to worry about the format of dictionary. Sometimes
    dictionary's literal format is hard to type and read.

9. time_filter
    time filter dictionary format:
    {'any word':{'start field name': ####, 'end field name'}}

    Example:
    __time_filter = {'example':{'start_actual_isodate':2006, 'end_actual_isodate': 2009}}
    Example: 'example' does not mean anything. The field with the start year of time span is 'start_actual_isodate',
    and the condition is 2006. In the same way to explain, 'end_actual_isodate' is the field name about the end year of
    time span we are looking at. The end year here is 2009.

    The Python way mentioned above also works here.

10. comparing_country_iso : allow you to set up the comparing country in pair-wise mode by inputting their iso3 code.

    This field is a must if the voronoi mode is pair-wise (AKA, if voronoi_mode = 2)

"""


'''
please revise input parameter below
'''
__level1_fullpath = '/Users/EugeneWang/Desktop/AidData/Spatial Voronoi/spatial-voronoi/TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1/data/level_1a.csv'
__boundary_fullpath = '/Users/EugeneWang/Desktop/AidData/project1/TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1/TLS_adm_shp/TLS_adm0.shp'
#_output_polygon_fullpath = '/Users/EugeneWang/Desktop/AidData/Spatial Voronoi/spatial-voronoi/USA vs others_new/'
__output_polygon_fullpath = 'TEST_hightlight_USA_06_08.shp'
#_output_point_fullpath = '/Users/EugeneWang/Desktop/AidData/Spatial Voronoi/spatial-voronoi/USA vs others_points_new/'
__output_point_fullpath = 'Test_highlight_USA_06_08_point.shp'
# if setting csv file is default
__attribute_csv_fullpath = 'default'

# if dict_filter remain {}, no record will be filtered.
# __dict_filter is for fields that is not related to time(eg. starting time, ending time)
__dict_filter = {}
#__dict_filter['donors_iso3'] = 'USA'
#__dict_filter['ad_sector_codes'] = 311

__time_filter = {}
__time_filter['example'] = {'start_actual_isodate':2006, 'end_actual_isodate':2010}

__voronoi_mode = 2
__allow_empty_time_record = False

# for pair-wise mode:
__comparing_country_iso = 'USA'
'''
please revise input parameter above.
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
# pairwise mode must have this input below
comparing_country_iso = None


def load_input():
    global level1_fullpath
    global boundary_fullpath
    global output_polygon_fullpath
    global output_point_fullpath
    global attribute_csv_fullpath
    global dict_filter
    global time_filter
    global allow_empty_time_record
    global comparing_country_iso
    global voronoi_mode

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
        raise ImportError('Please check __voronoi_mode has been inputted properly under instruction.')

    try:
        allow_empty_time_record = bool(__allow_empty_time_record)
    except:
        raise ImportError('Please check __allow_empty_time_record has been inputted properly under instruction.')

    try:
        if voronoi_mode == 2:
            comparing_country_iso = str(__comparing_country_iso)
    except:
        raise ImportError('Please check __comparing_counties_iso has been inputted properly under instruction.')




load_input()




