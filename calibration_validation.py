# Pranav Minasandra
# pminasandra.github.io
# Sep 15, 2022

import glob
import os
import os.path
import random
seed = 1234
random.seed(seed)

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import accreading
import config

def scatterplots_of_acc_axes():
    """
    Chooses 5 random acc files from config.DATA_DIR/acc/, and plots 3D scatterplots of their 'x', 'y', and 'z' values.
    """
    list_of_files = glob.glob(f"{config.DATA_DIR}acc/tag*.txt")
    list_of_files = random.sample(list_of_files, k=5)

    fig = plt.figure(figsize=(25, 5), layout='tight')
    axs = fig.subplots(1, 5, subplot_kw={'projection':'3d'})

    count = 0
    for File in list_of_files:
        print(f"Working on file {count+1} of 5: {os.path.basename(File)}")
        df = accreading.read_acc_file(File)
        axs[count].scatter(df['x'][::100], df['y'][::100], df['z'][::100], s=0.05)
        axs[count].set_title(f"{os.path.basename(File)[:-4]}")
        count += 1

    config.saveimg(fig, "acc_3d_scatterplot")

scatterplots_of_acc_axes()
