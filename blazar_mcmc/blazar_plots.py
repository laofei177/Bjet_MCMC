#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
file name: blazar_plots.py
Program purpose: Code for various plots

Parameters are always listed in the following order:
[delta, K, n1, n2, gamma_min, gamma_max, gamma_break, B, R]
All parameters are the logarithm of the true value except for delta, n1, and n2
---------------------------------------------------
delta       doppler factor                  linear
K           particle density [cm^-3]        log
n1          alpha_1 (first index)           linear
n2          alpha_2 (second index)          linear
gamma_min   low-energy cutoff               log
gamma_max   high-energy cutoff              log
gamma_break energy break                    log
B           magnetic field strength [G]     log
R           blob radius (cm)                log
---------------------------------------------------

Note that data (observed) is expected in linear scale and model data is expected in log scale unless log param is set to False.

"""
import glob
import os
import pickle
import random

import corner
import numpy as np
import tqdm
from matplotlib import pyplot as plt
from scipy import interpolate

import blazar_model
from blazar_properties import *

image_type = 'svg'


# plots of SED ---------------------------------------------------------------------------------------------------------
def plot_model(model, title=None, no_title=False, line=True, points=True, point_style='.', line_style='-',
               line_alpha=1.0, file_name=RESULTS_FOLDER + "/model." + image_type, clear_plot=True, save=False,
               show=True, log=True):
    """
    Plots frequency against energy flux using matplotlib
    Args:
        results: an index-able type with at least two elements
            The first two elements are 1D numpy arrays of floats. Only the first
            2 elements are used. results[0] should be logv values and results[1]
            logvFv values.
        save (optional): bool
            Whether model should be saved as image; default is False
        show (optional): bool
            Specifies if plot is shown; default is true
        file_name (optional):str
            Where model should be saved; default is "<RESULTS_FOLDER>/model.<image_type>"
        line (optional): bool
            Specifies if the line between points should be shown; default is True
        points (optional): bool
            Specifies if the points should be shown (or just the line); default is True
        point_style (optional): str that is a valid matplotlib point style
            Specifies the point style; default is '.'
        line_style (optional): str that is a valid matplotlib line style
            Specifies the line style; default is '-'
        clear_plot (optional): bool
            Whether the plot should be cleared before new data is plotted; default
            is True

    After function call:
        If show is true, the plot is shown.
        If save is true, the plot is saved as file.
    """
    if log:
        x = np.power(10, model[0])
        y = np.power(10, model[1])
    else:
        x = model[0]
        y = model[1]

    if clear_plot:
        plt.figure("SED Plot")
    plt.xlabel(r"$\nu$")
    plt.ylabel(r"$\nu F_{\nu}$")
    if title is None and not no_title:
        title = "SED frequency/energy flux plot"
    if title is not None:
        plt.title(title)
    if points:
        plt.plot(x, y, point_style)
    if line:
        plt.plot(x, y, line_style, alpha=line_alpha)
    if save:
        plt.savefig(file_name)
    if show:
        plt.show()


def plot_model_and_data(model, v_data, vFv_data, err_data, title=None, no_title=False, adjust_scale=True, line=True,
                        points=True, point_style='.', line_style='-', lower_adjust_multiplier=None,
                        upper_adjust_multiplier=None, file_name=RESULTS_FOLDER + "/model_and_data." + image_type,
                        clear_plot=True, save=False, show=True, log=True):
    """
    Create a plot with data and model data
    Args:
        model: tuple of 1D np arrays of floats
            The data for the model; only the first 2 elems are used, which are
            logv and logvFv
        v_data: 1D np array of floats
            Data
        vFv_data: 1D np array of floats
            Data
        title: str
            Title for plot
        file_name (optional): str
            Relative path to where the image should be saved; default is
            "<RESULTS_FOLDER>/model_and_data.<image_type>"
        save (optional): bool
            If the plot should be saved; default is False
        show (optional): bool
            Specifies if plot is shown; default is True
        adjust_scale (optional): bool
            True = the plot should use the scale of the data
            False = scaled to the model
            default is True
        lower_adjust_multiplier (optional): float
            How far below the data the plot should be scaled; default is 1.1
        upper_adjust_multiplier (optional): float
            How far above the data the plot should be scaled; default is 1.1
        clear_plot (optional): bool
            Whether the plot should be cleared before new data is plotted; default
            is True

    After function call:
        If show is true, the plot is shown.
        If save is true, the plot is saved as file.
    """

    if clear_plot:
        plt.figure("Model and Data")
    plot_data(v_data, vFv_data, err_data, title=title, no_title=no_title, adjust_scale=adjust_scale,
              lower_adjust_multiplier=lower_adjust_multiplier, upper_adjust_multiplier=upper_adjust_multiplier,
              clear_plot=False, save=False, show=False)
    plt.xscale('log')
    plt.yscale('log')
    if log:
        x = np.power(10, model[0])
        y = np.power(10, model[1])
    else:
        x = model[0]
        y = model[1]
    if points:
        plt.plot(x, y, point_style)
    if line:
        plt.plot(x, y, line_style)

    if save:
        plt.savefig(BASE_PATH + file_name)
    if show:
        plt.show()


def plot_data(v_data, vFv_data, err_data, title=None, no_title=False, adjust_scale=True, lower_adjust_multiplier=None,
              upper_adjust_multiplier=None, file_name=RESULTS_FOLDER + "/data." + image_type, clear_plot=True,
              save=False, show=True):
    """
    Create a plot of the data
    Args:
        v_data: 1D np array of floats
            Data
        vFv_data: 1D np array of floats
            Data
        title: str
            Title for plot
        file_name (optional): str
            Relative path to where the image should be saved; default is
            "<RESULTS_FOLDER>>/data.<image_type>"
        save (optional): bool
            If the plot should be saved; default is False
        show (optional): bool
            Specifies if plot is shown; default is True
        adjust_scale (optional): bool
            True = the plot should use the scale of the data
            False = scaled to the model
            default is True
        lower_adjust_multiplier (optional): float
            How far below the data the plot should be scaled; default is 1.1
        upper_adjust_multiplier (optional): float
            How far above the data the plot should be scaled; default is 1.1
        clear_plot (optional): bool
            Whether the plot should be cleared before new data is plotted; default
            is True

    After function call:
        If show is true, the plot is shown.
        If save is true, the plot is saved as file.
    """
    if clear_plot:
        plt.figure("Plot of data")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel(r"$\nu$")
    plt.ylabel(r"$\nu F_{\nu}$")
    if title is None and not no_title:
        title = "Data"
    if title is not None:
        plt.title(title)
    plt.plot(v_data, vFv_data, '.')

    if adjust_scale:
        new_min, new_max = scale_to_values(vFv_data, lower_adjust_multiplier=lower_adjust_multiplier,
                                           upper_adjust_multiplier=upper_adjust_multiplier)
        plt.ylim(new_min, new_max)

    plt.errorbar(v_data, vFv_data, yerr=(err_data), fmt='.', color='b', ecolor='k',
                 label="Data")

    if save:
        plt.savefig(BASE_PATH + file_name)
    if show:
        plt.show()


# MCMC Plots -----------------------------------------------------------------------------------------------------------
def corner_plot(values, param_min_vals, param_max_vals, best_params, sigma_below_params, sigma_above_params, title=None,
                no_title=False, param_names=None, file_name=RESULTS_FOLDER + "/corner." + image_type, save=False,
                show=True, dpi=300, eic=False):
    """
    Create a corner plot:
    Args:
        values: 2D np array of arrays w/ NUM_DIM columns
            Flat samples--a list of sets of parameters
        param_min_vals: list or np array of NUM_DIM floats
            Minimum value for each param
        param_max_vals: list or np array of NUM_DIM floats
            Maximum value for each param
        best_params: list or np array of NUM_DIM floats
            Parameter values for the model with the best chi squared value
        sigma_below_params: list or np array of NUM_DIM floats
            Value for cutoff of lowest param value within 1 sigma for each param
        sigma_above_params: list or np array of NUM_DIM floats
            Value for cutoff of highest param value within 1 sigma for each param
        param_names (optional): list of strings
            Names of the parameters (param_names for the plot). These should be
            formatted params for math text. Default is None; then they will be
            set to FORMATTED_PARAM_NAMES.
        save (optional): bool
            If the plot should be saved; default is False
        show (optional): bool
            Specifies if plot is shown; default is True
        file_name (optional): str
            Relative path to where the image should be saved; default is
            "corner.<image_type>"
    After function call:
        mpl plot is shown, if save is true, plot is saved to a file
    """
    if param_names is None:
        param_names = modelProperties(eic).FORMATTED_PARAM_NAMES

    min_maxes = []
    for i in range(modelProperties(eic).NUM_DIM):
        min_maxes.append([param_min_vals[i], param_max_vals[i]])
    fig = corner.corner(values, labels=param_names,
                        range=min_maxes, use_math_text=True, plot_datapoints=False,
                        fill_contours=True, label_kwargs={"fontsize": 15},labelpad=0.28,max_n_ticks=4)
    # fig.set_size_inches(10, 10)
    # if title is None and not no_title:
    #     title = "MCMC Corner Plot"
    # if title is not None:
    #     plt.title(title)
    fig.subplots_adjust(top=.97,bottom=.08,left=.07,right=0.88)

    # extract axes
    dims = modelProperties(eic).NUM_DIM
    axes = np.array(fig.axes).reshape((dims, dims))
    # loop over the diagonal, add lines on histogram
    for i in range(dims):
        ax = axes[i, i]
        ax.tick_params(axis='both', labelsize=15)
        ax.axvline(best_params[i], color='r')
        ax.axvline(sigma_below_params[i], color='b', ls='--')
        ax.axvline(sigma_above_params[i], color='b', ls='--')
        best = "{:.3f}".format(best_params[i])
        below = "{:.3f}".format(sigma_below_params[i] - best_params[i])
        above = "{:.3f}".format(sigma_above_params[i] - best_params[i])
        text = param_names[i] + r" = $" + best + "^{" + above + "}_{" + below + "}$"
        ax.set_title(text, loc='left', fontsize=15)

    # add crossing lines for best point
    for i in range(1, dims):
        for j in range(i):
            ax = axes[i, j]
            ax.tick_params(axis='both', labelsize=15)
            ax.axhline(best_params[i], color='red', ls='dotted')
            ax.axvline(best_params[j], color='red', ls='dotted')
            ax.plot(best_params[j], best_params[i], '.', color='red', markersize=2)
    if not eic:
        fig.set_size_inches(11, 10)
    else:
        fig.set_size_inches(10, 12)
    if save:
        plt.savefig(BASE_PATH + file_name, dpi=dpi)
    if show:
        plt.show()
    return fig


def plot_chain(chain, param_names=None, file_name="chain." + image_type, save=False, show=True, eic=False):
    if param_names is None:
        param_names = modelProperties(eic).FORMATTED_PARAM_NAMES
    fig, axes = plt.subplots(modelProperties(eic).NUM_DIM, sharex="all")
    for i in range(modelProperties(eic).NUM_DIM):
        ax = axes[i]
        ax.plot(chain[:, :, i], "k", alpha=0.3)
        ax.set_xlim(0, len(chain))
        ax.set_ylabel(param_names[i])
    if save:
        plt.savefig(BASE_PATH + file_name)
    if show:
        plt.show()


def plot_chi_squared(values, discard_number, use_log_probs=True, plot_type='avg', title=None, no_title=False, fmt='',
                     file_name="avg_chi_squared_plot." + image_type, save=False, show=True, clear_plot=True):
    if plot_type not in ['avg', 'best', 'all']:
        raise ValueError(plot_type + " is not a valid plot type")

    if clear_plot:
        plt.figure("Plot of chi^2")
    if use_log_probs:
        chi_sq = -2. * values
    else:
        chi_sq = 1. * values

    if plot_type == 'avg':
        chi_sq = np.mean(chi_sq, axis=1)
        if title is None and not no_title:
            title = r"Average $\chi^2$ by Step"
    elif plot_type == 'best':
        chi_sq = np.min(chi_sq, axis=1)
        if title is None and not no_title:
            title = r"Best $\chi^2$ by Step"
    else:
        if title is None and not no_title:
            title = r"$\chi^2$ by Step"
    if title is not None:
        plt.title(title)
    if plot_type == 'all':
        plt.plot(np.arange(discard_number, discard_number + len(chi_sq)), chi_sq[:, :], fmt, alpha=0.3)
    else:
        plt.plot(np.arange(discard_number, discard_number + len(chi_sq)), chi_sq[:], fmt, alpha=0.3)
    plt.xlim(discard_number, discard_number + len(chi_sq))

    plt.xlabel("step")
    plt.ylabel(r"$\chi^2$")

    if save:
        plt.savefig(FOLDER_PATH + file_name)
    if show:
        plt.show()


def plot_1sigma(v_data, vFv_data, err_data, indices_within_1sigma, flat_samples, min_chi_squared_index, both=False,
                extreme=True, title=None, no_title=False, folder=None, file=None, save=False, show=True,
                serialize=False, lower_adjust_multiplier=None, upper_adjust_multiplier=1.02,
                max_num_lines_to_graph=1000, dims=None, eic=False, theta=None, redshift=None, min_freq=None,
                max_freq=None, executable=None, data_folder=None, name_stem=None, command_params_full=None,
                command_params_1=None, command_params_2=None, torus_temp=None, torus_luminosity=None, torus_frac=None,
                verbose=False):
    """
    TODO what happens when folder is None??
    The parameters within 1 sigma that have the biggest and smallest values for
    each parameter are found, resulting in 2 arrays of dimension NUM_DIM * NUM_DIM.
    Models are created from these, and for each frequency value,
    the minimum and the maximum are found.
    The graph is made by filling in the space between the minimum and maximum
    for each frequency value.
    The best model and the actual data with error bars are plotted on top of this.
    """
    if both:
        descriptor = ""
    elif extreme:
        descriptor = " extreme"
    else:
        descriptor = " random"

    if title is None and not no_title:
        title = "MCMC results with the range from" + descriptor + " models within 1 sigma"

    fig = plt.figure(title)
    ax = fig.add_subplot()

    if name_stem is None:
        delete_after = True
        name_stem = "for_plotting" + str(random.getrandbits(20))
    else:
        delete_after = False
    best_model = blazar_model.make_model(flat_samples[min_chi_squared_index], name_stem, theta=theta, redshift=redshift,
                                         min_freq=min_freq, max_freq=max_freq, torus_temp=torus_temp,
                                         torus_luminosity=torus_luminosity, torus_frac=torus_frac,
                                         data_folder=data_folder, executable=executable,
                                         command_params_full=command_params_full, command_params_1=command_params_1,
                                         command_params_2=command_params_2, prev_files=False, use_param_file=False,
                                         verbose=verbose, eic=eic)

    # going to get the values to fill between
    logv = best_model[0].copy()
    if dims is None:
        dims = modelProperties(eic).NUM_DIM
    to_plot = np.empty((0, dims))

    if extreme or both:
        min_per_param, max_per_param = get_params_1sigma_ranges(flat_samples, indices_within_1sigma,
                                                                eic=eic)
        to_plot = np.concatenate((np.array(min_per_param), np.array(max_per_param)))
    if not extreme or both:
        samples = np.unique(flat_samples[indices_within_1sigma], axis=0)
        num_lines_to_graph = min(len(samples), max_num_lines_to_graph)
        if num_lines_to_graph != len(samples):
            indices = np.random.choice(np.arange(0, len(samples)), size=num_lines_to_graph, replace=False)
        else:
            indices = np.arange(0, len(samples))
        to_plot = np.concatenate((to_plot, samples[indices]))  # if both, both sets will be plotted

    lowest_per_point, highest_per_point = get_min_max_per_point(logv, to_plot, name_stem=name_stem, theta=theta,
                                                                redshift=redshift, min_freq=min_freq, max_freq=max_freq,
                                                                torus_temp=torus_temp,
                                                                torus_luminosity=torus_luminosity,
                                                                torus_frac=torus_frac, data_folder=data_folder,
                                                                executable=executable,
                                                                command_params_full=command_params_full,
                                                                command_params_1=command_params_1,
                                                                command_params_2=command_params_2, verbose=False,
                                                                eic=eic)

    ax.fill_between(logv, lowest_per_point, highest_per_point, alpha=.5, label=r"Within 1 sigma")

    plt.plot(best_model[0], best_model[1], '-', color='g', linewidth=2, label="Best model")

    plt.errorbar(v_data, vFv_data, yerr=(err_data), fmt='.', color='b', ecolor='k', label="Data")

    plt.xlabel(r"log $\nu$")
    plt.ylabel(r"log $\nu F_{\nu}$")
    new_min, new_max = scale_to_values(vFv_data,
                                       lower_adjust_multiplier=lower_adjust_multiplier,
                                       upper_adjust_multiplier=upper_adjust_multiplier)
    plt.ylim(new_min, new_max)
    plt.legend(loc='best')
    if title is not None:
        plt.title(title)

    if delete_after:
        for f in glob.glob(BASE_PATH + DATA_FOLDER + "/" + name_stem + "_*"):
            os.remove(f)

    if save or serialize:
        if folder is None:
            folder = ''
        if folder[-1] != '/':
            folder = folder + '/'
        if descriptor != '' and descriptor is not None:
            file_name = BASE_PATH + folder + "plot_with_" + descriptor[1:] + "_params."
        else:
            file_name = BASE_PATH + folder + "plot_with_error."
        if save:
            if file is None:
                if descriptor != " extreme":
                    plt.savefig(file_name + "png")  # too big for svg
                else:
                    plt.savefig(file_name + image_type)
            else:
                plt.savefig(BASE_PATH + file)
        if serialize:
            with open(file_name + "pickle", 'wb') as f:
                pickle.dump(fig, f)
    if show:
        plt.show()


def plot_1sigma_plots(v_data, vFv_data, err_data, indices_within_1sigma, flat_samples, min_chi_squared_index,
                      both=False, extreme=True, title=None, no_title=False,
                      folder=None, file=None, save=False, show=True, serialize=False,
                      lower_adjust_multiplier=None, upper_adjust_multiplier=1.02, max_num_lines_to_graph=1000,
                      dims=None,
                      eic=False, return_models=False, theta=None, redshift=None, min_freq=None, max_freq=None,
                      executable=None, data_folder=None, command_params_full=None, command_params_1=None,
                      command_params_2=None, name_stem=None, torus_temp=None, torus_luminosity=None, torus_frac=None,
                      verbose=False):
    """
    TODO what happens when folder is None??
    The parameters within 1 sigma that have the biggest and smallest values for
    each parameter are found, resulting in 2 arrays of dimension NUM_DIM * NUM_DIM.
    Models are created from these, and for each frequency value,
    the minimum and the maximum are found.
    The graph is made by filling in the space between the minimum and maximum
    for each frequency value.
    The best model and the actual data with error bars are plotted on top of this.
    """
    if both:
        descriptor = ""
    elif extreme:
        descriptor = " extreme"
    else:
        descriptor = " random"

    if title is None and not no_title:
        title = "MCMC results with" + descriptor + " models within 1 sigma"

    fig = plt.figure(title)
    ax = fig.add_subplot()

    if name_stem is None:
        delete_after = True
        name_stem = "for_plotting" + str(random.getrandbits(20))
    else:
        delete_after = False
    best_model = blazar_model.make_model(flat_samples[min_chi_squared_index], name_stem, theta=theta, redshift=redshift,
                                         min_freq=min_freq, max_freq=max_freq, torus_temp=torus_temp,
                                         torus_luminosity=torus_luminosity, torus_frac=torus_frac,
                                         data_folder=data_folder, executable=executable,
                                         command_params_full=command_params_full, command_params_1=command_params_1,
                                         command_params_2=command_params_2, prev_files=False, use_param_file=False,
                                         verbose=verbose, eic=eic)

    # going to get the values to fill between
    logv = best_model[0].copy()
    if dims is None:
        dims = modelProperties(eic).NUM_DIM
    to_plot = np.empty((0, dims))

    if extreme or both:
        min_per_param, max_per_param = get_params_1sigma_ranges(flat_samples, indices_within_1sigma,
                                                                eic=eic)
        to_plot = np.concatenate((np.array(min_per_param), np.array(max_per_param)))
    if not extreme or both:
        samples = np.unique(flat_samples[indices_within_1sigma], axis=0)
        num_lines_to_graph = min(len(samples), max_num_lines_to_graph)
        if num_lines_to_graph != len(samples):
            indices = np.random.choice(np.arange(0, len(samples)), size=num_lines_to_graph, replace=False)
        else:
            indices = np.arange(0, len(samples))
        to_plot = np.concatenate((to_plot, samples[indices]))  # if both, both sets will be plotted

    name_stem = "plotting" + str(random.getrandbits(20))
    models = []
    for i in tqdm.trange(0, len(to_plot)):
        params = to_plot[i]
        model = blazar_model.make_model(params, name_stem, theta=theta, redshift=redshift, min_freq=min_freq,
                                        max_freq=max_freq, torus_temp=torus_temp, torus_luminosity=torus_luminosity,
                                        torus_frac=torus_frac, data_folder=data_folder, executable=executable,
                                        command_params_full=command_params_full, command_params_1=command_params_1,
                                        command_params_2=command_params_2, prev_files=False, use_param_file=False,
                                        verbose=verbose, eic=eic)
        models.append(model)
        plot_model(model, points=False, line_style='r-', line_alpha=.5, clear_plot=False, show=show)
        if return_models:
            models.append(model)

    plt.xscale('log')
    plt.yscale('log')
    plt.plot(np.power(10, best_model[0]), np.power(10, best_model[1]), '-', color='g', linewidth=2, label="Best model")

    plt.errorbar(v_data, vFv_data, yerr=(err_data, err_data), fmt='.', color='b', ecolor='k',
                 label="Data")

    plt.xlabel(r"$\nu$")
    plt.ylabel(r"$\nu F_{\nu}$")
    new_min, new_max = scale_to_values(vFv_data,
                                       lower_adjust_multiplier=lower_adjust_multiplier,
                                       upper_adjust_multiplier=upper_adjust_multiplier)
    plt.ylim(new_min, new_max)
    plt.legend(loc='best')
    if title is not None:
        plt.title(title)

    if delete_after:
        for f in glob.glob(BASE_PATH + DATA_FOLDER + "/" + name_stem + "_*"):
            os.remove(f)

    if folder is not None and folder[-1] != "/":
        folder = folder + "/"
    if folder is None:
        folder = ""
    if descriptor != "" and descriptor is not None:
        file_name = BASE_PATH + folder + "plot_with_lines_" + descriptor[1:] + "_params."
    else:
        file_name = BASE_PATH + folder + "plot_with_error_lines."
    if save:
        if file is None:
            if descriptor != " extreme":
                plt.savefig(file_name + "png")  # too big for svg
            else:
                plt.savefig(file_name + image_type)
        else:
            plt.savefig(BASE_PATH + file)
    if serialize:
        with open(file_name + "pickle", 'wb') as f:
            pickle.dump(fig, f)
    if show:
        plt.show()

    return models if return_models else None


# utils ----------------------------------------------------------------------------------------------------------------
def scale_to_values(values, upper_adjust_multiplier=None, lower_adjust_multiplier=None):
    if upper_adjust_multiplier is None:
        upper_adjust_multiplier = 5
    if lower_adjust_multiplier is None:
        lower_adjust_multiplier = 5
    data_min = np.min(values)
    data_max = np.max(values)
    if data_min < 0:
        new_min = lower_adjust_multiplier * data_min
    else:
        new_min = 1 / lower_adjust_multiplier * data_min
    if data_max < 0:
        new_max = 1 / upper_adjust_multiplier * data_max
    else:
        new_max = upper_adjust_multiplier * data_max
    return new_min, new_max


def get_params_1sigma_ranges(flat_samples, indices_within_1sigma, eic=False):
    """
    Finds the array of parameters that has the minimum and maximum value for
    each of the parameters.
    For example, with samples [[0, 1, 2], [5, 2, 1], [4, 6, 1], [3, 2, 0]], the
    minima would be [[0, 1, 2], [0, 1, 2], [3, 2, 0]] and the maxima would be
    [[5, 2, 1], [4, 6, 1], [0, 1, 2]]

    Arguments:
    flat_samples:
    indices_within_1sigma:

    Returns:
    """
    # set the minima and maxima to the first set of params for all vals
    dims = modelProperties(eic).NUM_DIM
    print(np.shape(indices_within_1sigma))
    print(dims)
    minima = [flat_samples[indices_within_1sigma[0]].copy() for _ in range(dims)]
    maxima = [flat_samples[indices_within_1sigma[0]].copy() for _ in range(dims)]
    for index in indices_within_1sigma:
        params = flat_samples[index]
        for i in range(dims):
            if params[i] < minima[i][i]:
                minima[i] = params.copy()
            if params[i] > maxima[i][i]:
                maxima[i] = params.copy()
    print(minima, maxima)
    print(len(minima))
    return minima, maxima


def get_min_max_per_point(v_vals, model_params_list, name_stem=None, theta=None, redshift=None, min_freq=None,
                          max_freq=None, torus_temp=None, torus_luminosity=None, torus_frac=None, data_folder=None,
                          executable=None, command_params_full=None, command_params_1=None, command_params_2=None,
                          verbose=False, eic=False):
    num_points = len(v_vals)
    lowest_per_point = np.array([np.inf for _ in range(num_points)])
    highest_per_point = np.array([-np.inf for _ in range(num_points)])
    print("min_max_per_point")
    if name_stem is None:
        delete_after = True
        name_stem = "for_plotting" + str(random.getrandbits(20))
    else:
        delete_after = False
    for i in tqdm.trange(0, len(model_params_list)):
        params = model_params_list[i]
        model = blazar_model.make_model(params, name_stem, theta=theta, redshift=redshift, min_freq=min_freq,
                                        max_freq=max_freq, torus_temp=torus_temp, torus_luminosity=torus_luminosity,
                                        torus_frac=torus_frac, data_folder=data_folder, executable=executable,
                                        command_params_full=command_params_full, command_params_1=command_params_1,
                                        command_params_2=command_params_2, prev_files=False, use_param_file=False,
                                        verbose=verbose, eic=eic)
        f = interpolate.interp1d(model[0], model[1], fill_value='extrapolate')
        vFv_interpolated = f(v_vals)
        for j in range(num_points):
            if vFv_interpolated[j] < lowest_per_point[j]:
                lowest_per_point[j] = vFv_interpolated[j]
            if vFv_interpolated[j] > highest_per_point[j]:
                highest_per_point[j] = vFv_interpolated[j]

    if delete_after:
        for f in glob.glob(BASE_PATH + DATA_FOLDER + "/" + name_stem + "_*"):
            os.remove(f)
    return lowest_per_point, highest_per_point


def residual_plot(data, best_model, lowest_per_point, highest_per_point):
    f_best = interpolate.interp1d(best_model[2], best_model[3])
    f_low = interpolate.interp1d(best_model[2], np.power(10, lowest_per_point))
    f_high = interpolate.interp1d(best_model[2], np.power(10, highest_per_point))
    plt.fill_between(data[0], f_low(data[0]) - data[1], f_high(data[0]) - data[1], alpha=.5,
                     zorder=1)
    plt.errorbar(data[0], f_best(data[0]) - data[1], yerr=(data[2], data[2]), fmt='.',
                 zorder=2)
    plt.axhline(0, zorder=0, color='k', alpha=.5)
    plt.xlabel(r"Frequency $\nu$ (Hz)")
    plt.ylabel(r"Residual Energy Flux $\nu F_{\nu}$ (erg cm$^{-2}$ s$^{-1})$")
    plt.xscale("log")
