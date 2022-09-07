# Pranav Minasandra
# pminasandra@ab.mpg.de
# August 19, 2022

import datetime as dt
import glob
import logging
import multiprocessing as mp
import os
import os.path
import warnings

import pandas as pd

import config

def _get_delimiter(filename):
    if filename[-4:] == ".csv":
        return ","
    elif filename[-4:] == ".tsv":
        return "\t"
    else:
        return input(
f"""{os.path.basename(__file__)}: could not determine delimiter from {filename}.
    It's usually ',' or '\\t' or something like that.
    Enter it here (without quotation marks):"""
)


def read_audit(auditfile):
    """
    Reads in auditfile generated from BORIS output, and returns UTC-synced audit data in pd.DataFrame

    Args:
        auditfile (str): Path to an audit-file, usually a .tsv or a .csv file.
    Returns:
        pd.DataFrame() object containing UTC time-stamped labels for behavioural states.
    Raises:
        ValueError: for inconsistencies in audit files
    """

    delimiter = _get_delimiter(auditfile)
    df = pd.read_csv(auditfile, sep=delimiter)
    df_relevant = df[['Start (s)', 'Stop (s)', 'Comment start', 'Behavior']]

    # TODO: sanitisation and validation

    df_timestamp = df_relevant.loc[df_relevant['Behavior'] == 'time']['Comment start']
    multiple_timestamps = False
    if len(df_timestamp) > 1:
        multiple_timestamps = True
        df_timestamp_list = []

    if len(df_timestamp) > 1:
        # TODO: Handle multiple time-stamps
        if not config.MULTIPLE_STARTS_ALLOWED:
            raise ValueError("Multiple timestamps encountered, but not allowed. To allow, set the MULTIPLE_STARTS_ALLOWED variable to True in config.py.")
        else:
            if config.MULTIPLE_STARTS_WARNING:
                warnings.warn("{os.path.basename(__file__)}: multiple starts encountered. To supress this warning, set MULTIPLE_STARTS_WARNING to False in config.py.")
            multiple_timestamps = True
            df_timestamp_list = list(df_relevant.loc[df_relevant['Behavior'] == 'time']['Comment start'])
            df_timestamp_loc_list = list(df_relevant.loc[df_relevant['Behavior'] == 'time']['Start (s)'])

    else:
        df_timestamp = df_timestamp.item()

    if multiple_timestamps:
        df_start_times = []
        for i in range(len(df_timestamp_list)):
            timestamp = df_timestamp_list[i]
            loc = df_timestamp_loc_list[i]
            if not timestamp.startswith('gps time: '):
                raise ValueError(f"In {os.path.basename(auditfile)}- was expecting timestamp comment to start with 'gps time: '")
            else:
                timestamp = dt.datetime.fromisoformat(timestamp[len('gps time: '):])
                df_start_times.append(timestamp - dt.timedelta(seconds = loc))

                st1 = df_start_times[0]
                st_rest = df_start_times[1:]
                avg_sec = st1
                for time in st_rest:
                    avg_sec += dt.timedelta(seconds = (st1 - time).total_seconds()/len(df_start_times))
                df_start_time = avg_sec # Average of all start-times guessed from the multiple time-stamps available in the audit.
    else:
        if not df_timestamp.startswith('gps time: '):
            raise ValueError("Was expecting timestamp comment to start with 'gps time: '")
        else:
            df_timestamp = dt.datetime.fromisoformat(df_timestamp[len('gps time: '):])
        df_timestamp_loc = df_relevant.loc[df_relevant['Behavior'] == 'time']['Start (s)'].item()

        df_start_time = df_timestamp - dt.timedelta(seconds = df_timestamp_loc)

    starts_and_stops = list(zip(list(df_relevant['Start (s)']), list(df_relevant['Stop (s)']))) #Start and stop times in seconds, in a list of tuples
    behaviours = list(df_relevant['Behavior'])
    times_and_labels = []
    proc_time = df_start_time + dt.timedelta(seconds = starts_and_stops[0][0])
    proc_time = proc_time - dt.timedelta(microseconds = proc_time.microsecond)  #First second before data available
    proc_state = behaviours[0]

    first_iter = True
    bout_count = 0
    df_stop_time = df_start_time + dt.timedelta(seconds = starts_and_stops[-1][1])

    while proc_time < df_stop_time and bout_count < len(behaviours):
        bout_count_correction = 0
        if first_iter:
            first_iter = False
            if (starts_and_stops[0][0] % 1)/config.EPOCH > 1 - config.EPOCH_OVERHANG_TOLERANCE:
                proc_time += dt.timedelta(seconds = config.EPOCH)
                continue
            else:
                pass

        proc_state = behaviours[bout_count]
        if proc_state not in config.STATES:
            if config.IGNORE_EVENTS_IN_AUDITS:
                bout_count += 1
                continue
            else: #THIS THING IS NOT WORKING #FIXME
                bout_count_correction += 1

        while (df_start_time + dt.timedelta(seconds = starts_and_stops[bout_count][1]) - proc_time).total_seconds() >= config.EPOCH:
            times_and_labels.append([proc_time, proc_state])
            proc_time += dt.timedelta(seconds = config.EPOCH)

        if ((df_start_time + dt.timedelta(seconds = starts_and_stops[bout_count][1]) - proc_time)/config.EPOCH).total_seconds() > 1 - config.EPOCH_OVERHANG_TOLERANCE:
            times_and_labels.append([proc_time, proc_state])

        proc_time += dt.timedelta(seconds = config.EPOCH)
        bout_count += bout_count_correction + 1

    return pd.DataFrame(times_and_labels, columns=("time", "state"))

def read_all_audits():

    tsvfiles = glob.glob(f"{config.DATA_DIR}audits/*.tsv")

    list_of_audits = []
    for tsvf in tsvfiles:
        list_of_audits.append(read_audit(tsvf))

    return list_of_audits
if __name__ == "__main__":
    pass
