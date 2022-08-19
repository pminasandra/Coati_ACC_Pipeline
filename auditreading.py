# Pranav Minasandra
# pminasandra@ab.mpg.de
# August 19, 2022

import datetime as dt
import logging
import os.path

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

    if len(df_timestamp) > 1:
        # TODO: Handle multiple time-stamps
        raise ValueError("Multiple timestamps encountered. Handling this has not yet been implemented.")

    else:
        df_timestamp = df_timestamp.item()

    if not df_timestamp.startswith('gps time: '):
        raise ValueError("Was expecting timestamp comment to start with 'gps time: '")
    else:
        df_timestamp = dt.datetime.fromisoformat(df_timestamp[len('gps time: '):])
    df_timestamp_loc = df_relevant.loc[df_relevant['Behavior'] == 'time']['Start (s)'].item()

    print(f"This means that the video started at {df_timestamp - dt.timedelta(seconds=df_timestamp_loc)}")
    df_start_time = df.timestamp - dt.timedelta(seconds = df_timestamp_loc)

    times_and_labels = []

    # TODO: Write out this part neatly, for every 'floor-operated' EPOCH, a label should be assigned while taking care of OVERHANG_TOLERANCE.

read_audit(config.DATA_DIR + "trial1.tsv")
