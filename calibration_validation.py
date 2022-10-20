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
import numpy as np
import scipy.fft

import accreading
import config
import feature_extraction
import utilities

def scatterplots_of_acc_axes(use_only_high_sampling = True):
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
        if use_only_high_sampling:
            df = df[df['acc_type'] == "ACCN"]
        axs[count].scatter(df['x'][::100], df['y'][::100], df['z'][::100], s=0.05)
        axs[count].set_title(f"{os.path.basename(File)[:-4]}")
        count += 1

    utilities.saveimg(fig, "acc_3d_scatterplot")

    count = 0
    if use_only_high_sampling:
        plt.close(fig)
        fig = plt.figure(figsize=(25, 5), layout='tight')
        axs = fig.subplots(1, 5, subplot_kw={'projection':'3d'})
        for File in list_of_files:
            print(f"Working on file {count+1} of 5: {os.path.basename(File)}")
            df = accreading.read_acc_file(File)
            if use_only_high_sampling:
                df = df[df['acc_type'] == "ACC"]
            axs[count].scatter(df['x'][::100], df['y'][::100], df['z'][::100], s=0.05)
            axs[count].set_title(f"{os.path.basename(File)[:-4]}")
            count += 1
    utilities.saveimg(fig, "lowres_acc_3d_scatterplot")

def fourier_plots():
    """
    Chooses 5 random acc files from config.DATA_DIR/acc/, and plots frequency domain maps for all 3 axes.
    """
    list_of_files = glob.glob(f"{config.DATA_DIR}acc/tag*.txt")
    list_of_files = [random.sample(list_of_files, k=5)[0]]

    fig = plt.figure(figsize=(25, 15), layout='tight')
    axs = fig.subplots(3, 1)

    count = 0
    for File in list_of_files:
        print(f"Working on file {count+1} of 5: {os.path.basename(File)}")
        dataset = feature_extraction.data_from(File)
        data_count = 1
        for time, data in dataset:
            fig = plt.figure(figsize=(25, 15), layout='tight')
            axs = fig.subplots(3, 1)
            print(data_count, end="\033[K\r")
            xs = data[:,0]
            ys = data[:,1]
            zs = data[:,2]

            x_fft = np.fft.fft(xs)[1:11]
            y_fft = np.fft.fft(ys)[1:11]
            z_fft = np.fft.fft(zs)[1:11]

            axs[0].plot(np.abs(x_fft))
            axs[1].plot(np.abs(y_fft))
            axs[2].plot(np.abs(z_fft))

            data_count += 1
            plt.show()

            axs[0].cla()
            axs[1].cla()
            axs[2].cla()

        count += 1
        utilities.saveimg(fig, "fft_avg")

    utilities.saveimg(fig, "fft_avg")

scatterplots_of_acc_axes()
#fourier_plots()
