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
