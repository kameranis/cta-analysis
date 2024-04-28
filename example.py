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
