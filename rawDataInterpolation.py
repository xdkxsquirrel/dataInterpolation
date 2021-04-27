import pandas as pd
import numpy as np

ODO_SAMPLE_TIME = .4

df = pd.read_csv('1.csv')
df['Time'] = pd.to_datetime(df['TS_MS'], unit='ms')
df = df.set_index(df['Time'], drop=True)
df = df.resample('400us').interpolate(method='linear')

for index, row in df.iterrows():
    df.at[index, 'WHEEL_A'] = int(row['WHEEL_A']) << 6
    df.at[index, 'WHEEL_B'] = int(row['WHEEL_B']) << 6
    df.at[index, 'WHEEL_C'] = int(row['WHEEL_C']) << 6

df = df.drop(columns=['Time'])
df = df.dropna()
df.to_csv('interp.csv', index=False)