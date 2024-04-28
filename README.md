# CTA API Wrapper and Scheduler

Offers a python wrapper to the Chicago Transit Authority bus and trains APIs through two different modules. Additionally, some utilities that work around API call limits like getting all the vehicles in a list. Another utility (which motivated this project) is `track_CTA.py` which pings the API every set amount of seconds and deposits the positions of all buses and trains in separate CSV files. Example dumps can be found on [here](https://uchicago.box.com/s/mulzmxs6f5sua7a1p910nypqtlgzc495).

### Setup
You will need a CTA [bus tracker API](https://www.ctabustracker.com/home) and [train tracker API](https://www.transitchicago.com/developers/traintracker/) key which should be stored in `bus_api_key.txt` and `train_api_key.txt` respectively.

### Example usage
Here is a short example of how to plot all patterns and vehicles

```python3
import matplotlib.pyplot as plt
import pandas as pd

import bus


vehicles = bus.get_all_vehicles()
patterns = bus.get_all_patterns()
df = pd.DataFrame(vehicles)
df[['lon', 'lat']] = df[['lon', 'lat']].astype(float)
lines = [sorted([(point['seq'], point['lon'], point['lat']) for point in pattern['pt']]) for i, pattern in patterns.items()]

fig, ax = plt.subplots()
for line in lines:
    x = [a[1] for a in line]
    y = [a[2] for a in line]
    plt.plot(x, y, 'k-', linewidth=0.5, alpha=0.5, zorder=2)
plt.scatter(df['lon'], df['lat'], s=2, zorder=4)
plt.axis('off')
plt.savefig('example.png', dpi=500, bbox_inches='tight')
plt.show()
```

![Example](example.png?raw=true "Example picture")

Another example is plotting how many vehicles are executing routes over a set timeline.

```python3
import sys

import matplotlib.pyplot as plt
import pandas as pd


df = pd.read_csv(sys.argv[1], names=['vid', 'tmstmp', 'lat', 'lon', 'hdg', 'pid', 'rt', 'des', 'pdist',
                                     'dly', 'tatripid', 'origtatripno', 'tablockid', 'zone'])
df['tmstmp'] = pd.to_datetime(df['tmstmp'])
sample = df[['vid', 'tmstmp']].resample('5Min', on='tmstmp')['vid'].nunique()
sample = sample.loc[sys.argv[2]:sys.argv[3]]
plt.fill_between(sample.index, sample, color='tab:blue')
plt.axis(xmin=sample.index[0], xmax=sample.index[-1], ymin=0)
plt.ylabel('# of unique vehicles active')
plt.xticks(rotation=30)
plt.savefig('Week of vehicles.png', dpi=300, bbox_inches='tight')
plt.show()
```

![Week of vehicles](https://github.com/kameranis/cta-analysis/blob/main/Week%20of%20vehicles.png?raw=true "Week of vehicles")
