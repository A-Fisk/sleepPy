# Script for plotting data from EEG frequency bands

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                   "07_python_package/sleepPy")
import sleepPy.preprocessing as prep
from actigraphy_analysis.preprocessing \
    import separate_by_condition

# Function for plotting by stage
def plot_by_stage(data,
                  label_col,
                  base_freq="4S",
                  plot_epochs=False,
                  *args,
                  **kwargs):
    """
    Function to plot the data by each stage type on a single axis
    :param data:
    :param label_col:
    :return:
    """
    # remove artefacts from the data and separate out
    # into different stages based on each vigilance state
    # then plot each as a separate line and finally adjust the
    # labels
    artefact_free_df = prep.artefacts_null(data)
    artefact_free_drop_nas = artefact_free_df.dropna(axis=0)
    separated_data_list = separate_by_condition(artefact_free_drop_nas,
                                                label_col=label_col)
    separated_data_list = _sort_separated_list(separated_data_list,
                                               label_col=label_col)
    
    # generate a dict of colour keys
    colour_keys = {"W":"b",
                   "NR":"g",
                   "R":"r",
                   "M":"b"}
    if "colour_keys" in kwargs:
        colour_keys = kwargs["colour_keys"]
        
    fig, ax = plt.subplots()
    for df in separated_data_list:
        # inserts NaN's to remove interpolation lines
        df_plot = df.resample(base_freq).mean()
        if plot_epochs:
            df_plot = df_plot.reset_index(drop=True)
        label = df.iloc[0,label_col]
        ax.plot(df_plot, colour_keys[label], label=label)
    fig.legend(loc="upper right")
    
    # tidy up with kwargs and labels
    fig.autofmt_xdate()
    xfmt = mdates.DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_formatter(xfmt)
    
    xlabel = "Time of day"
    if plot_epochs:
        xlabel = "Epoch No"
    if "xlabel" in kwargs:
        xlabel = kwargs["xlabel"]
    ax.set_xlabel(xlabel)
    
    ylabel = "Power v2"
    if "ylabel" in kwargs:
        ylabel = kwargs["ylabel"]
    ax.set_ylabel(ylabel)
    
    title = "Power over time"
    if "title" in kwargs:
        title = kwargs["title"]
    fig.suptitle(title)
    
    if "figsize" in kwargs:
        fig.set_size_inches(kwargs["figsize"])
    if "showfig" in kwargs and kwargs["showfig"]:
        plt.show()
    if "savefig" in kwargs and kwargs["savefig"]:
        plt.savefig(kwargs["fname"])
        plt.close()

def plot_spectral_hypnogram(data,
                            label_col=-1,
                            *args,
                            **kwargs):
    """
    Function to take in dataframe and plot full spectrum hypnogram
    :param data:
    :param spectrum_range - Tuple of string for frequency range
    :param args:
    :param kwargs:
    :return:
    """
    spectrum_name = kwargs["spectrum_name"]
    spectrum_range = kwargs["spectrum_range"]
    # sum up the delta power
    # plot hynpgram for that power
    data_summed = prep.create_df_for_single_band(data,
                                                 name_of_band=spectrum_name,
                                                 range_to_sum=spectrum_range)
    kwargs["title"] = kwargs["fname"].stem
    plot_by_stage(data_summed,
                  label_col=label_col,
                  *args,
                  **kwargs)
                 
def _sort_separated_list(data_list,
                         label_col=-1):
    """
    Function to take separated list and sort by the conditions
    so always getting same sorted list and colours are the same
    :param data_list:
    :param label_col:
    :return:
    """
    sorted_list = sorted(data_list,
                         key=lambda x:x.iloc[0,label_col],
                         reverse=False)
    return sorted_list