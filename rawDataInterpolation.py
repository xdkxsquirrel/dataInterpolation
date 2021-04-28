import pandas as pd
import numpy as np

ODO_SAMPLE_TIME = .4
ODOA = 0
ODOB = 1
ODOC = 2
ODO_MIN = [51,51,53]
ODO_MAX = [971,967,966]
ROLLOVER_DIFF = 1 
previousDiff = [0,0,0]

df = pd.read_csv('1.csv')
df['Time'] = pd.to_datetime(df['TS_MS'], unit='ms')
df = df.set_index(df['Time'], drop=True)
df = df.resample('400us').sum()
df.reset_index(drop=True, inplace=True)
df = df.drop(columns=['TS_MS'])

def interpolateData( curIdx, prevIdx ):
    global previousDiff
    global df

    if curIdx == 0:
        return

    idxDiff = curIdx - prevIdx
    odoADiff = int(df.at[curIdx, 'WHEEL_A']) - int(df.at[prevIdx, 'WHEEL_A'])
    odoBDiff = int(df.at[curIdx, 'WHEEL_B']) - int(df.at[prevIdx, 'WHEEL_B'])
    odoCDiff = int(df.at[curIdx, 'WHEEL_C']) - int(df.at[prevIdx, 'WHEEL_C'])

    odoADiffPerSample = odoADiff / idxDiff
    odoBDiffPerSample = odoBDiff / idxDiff
    odoCDiffPerSample = odoCDiff / idxDiff

    i=1
    while( i < idxDiff ):
        if( int(df.at[prevIdx, 'WHEEL_A']) + int(df.at[curIdx, 'WHEEL_A']) != 0 ):
            if odoADiff > 0:
                df.at[prevIdx+i, 'WHEEL_A'] = int(df.at[prevIdx, 'WHEEL_A']) + int(i*odoADiffPerSample)
            else:
                df.at[prevIdx+i, 'WHEEL_A'] = int(df.at[prevIdx+i-1, 'WHEEL_A']) - ROLLOVER_DIFF

        if( int(df.at[prevIdx, 'WHEEL_B']) + int(df.at[curIdx, 'WHEEL_B']) != 0 ):
            if odoBDiff > 0:
                df.at[prevIdx+i, 'WHEEL_B'] = int(df.at[prevIdx, 'WHEEL_B']) + int(i*odoBDiffPerSample)
            else:
                df.at[prevIdx+i, 'WHEEL_B'] = int(df.at[prevIdx+i-1, 'WHEEL_B']) - ROLLOVER_DIFF

        if( int(df.at[prevIdx, 'WHEEL_C']) + int(df.at[curIdx, 'WHEEL_C']) != 0 ):
            if odoCDiff > 0:
                df.at[prevIdx+i, 'WHEEL_C'] = int(df.at[prevIdx, 'WHEEL_C']) + int(i*odoCDiffPerSample)
            else:
                df.at[prevIdx+i, 'WHEEL_C'] = int(df.at[prevIdx+i-1, 'WHEEL_C']) - ROLLOVER_DIFF


        i+=1

    if odoADiff > 0:
        previousDiff[ODOA] = odoADiff
    if odoBDiff > 0:
        previousDiff[ODOB] = odoBDiff
    if odoCDiff > 0:
        previousDiff[ODOC] = odoCDiff

#OVERSAMPLE TICK DATA TO ODO SAMPLE DATA
previousIndex = 0
for index, row in df.iterrows():
    if row.sum() != 0:
        interpolateData( int(index), previousIndex )
        previousIndex = int(index)

#CORRECT ROLLOVERS
startOfRollover = [0,0,0]
for index, row in df.iterrows():
    if index > 2:
        currentValue = df.at[index, 'WHEEL_A']
        previousValue = df.at[index-1, 'WHEEL_A']
        twoValuesAgo = df.at[index-2, 'WHEEL_A']

        if currentValue < previousValue and previousValue > twoValuesAgo:
            startOfRollover[ODOA] = index-1
        elif currentValue > previousValue and previousValue < twoValuesAgo:
            numberOfValuesToChange = index-2 - startOfRollover[ODOA]
            changeInValue = int((df.at[startOfRollover[ODOA], 'WHEEL_A'] - df.at[index-1, 'WHEEL_A']) / (numberOfValuesToChange+1))
            for i in range(numberOfValuesToChange):
                df.at[index-2-i, 'WHEEL_A'] = df.at[index-1-i, 'WHEEL_A'] + changeInValue

        currentValue = df.at[index, 'WHEEL_B']
        previousValue = df.at[index-1, 'WHEEL_B']
        twoValuesAgo = df.at[index-2, 'WHEEL_B']

        if currentValue < previousValue and previousValue > twoValuesAgo:
            startOfRollover[ODOB] = index-1
        elif currentValue > previousValue and previousValue < twoValuesAgo:
            numberOfValuesToChange = index-2 - startOfRollover[ODOB]
            changeInValue = int((df.at[startOfRollover[ODOB], 'WHEEL_B'] - df.at[index-1, 'WHEEL_B']) / (numberOfValuesToChange+1))
            for i in range(numberOfValuesToChange):
                df.at[index-2-i, 'WHEEL_B'] = df.at[index-1-i, 'WHEEL_B'] + changeInValue

        currentValue = df.at[index, 'WHEEL_C']
        previousValue = df.at[index-1, 'WHEEL_C']
        twoValuesAgo = df.at[index-2, 'WHEEL_C']

        if currentValue < previousValue and previousValue > twoValuesAgo:
            startOfRollover[ODOC] = index-1
        elif currentValue > previousValue and previousValue < twoValuesAgo:
            numberOfValuesToChange = index-2 - startOfRollover[ODOC]
            changeInValue = int((df.at[startOfRollover[ODOC], 'WHEEL_C'] - df.at[index-1, 'WHEEL_C']) / (numberOfValuesToChange+1))
            for i in range(numberOfValuesToChange):
                df.at[index-2-i, 'WHEEL_C'] = df.at[index-1-i, 'WHEEL_C'] + changeInValue

#CONVERT FROM 10-bit to 16-bit
for index, row in df.iterrows():
    df.at[index, 'WHEEL_A'] = int(row['WHEEL_A']) << 6
    df.at[index, 'WHEEL_B'] = int(row['WHEEL_B']) << 6
    df.at[index, 'WHEEL_C'] = int(row['WHEEL_C']) << 6

df.to_csv('interp.csv', index=False)