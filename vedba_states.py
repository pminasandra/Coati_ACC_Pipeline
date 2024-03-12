
from os.path import join
import os.path
import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.mixture import GaussianMixture as GMM

import config
import utilities

for f in glob.glob(join(config.DATA_DIR, "trago/features/*.csv")):
    fname = os.path.basename(f)
    df = pd.read_csv(f, header=0)
    df_out = df.copy()

    vedba_vals = np.array(df_out["vedba"])
    vedba_vals = vedba_vals.reshape(-1, 1)
    vedba_vals = np.log(vedba_vals)


    gmm = GMM(n_components=2, covariance_type="full")

    df_out["state"] = "UNKNOWN"
    gmm.fit(vedba_vals)
    print(fname, "Means:", gmm.means_, "\nCovariances:", gmm.covariances_, "\nWeights: ", gmm.weights_, "\n\n")
    vedba_states = gmm.predict(vedba_vals)

    fig, ax = plt.subplots()
    ax.hist(vedba_vals, 100, density=True)
    xrange_low, xrange_high = ax.get_xlim()
    xrange = np.linspace(xrange_low, xrange_high, 200)
    mean1= gmm.means_[0][0]
    mean2= gmm.means_[1][0]

    var1 = gmm.covariances_[0][0]
    var2 = gmm.covariances_[1][0]

    w1 = gmm.weights_[0]
    w2 = gmm.weights_[1]

    ax.plot(xrange, w1*norm.pdf(xrange, loc=mean1, scale=var1), color='black', linewidth=0.5)
    ax.plot(xrange, w2*norm.pdf(xrange, loc=mean2, scale=var2), color='red', linewidth=0.5)

    ax.set_xlabel('log VeDBA')
    ax.set_ylabel('frequency')

    utilities.saveimg(fig, "vedba_hist_" + fname[:-len(".csv")])

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

