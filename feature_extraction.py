# Pranav Minasandra
# pminasandra@ab.mpg.de
# August 19, 2022

import datetime as dt

import pandas as pd

import accreading
import config

FEATURES_TO_USE = []
FOURIER_FEATURES_TO_USE = []

def _round_to_nearest_second(datetime_obj):
    if datetime_obj.microsecond <= config.EPOCH_OVERHANG_TOLERANCE*1e6:
        return datetime_obj - dt.timedelta(microseconds = datetime_obj.microsecond)
    else:
        return datetime_obj + dt.timedelta(microseconds = 1e6 - datetime_obj.microsecond)

def feature(feature_func):
    """
    --> DECORATOR <--
    Use this to decorate feature functions
    """
    global FEATURES_TO_USE
    FEATURES_TO_USE.append(feature_func)
    return feature_func

def fourier_feature(feature_func):
    """
    --> DECORATOR <--
    Use this to decorate feature functions on frequency domain data
    """
    global FOURIER_FEATURES_TO_USE
    FOURIER_FEATURES_TO_USE.append(feature_func)
    return feature_func

def data_from(filename):
    """
    --> GENERATOR <--
    Retrieve data from filename as an iterable
    Args:
        filename (str): path to file to work with
    Yields:
        2-tuple with datetime and np table for all data
    Raises:
        None so far
    """
    acc_df = accreading.read_acc_file(filename)
    datetime_min = acc_df['datetime'].min()
    datetime_max = acc_df['datetime'].max()

    cols = [f.__name__ for f in FEATURES_TO_USE]
    df = pd.DataFrame(columns=(['datetime'] + cols))

    curr_time = _round_to_nearest_second(datetime_min)
    while curr_time < datetime_max:
        np_tab = acc_df[(curr_time <= acc_df['datetime']) & (acc_df['datetime'] < curr_time + dt.timedelta(seconds = config.EPOCH))][['x','y','z']].to_numpy()
        if len(np_tab != 0):
            yield (curr_time, np_tab)
        curr_time += dt.timedelta(seconds = config.EPOCH)

def extract_all_features():
    """
    Extracts all features avaiilable from all e-Obs generated tsv files
    Args:
        None
    Returns:
        pd.DataFrame() object with all extracted features
    Raises:
        None so far
    """
    pass
