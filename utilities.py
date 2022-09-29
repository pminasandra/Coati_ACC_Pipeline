# Pranav Minasandra
# pminasandra.github.io
# Sep 27, 2022

import os

import matplotlib.pyplot as plt

import config

# IMAGE SAVING
formats = ['pdf', 'png', 'svg']
def saveimg(img_obj, name, formats=formats):
    Dirs = [f"{config.FIGURES_DIR}{form}" for form in formats]
    for Dir in Dirs:
        os.makedirs(Dir, exist_ok=True)
    for form in formats:
        img_obj.savefig(f"{config.FIGURES_DIR}{form}/{name}.{form}")

# ACC VISUALISATION
def acc_visualise(acc_reads, start_time, stop_time):
    """
    Plots raw ACC data between start_time and stop_time
    Args:
        acc_reads (pd.DataFrame): typically, output from accreading.read_acc_file(...)
        start_time (datetime.datetime)
        stop_time (datetime.datetime)
    """

    assert acc_reads['datetime'].min() <= start_time
    assert acc_reads['datetime'].max() >= stop_time

    acc_relevant = acc_reads[(acc_reads['datetime'] > start_time) & (acc_reads['datetime'] < stop_time)]

    fig, axs = plt.subplots(3,1, sharex=True, sharey=False)
    axs[0].plot(acc_relevant['datetime'], acc_relevant['x'])
    axs[1].plot(acc_relevant['datetime'], acc_relevant['y'])
    axs[2].plot(acc_relevant['datetime'], acc_relevant['z'])

    axs[0].set_title('x')
    axs[1].set_title('y')
    axs[2].set_title('z')

    axs[2].set_xlabel('Time')

    return fig, axs
