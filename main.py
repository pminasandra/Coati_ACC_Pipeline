# Pranav Minasandra
# pminasandra.github.io
# September 06, 2022

import glob
import multiprocessing as mp
import os
import os.path

import accreading
import auditreading
import config

# First read all available audit data
tsvfiles = glob.glob(f"{config.DATA_DIR}audits/*.tsv")

manager = mp.Manager()
mdict = manager.dict()

def parallel_read(filename):
    print(f"{os.path.basename(__file__)}: Handingling audit data for {filename}")
    global mlist
    mdict[filename] = auditreading.read_audit(filename)

with mp.Pool(16) as pool:
    pool.map(parallel_read, tsvfiles)
pool.close()

set_list = []
for name, df in mdict.items():
    set_list.extend(df['state'].unique())

print(set(set_list))
# Then extract all features for all feature-space
# Train the classifiers
# Perform analyses
