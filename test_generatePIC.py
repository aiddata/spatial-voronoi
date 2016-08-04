from itertools import chain
from mpl_toolkits.basemap import Basemap
import fiona # fiona or shapely should be imported after Basemap, otherwise there is error
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon
import pandas as pd
import matplotlib.pyplot as plt
import os
from descartes import PolygonPatch
from matplotlib.colors import ListedColormap
from matplotlib.collections import PatchCollection
import matplotlib.cm as cm
import numpy as np

def create_colorbar(list_label, list_status, list_color, cmap, **kwargs):
    ncolors = len(list_color)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, ncolors + 0.5)
    colorbar = plt.colorbar(mappable, **kwargs)
    colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
    colorbar.set_ticklabels(range(ncolors))
    if len(list_label):
        colorbar.set_ticklabels(list_label)
    return colorbar

'''
inputs are below.
'''
input_fullpath='/Users/EugeneWang/Desktop/AidData/Spatial Voronoi/spatial-voronoi/USA vs others_new_new/USA to AUS_voronoi.shp'
fieldname_on_legend = 'donor_iso'
'''
inputs are above
'''
input_name, input_ext = os.path.splitext(input_fullpath)

figure = plt.figure()
ax = figure.add_subplot(111,axisbg='w', frame_on=False)

shp = fiona.open(input_fullpath)
bds = shp.bounds
shp.close()
extra = 0.01
ll = (bds[0], bds[1]) # lower left point
ur = (bds[2], bds[3]) # upper right point
coords = list(chain(ll, ur))
w, h = coords[2] - coords[0], coords[3] - coords[1]

cen_lat = (coords[1] + coords[3])/2
cen_lon = (coords[0] + coords[2])/2

m = Basemap(
    projection='tmerc',
    lon_0=cen_lon,
    lat_0=cen_lat,
    ellps='WGS84',
    llcrnrlon=coords[0] - extra * w,
    llcrnrlat=coords[1] - extra + 0.01 * h,
    urcrnrlon=coords[2] + extra * w,
    urcrnrlat=coords[3] + extra + 0.01 * h,
    lat_ts=0,
    resolution='i',
    suppress_ticks=True,
    ax=ax)

m.drawmapboundary(fill_color='#DFDFDE')
m.fillcontinents(color='#A7A7A7', lake_color='#DFDFDE', zorder=0)

# The options of resolution are c (crude, the default), l (low), i (intermediate), h (high), f (full) or None.
m.readshapefile(
    input_name,
    'polygon_voronoi',
    color='none',
    default_encoding='utf-8'
    #zorder=2
)

# set up a map dataframe, and extract attribute from shapefile
dict_df = {
    'poly': [Polygon(xy) for xy in m.polygon_voronoi],
    fieldname_on_legend : [attribute[fieldname_on_legend] for attribute in m.polygon_voronoi_info],
    'vs_code': [int(attribute['vs_code']) for attribute in m.polygon_voronoi_info]}
df_map = pd.DataFrame(dict_df)
#df_map['area_m'] = df_map['poly'].map(lambda x: x.area)
#df_map['area_km'] = df_map['area_m'] / 100000

# how many classes are needed?
#n = len(set(df_map[fieldname_on_legend].tolist()))

# patches converted with grey color.
df_map['patches'] = df_map['poly'].map(lambda x: PolygonPatch(x, ec='#555555', lw=.2, alpha=1., zorder=4))

# customize color map, only two/three kind of colors + color for void property. To highlight the conflict
statuses = [0, 2, 1, -1] # A, B, conflict, void
colors = ['#ffffbf', '#91cf60', '#fc8d59', '#000000'] # A, B, conflicting, void
cmap = ListedColormap(colors, name='For Pair-wise comparision', N=4)

# loop throught status and color,
# set color to regions based on vs_code
# A or B, or conflict or void.
for status, color in zip(statuses, colors):
    is_eachstatus = df_map.vs_code == status
    df_eachstatus = df_map[is_eachstatus]
    if len(df_eachstatus) == 0:
        continue
    pc = PatchCollection(df_eachstatus['patches'], match_original=True)
    pc.set_facecolor(color) # set color
    ax.add_collection(pc) # add to the axis of figure


# for legend:

list_legendlabels = []
# get the correspondent title with vs_code
for code in statuses:
    find_correspondant = df_map.vs_code == int(code)
    df_eachcode = df_map[find_correspondant]
    title = list(set(df_eachcode[fieldname_on_legend].tolist()))[0]
    list_legendlabels.append(title)
# till now, statuses share the correspondent order with list_legendtitle.

# add a color bar
cb = create_colorbar(list_legendlabels, statuses, colors, cmap, shrink=0.3)
cb.ax.tick_params(labelsize=6)

# add title
title = list_legendlabels[0] + ' and '+ list_legendlabels[1]+' Voronoi Surface'
plt.title(title)

# output picture
outputpath = input_name+'.png'
plt.savefig(outputpath, dpi=300, alpha=True)

plt.show()
