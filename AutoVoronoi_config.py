'''
Please read the following description before editing configuration parameters down below

Please keep this configuration placed in the same folder with AutoVoronoi_AidData_seperate_land.py and


'''
level1_fullpath = None
boundary_fullpath = None
output_polygon_fullpath = None
output_point_fullpath = None
attribute_csv_fullpath = None
# for time filter:
allow_empty_time_record = True
is_searching_time = None
# voronoi mode
voronoi_mode = None
dict_filter = None

'''
please revise input parameter
'''
__level1_fullpath = '/Users/EugeneWang/Desktop/AidData/Spatial Voronoi/spatial-voronoi/TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1/data/level_1a.csv'
__boundary_fullpath = '/Users/EugeneWang/Desktop/AidData/project1/TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1/TLS_adm_shp/TLS_adm0.shp'
__output_polygon_fullpath = 'TEST_USA.shp'
__output_point_fullpath = 'Test_USA_point.shp'

# if setting csv file is default
__attribute_csv_fullpath = 'default'

__dict_filter = {}
# if dict_filter remain {}, no record will be filtered.
# dict_filter['ad_sector_codes'] = 311
__dict_filter['donors_iso3'] = 'USA'



# choosing voronoi mode:
# 0 - records not fitting filter will be ignored.
# 1 - all records are involved in voronoi analysis, but highlight those fitting against the others
# 2 - Pair-wise comparison. checking one country and those others countries has connection with it.
    # PS: the connectiong of donating money to the same place or city.
__voronoi_mode = 0

def check_input()
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
    except:
        raise ImportError('Please check filter dictionray has been inputted properly in input configuration file.')

    try:
        voronoi_mode = int(__voronoi_mode)
    except:
        raise ImportError('Please check voronoi mode has been inputted properly under instruction.')



