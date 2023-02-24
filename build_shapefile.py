import sys
from datetime import datetime
import pandas
import shapefile

from track_buses import BUS_OUTPUT_FILE as BUS_DATA

# the Writer generates multiple files with different extensions
OUTPUT_PREFIX = "bus_tracking"


if __name__ == '__main__':
    df = pandas.read_csv(sys.argv[1], names=['vid', 'tmstmp', 'lat', 'lon', 'hdg', 'pid', 'rt', 'des', 'pdist',
                                          'dly', 'tatripid', 'origtatripno', 'tablockid', 'zone'])

    with shapefile.Writer(sys.argv[2]) as shp:
        shp.field('vehicle_id', 'N')
        shp.field('timestamp', 'C')  # the 'D' type can only store dates, no times, so we'll use a Unix timestamp here
        shp.field('route', 'C', size=4)
        shp.field('destination', 'C')

        for row in df.itertuples(index=False):
            shp.point(row.lon, row.lat)
            shp.record(row.vid, row.tmstmp, row.rt, row.des)


