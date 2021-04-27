import pandas as pd
import numpy as np

ODO_SAMPLE_TIME = .4
ODOA = 0
ODOB = 1
ODOC = 2
ODO_MIN = [51,51,53]
ODO_MAX = [971,967,966]
ROLLOVER_DIFF = 40 
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
                if int(df.at[prevIdx, 'WHEEL_A']) + previousDiff[ODOA]*i < ODO_MAX[ODOA] and int(df.at[prevIdx, 'WHEEL_A']) + previousDiff[ODOA]*i > 0 :
                    df.at[prevIdx+i, 'WHEEL_A'] = int(df.at[prevIdx+i-1, 'WHEEL_A']) + previousDiff[ODOA]
                else:
                    if int(df.at[prevIdx+i-1, 'WHEEL_A']) - ROLLOVER_DIFF > ODO_MIN[ODOA]:
                        df.at[prevIdx+i, 'WHEEL_A'] = int(df.at[prevIdx+i-1, 'WHEEL_A']) - ROLLOVER_DIFF
                    else:
                        df.at[prevIdx+i, 'WHEEL_A'] = ODO_MAX[ODOA] + previousDiff[ODOA]*i

        if( int(df.at[prevIdx, 'WHEEL_B']) + int(df.at[curIdx, 'WHEEL_B']) != 0 ):
            if odoBDiff > 0:
                df.at[prevIdx+i, 'WHEEL_B'] = int(df.at[prevIdx, 'WHEEL_B']) + int(i*odoBDiffPerSample)
            else:
                if int(df.at[prevIdx, 'WHEEL_B']) + previousDiff[ODOB]*i < ODO_MAX[ODOB] and int(df.at[prevIdx, 'WHEEL_B']) + previousDiff[ODOB]*i > 0 :
                    df.at[prevIdx+i, 'WHEEL_B'] = int(df.at[prevIdx+i-1, 'WHEEL_B']) + previousDiff[ODOB]
                else:
                    if int(df.at[prevIdx+i-1, 'WHEEL_B']) - ROLLOVER_DIFF > ODO_MIN[ODOB]:
                        df.at[prevIdx+i, 'WHEEL_B'] = int(df.at[prevIdx+i-1, 'WHEEL_B']) - ROLLOVER_DIFF
                    else:
                        df.at[prevIdx+i, 'WHEEL_B'] = ODO_MAX[ODOB] + previousDiff[ODOB]*i

        if( int(df.at[prevIdx, 'WHEEL_C']) + int(df.at[curIdx, 'WHEEL_C']) != 0 ):
            if odoCDiff > 0:
                df.at[prevIdx+i, 'WHEEL_C'] = int(df.at[prevIdx, 'WHEEL_C']) + int(i*odoCDiffPerSample)
            else:
                if int(df.at[prevIdx, 'WHEEL_C']) + previousDiff[ODOC]*i < ODO_MAX[ODOC] and int(df.at[prevIdx, 'WHEEL_C']) + previousDiff[ODOC]*i > 0 :
                    df.at[prevIdx+i, 'WHEEL_C'] = int(df.at[prevIdx+i-1, 'WHEEL_C']) + previousDiff[ODOC]
                else:
                    if int(df.at[prevIdx+i-1, 'WHEEL_C']) - ROLLOVER_DIFF > ODO_MIN[ODOC]:
                        df.at[prevIdx+i, 'WHEEL_C'] = int(df.at[prevIdx+i-1, 'WHEEL_C']) - ROLLOVER_DIFF
                    else:
                        df.at[prevIdx+i, 'WHEEL_C'] = ODO_MAX[ODOC] + previousDiff[ODOC]*i

        i+=1

    if odoADiff > 0:
        previousDiff[ODOA] = odoADiff
    if odoBDiff > 0:
        previousDiff[ODOB] = odoBDiff
    if odoCDiff > 0:
        previousDiff[ODOC] = odoCDiff

previousIndex = 0
for index, row in df.iterrows():
    if row.sum() != 0:
        interpolateData( int(index), previousIndex )
        previousIndex = int(index)


for index, row in df.iterrows():
    df.at[index, 'WHEEL_A'] = int(row['WHEEL_A']) << 6
    df.at[index, 'WHEEL_B'] = int(row['WHEEL_B']) << 6
    df.at[index, 'WHEEL_C'] = int(row['WHEEL_C']) << 6

df.to_csv('interp.csv', index=False)