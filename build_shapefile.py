from datetime import datetime
import pandas
import shapefile

from track_buses import OUTPUT_FILE as BUS_DATA

# the Writer generates multiple files with different extensions
OUTPUT_PREFIX = "bus_tracking"

df = pandas.read_csv(BUS_DATA, names=['vid', 'tmstmp', 'lat', 'lon', 'hdg', 'pid', 'rt', 'des', 'pdist',
                                      'dly', 'tatripid', 'origtatripno', 'tablockid', 'zone'])

with shapefile.Writer(OUTPUT_PREFIX) as shp:
    shp.field('vehicle_id', 'N')
    shp.field('timestamp', 'N')  # the 'D' type can only store dates, no times, so we'll use a Unix timestamp here
    shp.field('route', 'C', size=4)
    shp.field('destination', 'C')

    for row in df.itertuples(index=False):
        shp.point(row.lon, row.lat)
        shp.record(row.vid, int(datetime.strptime(row.tmstmp, "%Y%m%d %H:%M:%S").timestamp()), row.rt, row.des)
