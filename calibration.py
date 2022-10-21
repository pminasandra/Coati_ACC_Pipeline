# Pranav Minasandra
# pminasandra.github.io
# October 17, 2022

import datetime as dt
import glob
import os
import os.path
import random
import shelve

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as mp3d
import numpy as np
import scipy.optimize

import accreading
import config
import utilities

FRACTION_OF_THETA_FOR_CUTOFF = 0.8

def get_spherical_calibration_data(acc_df, init_guess="auto"):
    """
    Calibrates acc_data to roughly accelerometer outputs, fitting a sphere to the data.
    Args:
        acc_df (pd.DataFrame): typically output from accreading.read_acc_file(...)
        init_guess (list-like, with 4 floats): list with x0, y0, z0, and r0 values. Set to "auto" to use medians as guesses.
    Returns:
        Sphere, in terms of ([x0, y0, z0], r)
    """

    acc_df2 = acc_df.copy()
    acc_df2['x'] = acc_df2['x'] - 2048.0
    acc_df2['y'] = acc_df2['y'] - 2048.0
    acc_df2['z'] = acc_df2['z'] - 2048.0

    if config.DELETE_G_FROM_SPHERICAL_THETA:
        phi = np.arctan2((acc_df2['x']**2 + acc_df2['y']**2)**0.5, acc_df2['z'])
        acc_df2 = acc_df2[phi < FRACTION_OF_THETA_FOR_CUTOFF*np.pi]

    if init_guess == "auto":
        init_guess = np.array([acc_df2['x'].median(),
                                acc_df2['y'].median(),
                                acc_df2['z'].median(),
                                1000.0
                                ])
    def optim_func_compute_r(array_of_guesses):

        x = array_of_guesses[0]
        y = array_of_guesses[1]
        z = array_of_guesses[2]
        r = array_of_guesses[3]

        x2 = (acc_df2['x'] - x)**2
        y2 = (acc_df2['y'] - y)**2
        z2 = (acc_df2['z'] - z)**2

        r_err = (x2+y2+z2)

        return (r_err - r**2).sum()

    optimization = scipy.optimize.least_squares(optim_func_compute_r, init_guess)
    if not config.TWO_ROUND_FIT:
        return optimization['x'][:-1], optimization['x'][-1]

    r = optimization['x'][2]

    def optim_func_without_r(array_of_guesses):

        x = array_of_guesses[0]
        y = array_of_guesses[1]
        z = array_of_guesses[2]

        x2 = (acc_df2['x'] - x)**2
        y2 = (acc_df2['y'] - y)**2
        z2 = (acc_df2['z'] - z)**2

        r_err = (x2+y2+z2)

        return ((r_err - r**2)**2).sum()

    if type(init_guess) == str and init_guess == "auto":
        init_guess = np.array([acc_df2['x'].median(),
                                acc_df2['y'].median(),
                                acc_df2['z'].median()
                                ])
    else:
        init_guess = init_guess[:-1]

    optimization = scipy.optimize.least_squares(optim_func_without_r, init_guess)
    return optimization['x'], r


def calibrate_all_files(generate_images=False):
    """
    Calibrates all files, stores calibration data in config.DATA_DIR/calibration as shelve files
    Args:
        generate_images (bool): Whether the function must also generate 3D scatterplots with the calibration
        sphere superimposed.
    """

    # FIXME: Right now, only ACCN data is used for calibration.
    # We might want to use ACC data in the future.

    list_of_files = glob.glob(f"{config.DATA_DIR}acc/tag*_acc.txt")
    for File in list_of_files:
        print(f"{os.path.basename(__file__)}: calibrate_all_files(): working on {File}")
        df = accreading.read_acc_file(File)
        df = df[df['acc_type'] == "ACCN"]
        [x0,y0,z0], r = get_spherical_calibration_data(df, [0,0,0,1000])

        if generate_images:
            fig = plt.figure()
            ax = fig.add_subplot(projection = '3d')

            u, v = np.mgrid[0:2*np.pi:30j, 0:np.pi:20j]
            x = x0 + r*(np.cos(u) * np.sin(v))
            y = y0 + r*(np.sin(u) * np.sin(v))
            z = z0 + r*np.cos(v)

            ax.plot_wireframe(x,y,z, colors="#AA000022")
            df['x'] -= 2048.0
            df['y'] -= 2048.0
            df['z'] -= 2048.0
            phi = np.arctan2((df['x']**2 + df['y']**2)**0.5, df['z'])
            df = df[phi < FRACTION_OF_THETA_FOR_CUTOFF*np.pi]
            ax.scatter(df['x'][::50], df['y'][::50], df['z'][::50], s=0.1, c=phi[phi<FRACTION_OF_THETA_FOR_CUTOFF*np.pi][::50])
            ax.scatter(x0,y0,z0,s=2,c='red')

            utilities.saveimg(fig, os.path.basename(File)[:-len('.txt')])
            plt.close(fig)

        with shelve.open(f"{config.DATA_DIR}calibration/{os.path.basename(File)[:-len('.txt')]}.calibration") as calib_data:
            calib_data['x0'] = x0
            calib_data['y0'] = y0
            calib_data['z0'] = z0
            calib_data['r'] = r

def calibrate_data(acc_df, calibration_file):
    df = acc_df.copy()
    df['x'] -= 2048.0
    df['y'] -= 2048.0
    df['z'] -= 2048.0

    Shelf = shelve.open(calibration_file)
    df['x'] -= Shelf['x0']
    df['y'] -= Shelf['y0']
    df['z'] -= Shelf['z0']

    df['x'] /= Shelf['r']
    df['y'] /= Shelf['r']
    df['z'] /= Shelf['r']

    Shelf.close()
    return df

def calibration_file(acc_file):
    cfname =os.path.basename(acc_file)[:-len('.txt')]+".calibration"
    return config.DATA_DIR + "calibration/" + cfname

def calibration_file_exists(acc_file):
    return os.path.exists(calibration_file(acc_file))

if __name__ == "__main__":
    calibrate_all_files()

