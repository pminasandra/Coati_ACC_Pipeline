
from os.path import join
import os.path
import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config

for f in glob.glob(join(config.DATA_DIR, "features/*.csv")):
    fname = os.path.basename(f)
    df = pd.read_csv(f, header=0)
    df_out = df.copy()

    df_out["state"] = "UNKNOWN"
    df_out.loc[np.log(df["vedba"]) > -3, "state"] = "High"
    df_out.loc[np.log(df["vedba"]) <= -3, "state"] = "Low"

    df_out = df_out[["datetime", "state"]]
    df_out.to_csv(join(config.DATA_DIR, "VeDBA_States", fname), index=False)

