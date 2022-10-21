# Pranav Minasandra
# pminasandra@ab.mpg.de
# August 19, 2022

import datetime as dt
import glob
import multiprocessing as mp
import os
import os.path

import numpy as np
import pandas as pd

import accreading
import config
import calibration

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
    assert calibration.calibration_file_exists(filename)
    acc_df = calibration.calibrate_all_files(acc_df, calibration.calibration_file(filename))
    datetime_min = acc_df['datetime'].min()
    datetime_max = acc_df['datetime'].max()
    cols = [f.__name__ for f in FEATURES_TO_USE]
    cols += [f.__name__ for f in FOURIER_FEATURES_TO_USE]


    curr_time = _round_to_nearest_second(datetime_min)
    curr_row = 0
    rows_in_epoch = int(config.EPOCH*config.ACC_FREQ)
    first_epoch = True
    time_skip_detected = False
    while curr_time < datetime_max:
        if first_epoch:
            first_epoch = False
            time_diff = (curr_time - acc_df['datetime'][0]).total_seconds()
            if time_diff > 0:
                if time_diff/config.EPOCH > config.EPOCH_OVERHANG_TOLERANCE:
                    curr_row += int((config.EPOCH - time_diff)*rows_in_epoch)
                    curr_time += dt.timedelta(int((config.EPOCH - time_diff)*rows_in_epoch))
                else:
                    next_second_start = curr_row+int((config.EPOCH - time_diff)*rows_in_epoch)
                    yield curr_time, acc_df[['x', 'y', 'z']][curr_row:next_second_start].to_numpy()
                    curr_time += dt.timedelta(seconds=int((next_second_start - curr_row)/rows_in_epoch))
                    curr_row = next_second_start
            elif time_diff == 0:
                yield curr_time, acc_df[['x', 'y', 'z']][curr_row:curr_row+rows_in_epoch].to_numpy()
                curr_time += dt.timedelta(seconds=config.EPOCH)
                curr_row += int(config.EPOCH)*rows_in_epoch
            else:
                curr_time += dt.timedelta(seconds=config.EPOCH-abs(time_diff))
                curr_row += int(config.EPOCH - abs(time_diff))*rows_in_epoch

        row_end = curr_row + int(config.EPOCH*rows_in_epoch)
        epoch_dur = (acc_df['datetime'][row_end] - acc_df['datetime'][curr_row]).total_seconds()
        if epoch_dur > 2*config.EPOCH:
            time_skip_detected = True
            true_row_end = row_end
            true_epoch_dur = (acc_df['datetime'][true_row_end] - acc_df['datetime'][curr_row]).total_seconds()
            while row_end > curr_row:
                epoch_dur = (acc_df['datetime'][row_end] - acc_df['datetime'][curr_row]).total_seconds()
                if epoch_dur <= config.EPOCH:
                    if epoch_dur < config.EPOCH*(1 - config.EPOCH_OVERHANG_TOLERANCE):
                        curr_row = true_row_end
                        curr_time = acc_df['datetime'][true_row_end]
                    else:
                        yield curr_time, acc_df[['x', 'y', 'z']][curr_row:row_end].to_numpy()
                        curr_time = acc_df['datetime'][true_row_end]
                        curr_row = true_row_end
                row_end -= 1
        else:
            if epoch_dur < config.EPOCH*(1 - config.EPOCH_OVERHANG_TOLERANCE):
                curr_time += dt.timedelta(seconds = int((row_end - curr_row)/rows_in_epoch))
                curr_row = row_end
            else:
                yield curr_time, acc_df[['x', 'y', 'z']][curr_row:row_end].to_numpy()
                curr_time += dt.timedelta(seconds = int((row_end - curr_row)/rows_in_epoch))
                curr_row = row_end

        if time_skip_detected:
            time_skip_detected = False
            potential_curr_time = _round_to_nearest_second(curr_time)
            time_diff = (potential_curr_time - curr_time).total_seconds()
            if time_diff > 0:
                curr_time += dt.timedelta(seconds=time_diff)
                curr_row += int(time_diff*rows_in_epoch)
            elif time_diff == 0:
                pass
            else:
                curr_time += dt.timedelta(seconds = config.EPOCH + time_diff)
                curr_row += int((config.EPOCH + time_diff)*rows_in_epoch)

## Features to be extracted

@feature
def x_mean(x,y,z):
    del y,z
    return x.mean()

@feature
def x_var(x,y,z):
    del y,z
    return x.var()

@feature
def x_min(x,y,z):
    del y,z
    return x.min()

@feature
def x_max(x,y,z):
    del y,z
    return x.max()

@feature
def y_mean(x,y,z):
    del x,z
    return y.mean()

@feature
def y_var(x,y,z):
    del x,z
    return y.var()

@feature
def y_min(x,y,z):
    del x,z
    return y.min()

@feature
def y_max(x,y,z):
    del y,z
    return y.max()

@feature
def z_mean(x,y,z):
    del x,y
    return z.mean()

@feature
def z_var(x,y,z):
    del x,y
    return z.var()

@feature
def z_min(x,y,z):
    del x,y
    return z.min()

@feature
def z_max(x,y,z):
    del x,y
    return z.max()

@feature
def vedba(x,y,z):
    xr = x - x.mean()
    yr = y - y.mean()
    zr = z - z.mean()

    res = (xr**2 + yr**2 + zr**2)**0.5
    return res.sum()

##

def _extract_all_features_from(File, header="choose"):
    """
    Extracts all features avaiilable from an e-Obs generated tsv files, writes to usable csv fil
    Args:
        File (str): file from which to extract features
        header (str): string to write in header of generated csv file. If value is "choose", automatically computes header.
    Returns:
        None
    Raises:
        None so far
    """

    assert len(FEATURES_TO_USE) + len(FOURIER_FEATURES_TO_USE) > 0, "there are no features defined"
    print(f"{os.path.basename(__file__):} feature extraction started from {os.path.basename(File)}")
 
    feature_buffer = []
    with open(f"{config.DATA_DIR}features/{os.path.basename(File)[:-4]}.csv", "w") as data_table:
        cols = [f.__name__ for f in FEATURES_TO_USE]
        cols += [f.__name__ for f in FOURIER_FEATURES_TO_USE]
        cols = ['datetime'] + cols
        if header=="choose":
            data_table.write(",".join(cols) + "\n")
        else:
            data_table.write(header + "\n")

    dataset = data_from(File)
    for time, data in dataset:
        x = data[:,0]
        y = data[:,1]
        z = data[:,2]

        x_fft = np.fft.fft(x)[1:11]
        y_fft = np.fft.fft(y)[1:11]
        z_fft = np.fft.fft(z)[1:11]

        normal_features = [f(x,y,z) for f in FEATURES_TO_USE]
        fourier_features = [f(x_fft,y_fft,z_fft) for f in FOURIER_FEATURES_TO_USE]

        if len(normal_features) > 0:
            seperator = ","
        else:
            seperator = ""
        feature_buffer.append(str(time)+ ","+ ",".join([str(val) for val in normal_features]) + seperator + ",".join([str(val) for val in fourier_features]) +"\n")

        if len(feature_buffer) >= 500:
            with open(f"{config.DATA_DIR}features/{os.path.basename(File)[:-4]}.csv", "a") as data_table:
                for line in feature_buffer:
                    data_table.write(line)
            feature_buffer = []

    if len(feature_buffer) > 0:
        with open(f"{config.DATA_DIR}features/{os.path.basename(File)[:-4]}.csv", "a") as data_table:
            for line in feature_buffer:
                data_table.write(line)

    print(f"{os.path.basename(__file__):} feature extraction completed for {os.path.basename(File)}")


#data_from(f"{config.DATA_DIR}acc/tag9483_acc.txt")
#extract_all_features()
def extract_all_features(list_of_files="auto", header="auto"):
    if list_of_files == "auto":
        list_of_files = glob.glob(f"{config.DATA_DIR}acc/tag*.txt")
    pool = mp.Pool(config.NUM_CORES)
    pool.starmap(_extract_all_features_from, [(f, header) for f in list_of_files])
    pool.join()
    pool.close()
    
if __name__ == "__main__":
    extract_all_features(list_of_files="auto", header="auto")
