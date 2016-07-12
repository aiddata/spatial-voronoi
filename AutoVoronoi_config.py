'''
Please read the following description before editing configuration parameters down below



'''

level1_fullpath = '/Users/EugeneWang/Desktop/AidData/Spatial Voronoi/spatial-voronoi/TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1/data/level_1a.csv'
boundary_fullpath = '/Users/EugeneWang/Desktop/AidData/project1/TimorLesteAIMS_GeocodedResearchRelease_Level1_v1.4.1/TLS_adm_shp/TLS_adm0.shp'

output_polygon_fullpath = 'TEST_USA.shp'
output_point_fullpath = 'Test_USA_point.shp'

dict_filter = {}
# if dict_filter remain {}, no record will be filtered.
# dict_filter['ad_sector_codes'] = 311
dict_filter['donors_iso3'] = 'USA'

# if this is default
attribute_csv_fullpath = 'default'