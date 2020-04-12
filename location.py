#!/usr/bin/env python3

import argparse
from datetime import datetime as dt
import logging

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd

logging.basicConfig()
logger = logging.getLogger(__package__)
logger.setLevel(level=logging.INFO)

parser = argparse.ArgumentParser('Google location history visualiser.')
parser.add_argument('--location-history-json', required=True)
parser.add_argument('--output-png', required=True)
parser.add_argument('--latitude', type=float, required=True)
parser.add_argument('--longtitude', type=float, required=True)
args = parser.parse_args()

df = pd.read_json(args.location_history_json)
logger.info('Loaded {} data points'.format(len(df)))

# Parse lat, lon, and timestamp from the dict inside the locations column
df['lat'] = df['locations'].map(lambda x: x['latitudeE7'])
df['lon'] = df['locations'].map(lambda x: x['longitudeE7'])
df['timestamp_ms'] = df['locations'].map(lambda x: x['timestampMs'])

# convert lat/lon to decimalised degrees and the timestamp to date-time
df['lat'] = df['lat'] / 10.**7
df['lon'] = df['lon'] / 10.**7
df['timestamp_ms'] = df['timestamp_ms'].astype(float) / 1000
df['datetime'] = df['timestamp_ms'].map(lambda x: dt.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
date_range = '{}-{}'.format(df['datetime'].min()[:4], df['datetime'].max()[:4])

# drop columns we don't need, then show a slice of the dataframe
df_gps = df.drop(labels=['locations', 'timestamp_ms'], axis=1, inplace=False)

# define map colors
land_color = '#f2f2f0'
water_color = '#cdd2d4'
coastline_color = '#f5f5f3'
border_color = '#bbbbbb'
meridian_color = '#f5f5f3'
marker_fill_color = '#3FEAE9'
marker_edge_color = 'None'

# first define a transverse mercator projection for california
map_width_m = 25 * 550
map_height_m = 40 * 550
target_crs = {'datum': 'WGS84',
              'ellps': 'WGS84',
              'proj': 'tmerc',
              'lon_0': args.longtitude,
              'lat_0': args.latitude}

# plot the map
fig_width = 6
fig = plt.figure(figsize=[fig_width, fig_width * map_height_m / float(map_width_m)])
ax = fig.add_subplot(111, facecolor='#ffffff', frame_on=False)
ax.set_title('Cambridge'.format(date_range), fontsize=16, color='#333333')

m = Basemap(ellps=target_crs['ellps'],
            projection=target_crs['proj'],
            lon_0=target_crs['lon_0'],
            lat_0=target_crs['lat_0'],
            width=map_width_m,
            height=map_height_m,
            resolution='l',
            area_thresh=10000)

m.drawcoastlines(color=coastline_color)
m.drawcountries(color=border_color)
m.fillcontinents(color=land_color, lake_color=water_color)
m.drawstates(color=border_color)
m.drawmapboundary(fill_color=water_color)

x, y = m(df_gps['lon'].values, df_gps['lat'].values)
m.scatter(x, y, s=0.5, color=marker_fill_color, edgecolor=marker_edge_color, alpha=0.6, zorder=3)

plt.savefig(args.output_png, dpi=600, bbox_inches='tight', pad_inches=0.2)
