
from os.path import join
import os.path
import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture as GMM

import config

for f in glob.glob(join(config.DATA_DIR, "features/*.csv")):
    fname = os.path.basename(f)
    df = pd.read_csv(f, header=0)
    df_out = df.copy()

    vedba_vals = np.array(df_out["vedba"])
    vedba_vals = vedba_vals.reshape(-1, 1)
    vedba_vals = np.log(vedba_vals)


    gmm = GMM(n_components=2)

    df_out["state"] = "UNKNOWN"
    gmm.fit(vedba_vals)
    print(fname, "Means:", gmm.means_, "\nCovariances:", gmm.covariances_, "\nWeights: ", gmm.weights_, "\n\n")
    vedba_states = gmm.predict(vedba_vals)

    statenames = {}
    if gmm.means_[0] > gmm.means_[1]:
        statenames[0] = "High"
        statenames[1] = "Low"
    else:
        statenames[0] = "Low"
        statenames[1] = "High"

    df_out.loc[vedba_states == 0, "state"] = statenames[0]
    df_out.loc[vedba_states == 1, "state"] = statenames[1]

    df_out = df_out[["datetime", "state"]]
    df_out.to_csv(join(config.DATA_DIR, "VeDBA_States", fname), index=False)

