# Pranav Minasandra
# pminasandra.github.io
# September 27, 2022

import datetime as dt

import matplotlib.pyplot as plt
import pandas as pd

import accreading
import auditreading
import config
import utilities

acc_file = f'{config.DATA_DIR}acc/tag9478_acc.txt'
audit_file = f'{config.DATA_DIR}audits/GX013524.tsv'

start_time = dt.datetime.fromisoformat('2021-12-12 14:21:00')
stop_time = dt.datetime.fromisoformat('2021-12-12 14:24:00')

df = accreading.read_acc_file(acc_file)
df_audit = auditreading.read_audit(audit_file)
df_audit.sort_values(by='datetime', inplace=True, ignore_index=True)

fig, axs = utilities.acc_visualise(df, start_time, stop_time)

df_audit = df_audit[(df_audit['datetime'] >= start_time) & (df_audit['datetime'] <= stop_time)]
df_audit['datetime'] = df_audit['datetime'] + dt.timedelta(seconds=19)
df_audits = df_audit.groupby('state')
for state, vals in df_audits: 
    axs[0].scatter(x=vals['datetime'], y=[3000]*len(vals['datetime']), label=state)

axs[0].legend()
plt.show()
