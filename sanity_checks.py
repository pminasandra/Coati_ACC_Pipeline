# Pranav Minasandra
# pminasandra.github.io
# September 27, 2022

import datetime as dt
import os.path

import matplotlib.pyplot as plt
import pandas as pd

import accreading
import auditreading
import calibration
import config
import utilities


print(f"{os.path.basename(__file__)}: initiated")
all_audits = auditreading.read_all_audits()
acc_file = f'{config.DATA_DIR}acc/tag9478_acc.txt'
df = accreading.read_acc_file(acc_file)
assert calibration.calibration_file_exists(acc_file)
df = calibration.calibrate_data(df, calibration.calibration_file(acc_file))

audit_count = 1
for df_audit in all_audits:
    print(f"{os.path.basename(__file__)}: sanity check, plotting audit {audit_count}")
    st = list(df_audit['state'])
    st = [config.REDUCED_STATE[state] for state in st]
    df_audit['state'] = pd.Series(st)
    df_audit.sort_values(by='datetime', inplace=True, ignore_index=True)
    start_time = df_audit['datetime'].min() - dt.timedelta(seconds=20)
    stop_time = df_audit['datetime'].max() + dt.timedelta(seconds=20)


    fig, axs = utilities.acc_visualise(df, start_time, stop_time)

    df_audits = df_audit.groupby('state')
    for state, vals in df_audits: 
        axs[0].scatter(x=vals['datetime'], y=[2]*len(vals['datetime']), label=state, s=0.9)

    axs[0].legend()
    utilities.saveimg(fig, f"audit{audit_count}")
    audit_count += 1
    plt.close(fig)
