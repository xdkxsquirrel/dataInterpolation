import pandas as pd
import numpy as np

df2 = pd.read_csv('13FPSPulltest.csv')

startValues = [df2.iloc[0]['WHEEL_A'], df2.iloc[0]['WHEEL_B'], df2.iloc[0]['WHEEL_C']]
tempLocations = df2.loc[df2['WHEEL_A'] == startValues[0]].index.to_list()
startValueLocation = []
startValueLocation.append([i for i in tempLocations if i > 500][0])
tempLocations = df2.loc[df2['WHEEL_B'] == startValues[1]].index.to_list()
startValueLocation.append([i for i in tempLocations if i > 500][0])
tempLocations = df2.loc[df2['WHEEL_C'] == startValues[2]].index.to_list()
startValueLocation.append([i for i in tempLocations if i > 500][0])

odoAValues = []
i = 360
while i > 0:
    odoAValues.append(df2.at[startValueLocation[0]-i, 'WHEEL_A'])
    i-=1

odoBValues = []
i = 360
while i > 0:
    odoBValues.append(df2.at[startValueLocation[1]-i, 'WHEEL_B'])
    i-=1

odoCValues = []
i = 360
while i > 0:
    odoCValues.append(df2.at[startValueLocation[2]-i, 'WHEEL_C'])
    i-=1

cols = ['WHEEL_A', 'WHEEL_B', 'WHEEL_C']
newRows = np.stack((odoAValues, odoBValues, odoCValues), axis=-1)
df = pd.DataFrame(newRows, columns=cols)
df = df.append(df2, ignore_index=True)

df.to_csv('tester.csv', index=False)