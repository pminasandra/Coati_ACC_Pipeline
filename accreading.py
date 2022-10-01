# Pranav Minasandra
# pminasandra.github.io
# September 06, 2022

import datetime as dt
import locale

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
import pandas as pd

import config

def read_acc_file(filename):
    """
    Reads an e-Obs DataDecoder generated txt file with a time-column (see README).
    Args:
        filename (str): /path/to/file
    Returns:
        pd.DataFrame() object with dates and ACC time-series
    Raises:
        None so far
    """

    df = pd.read_csv(filename, sep=',', names=['acc_type', 'some_number', 'datetime.date', 'datetime.weekday', 'datetime.time', 'x', 'y', 'z'])
    df = df[['acc_type', 'datetime.date', 'datetime.weekday', 'datetime.time', 'x', 'y', 'z']]
    df['datetime.weekday'] = df['datetime.weekday'].str.replace('So', 'Sun')
    df['datetime.weekday'] = df['datetime.weekday'].str.replace('Mo', 'Mon')
    df['datetime.weekday'] = df['datetime.weekday'].str.replace('Tu', 'Tue')
    df['datetime.weekday'] = df['datetime.weekday'].str.replace('We', 'Wed')
    df['datetime.weekday'] = df['datetime.weekday'].str.replace('Th', 'Thu')
    df['datetime.weekday'] = df['datetime.weekday'].str.replace('Fr', 'Fri')
    df['datetime.weekday'] = df['datetime.weekday'].str.replace('Sa', 'Sat')
    df['datetime'] = df['datetime.date'] + " " + df['datetime.weekday'] + " " + df['datetime.time']
    df = df[['acc_type', 'datetime', 'x', 'y', 'z']]
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d.%m.%Y %a %H:%M:%S.%f')

    if config.SYNC_ACC_FOR_EOBS_DRIFT:
        df['datetime'] = df['datetime'] - dt.timedelta(seconds=config.ACC_GPS_OFFSET)
    return df


if __name__ == "__main__":
    df = read_acc_file(f'{config.DATA_DIR}acc/tag9385_acc.txt')
    df_norm_vec = (((df['x']/1000)**2 + (df['y']/1000)**2 + (df['z']/1000)**2)**0.5).to_numpy()
    plt.plot(df['datetime'], df_norm_vec)
    plt.show()
