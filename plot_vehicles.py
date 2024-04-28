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
