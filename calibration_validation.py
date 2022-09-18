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

def fourier_plots():
    """
    Chooses 5 random acc files from config.DATA_DIR/acc/, and plots frequency domain maps for all 3 axes.
    """
    list_of_files = glob.glob(f"{config.DATA_DIR}acc/tag*.txt")
    list_of_files = random.sample(list_of_files, k=5)

    fig = plt.figure(figsize=(25, 15), layout='tight')
    axs = fig.subplots(3, 5)

    count = 0
    for File in list_of_files:
        print(f"Working on file {count+1} of 5: {os.path.basename(File)}")
        dataset = feature_extraction.data_from(File)
        x_fft, y_fft, z_fft = [], [], []
        data_count = 1
        for time, data in dataset:
            print(data_count, end="\033[K\r")
            xs = data[:,0]
            ys = data[:,1]
            zs = data[:,2]

            if len(xs) != 20 and len(xs) > 0:
                continue

            if len(x_fft) == 0:
                x_fft = scipy.fft.fft(xs)
                x_fft_freqs = scipy.fft.fftfreq(len(xs), 1/len(xs))[:len(xs)//2]
            else:
                x_fft *= (data_count-1)/data_count
                x_fft = 1/data_count * scipy.fft.fft(xs) + x_fft

            if len(y_fft) == 0:
                y_fft = scipy.fft.fft(ys)
                y_fft_freqs = scipy.fft.fftfreq(len(ys), 1/len(ys))[:len(ys)//2]
            else:
                y_fft *= (data_count-1)/data_count
                y_fft += 1/data_count * scipy.fft.fft(ys)


            if len(z_fft) == 0:
                z_fft = scipy.fft.fft(zs)
                z_fft_freqs = scipy.fft.fftfreq(len(zs), 1/len(zs))[:len(zs)//2]
            else:
                z_fft *= (data_count-1)/data_count
                z_fft += 1/data_count * scipy.fft.fft(zs)

            data_count += 1

        axs[0, count].plot(x_fft_freqs, np.abs(2/len(xs) * x_fft[:len(xs)//2]))
        axs[1, count].plot(y_fft_freqs, np.abs(2/len(ys) * y_fft[:len(xs)//2]))
        axs[2, count].plot(z_fft_freqs, np.abs(2/len(zs) * z_fft[:len(xs)//2]))
        count += 1
        config.saveimg(fig, "fft_avg")

    config.saveimg(fig, "fft_avg")

#scatterplots_of_acc_axes()
fourier_plots()
