# Script for plotting data from EEG frequency bands

import pandas as pd
idx = pd.IndexSlice
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import sys
import seaborn as sns
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                   "07_python_package/sleepPy")
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/07_python_package/"
                "actiPy")
from sleepPy.preprocessing import \
    _split_list_of_derivations, artefacts_null, create_df_for_single_band, \
    score_whole_df, convert_to_units

from actiPy.preprocessing \
    import separate_by_condition
from actiPy.plots import \
    single_plot_kwarg_decorator, \
    multiple_plot_kwarg_decorator, \
    show_savefig_decorator, set_title_decorator

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
    ax.set(xlim=[data.index[0], data.index[-1]])
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

@show_savefig_decorator
@multiple_plot_kwarg_decorator
def _plot_cumulative_stage(data,
                           *args,
                           **kwargs):
    """
    Function to take in data of scored stage and do a cumulative plot of
    each column on the same axis
    :param data:
    :param args:
    :param kwargs:
    :return:
    """
    fig, ax = plt.subplots()
    
    # plot each day on the same axis and create a legend for it
    for col in data:
        data_to_plot = data.loc[:,col]
        ax.plot(data_to_plot,
                label=col)
    fig.legend()
    ax.set(xlim=[data.index[0], data.index[-1]])
    
    params_dict = {
        "interval":2,
        "xlabel": "ZT/CT",
        "ylabel": "Cumulative stage (hours)",
        "title": "Cumulative stage over days"
    }
    
    return fig, ax, params_dict

def plot_cumulative_from_stage_df(data,
                                  scored=True,
                                  stages=None,
                                  base_freq=None,
                                  target_freq=None,
                                  end_of_title=3,
                                  set_file_title=True,
                                  set_name_title=False,
                                  *args,
                                  **kwargs):
    """
    Function to take in raw dataframe that has been read in and
        plot the cumulative sum of all the columns on the same axis
    :param scored_df:
    :param base_freq:
    :param target_freq:
    :param args:
    :param kwargs:
    :return:
    """
    if scored:
        scored_df = score_whole_df(data,stages)
    else:
        scored_df = data
    
    cumsum_df = scored_df.cumsum()
    converted_data = convert_to_units(cumsum_df,
                                     base_freq,
                                     target_freq)
    if set_file_title:
        kwargs["title"] = kwargs["fname"].stem[:end_of_title]
    if set_name_title:
        kwargs["title"] = kwargs["fname"].stem[:end_of_title] + data.name

    _plot_cumulative_stage(converted_data,
                           *args,
                           **kwargs)
    
    
def _create_plot_ready_stages_list(data,
                                   label_col=-1):
    """
    Function to take in single dataframe, remove artefacts,
    separate into stages and sort the stages list
    :param data:
    :return:
    """
    artefact_free_df = artefacts_null(data).dropna(axis=0)
    separated_data_list = separate_by_condition(artefact_free_df,
                                                label_col=label_col)
    sorted_data_list = _sort_separated_list(separated_data_list,
                                            label_col=label_col)
    return sorted_data_list


@show_savefig_decorator
@multiple_plot_kwarg_decorator
def _plot_hypnogram_from_list(data_list,
                              label_col=-1,
                              base_freq="4S",
                              plot_epochs=False,
                              sharey=True,
                              **kwargs):
    """
    Function to take list separated into derivations and plot each
    derivation on a separate subplot
    :param data_list:
    :param label_col:
    :param base_freq:
    :param plot_epochs:
    :return:
    """
    # AIM plot each derivation on a subplot
    sharex = True
    if plot_epochs:
        sharex = False

    # create the correct number of subplots
    fig, ax = plt.subplots(nrows=len(data_list),
                           sharex=sharex,
                           sharey=sharey)
     
    # generate a dict of colour keys
    colour_keys = {"W":"b",
                   "NR":"g",
                   "R":"r",
                   "M":"b"}
    if "colour_keys" in kwargs:
        colour_keys = kwargs["colour_keys"]
        
    # iterate through the subplots and plot each derivation on that subplot
    for curr_axis, der_df in zip(ax, data_list):
        # preprocess the data
        # set artefacts to be null, separate into a sorted list of conditions
        stages_list = _create_plot_ready_stages_list(der_df,
                                                     label_col=label_col)
        
        # loop through the list of separate stages and plot on the same axis
        for curr_df in stages_list:
            # remove interpolation lines and label col by resampling
            data_to_plot = curr_df.resample(base_freq).mean()
            # for quality control, allow option to plot by epoch number
            if plot_epochs:
                data_to_plot = data_to_plot.reset_index(drop=True)
            # grab the value of the stage for labelling
            label = curr_df.iloc[0,label_col]
            curr_axis.plot(data_to_plot,
                           colour_keys[label],
                           label=label)
        # label the axis with the current derivation
        curr_axis.set(ylabel=der_df.name)
    
    # set the default values dict
    param_dict = {
        "xlim":[der_df.index[0],der_df.index[-1]],
        "xlabel":"ZT/CT",
        "ylabel":"Power v2 (?)",
        "title":("%s over time" %der_df.columns[0]),
        "interval":3
    }
    if plot_epochs:
        param_dict["xlabel"] = "Epoch No"
        param_dict["timeaxis"] = False
        param_dict["xlim"] = [data_to_plot.index[0], data_to_plot.index[-1]]
    
    return fig, ax[-1], param_dict


def plot_hypnogram_from_df(data,
                           name_of_band=["Delta"],
                           range_to_sum=("0.50Hz", "4.00Hz"),
                           level_of_index=0,
                           label_col=-1,
                           base_freq="4S",
                           plot_epochs=False,
                           set_file_title=False,
                           set_name_title=True,
                           **kwargs):
    """
    Function to take in dataframe with multiple derivations,
    sum the given power band, then plot the hypnogram
    :param data:
    :param kwargs:
    :return:
    """
    # first step, sum the given band
    band_df = create_df_for_single_band(data,
                                        name_of_band=name_of_band,
                                        range_to_sum=range_to_sum)
    # Separate out into a list of derivations
    list_of_derivations = _split_list_of_derivations(band_df,
                                             level_of_index=level_of_index
                                             )
    
    # set the title of the plot to be the file name or
    # period name if needed
    if set_file_title:
        kwargs["title"] = kwargs["fname"].stem
    if set_name_title:
        kwargs["title"] = kwargs["fname"].stem + "_" + data.name
    
    # plot the hypnogram from the list of derivations
    _plot_hypnogram_from_list(list_of_derivations,
                              label_col=label_col,
                              base_freq=base_freq,
                              plot_epochs=plot_epochs,
                              **kwargs)
    

def plot_hypnogram_from_list(data_list, fname="", **kwargs):
    """
    Function to loop through all the values in a list of dataframes and
    call plot hypnogram from df on all of them
    :param data_list:
    :param file:
    :param kwargs:
    :return:
    """
    # loop through and call plot hypnogram from df on all of them
    for df in data_list:
        new_fname = fname.with_name((fname.stem +
                                     "_" +
                                     df.name +
                                     fname.suffix))
        plot_hypnogram_from_df(df, fname=new_fname, **kwargs)
    
    
####### Plot spectrum #####


@set_title_decorator
@show_savefig_decorator
@multiple_plot_kwarg_decorator
def _plot_spectrum(data, tick_space=10, **kwargs):
    """
    Plots the spectrum on a single axis from multiple day
    :param data:
    :param kwargs:
    :return:
    """

    fig, ax = plt.subplots()

    for day in data:
        data_to_plot = data.loc[:,day]
        ax.plot(data_to_plot)
        ax.set_yscale('log')
        
    # Tidy up the x axis
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_space))
    ax.tick_params(axis="x", rotation=45)
    
    params_dict = {
        "timeaxis": False,
        "title": "Mean spectrum over multiple days",
        "xlabel": "Frequency, Hz",
        "ylabel": "Mean power, log units"
    }
    
    return fig, ax, params_dict


@multiple_plot_kwarg_decorator
def _total_plot(data: pd.DataFrame,
                **kwargs):
    """
    Plots box and whisker plot with overlying scatter of datapoints
    :param data:
    :param kwargs:
    :return:
    """
    fig, ax = plt.subplots()

    sns.swarmplot(data=data, color='k', ax=ax)
    sns.boxplot(data=data, ax=ax, fliersize=0)

    params_dict = {
        "timeaxis": False,
        "legend": False,
        "title": "Total sleep per day",
        "xlabel": "experimental day",
        "ylabel": "total sleep (hours)"
    }
    
    return fig, ax, params_dict


@multiple_plot_kwarg_decorator
def dark_light_plot(data: pd.DataFrame,
                    x: str,
                    y: str,
                    hue: str,
                    **kwargs):

    fig, ax = plt.subplots()

    sns.swarmplot(data=data, x=x, y=y, hue=hue, ax=ax,
                  color='0.2', dodge=True)
    sns.boxplot(data=data, x=x, y=y, hue=hue, ax=ax,
                fliersize=0)

    handles, labels = ax.get_legend_handles_labels()
    legend = plt.legend(handles[0:2],
                        labels[0:2])
    
    params_dict = {
        "timeaxis": False,
        "legend": False,
        "title": "Total sleep per day",
        "xlabel": False,
        "ylabel": False,
    }
    
    return fig, ax, params_dict


def draw_sighlines(yval: float,
                   sig_list: list,
                   label_loc_dict: dict,
                   minus_val: float,
                   plus_val: float,
                   curr_ax,
                   **kwargs):
    """
    Draws an hline at the position indicated in the sig list of indexes by
    looking it up in label_loc_dict then drawing a hline at the yval from
    loc mins_val to loc plus_val on curr_ax
    :param yval:
    :param sig_list:
    :param label_loc_dict:
    :param minus_val:
    :param plus_val:
    :param curr_ax:
    :return:
    """
    for xval in sig_list:
        curr_xval = label_loc_dict[xval]
        hxvals = [curr_xval - minus_val, curr_xval + plus_val]
        hxval_axes = curr_ax.transLimits.transform([(hxvals[0], 0),
                                                    (hxvals[1], 0)])
        hxval_axes_val = hxval_axes[:, 0]
        curr_ax.axhline(yval,
                        xmin=hxval_axes_val[0],
                        xmax=hxval_axes_val[1],
                        **kwargs)

def get_xval_dates(curr_xval,
                   minus_val: float,
                   plus_val: float,
                   curr_ax):
    """
    Works to get xvals to plot if dates
    :param sig_list:
    :param minus_val:
    :param plus_val:
    :param curr_ax:
    :return:
    """
    hxvals = [curr_xval - minus_val, curr_xval + plus_val]
    hxvals_num = [mdates.date2num(x) for x in hxvals]
    hxvals_transformed = curr_ax.transLimits.transform(
        [(hxvals_num[0], 0),
         (hxvals_num[1], 0)]
    )
    hxvals_trans_xvals = hxvals_transformed[:, 0]
    
    return hxvals_trans_xvals
    

def get_xtick_dict(curr_ax):
    """
    Returns a dict of the locations of where each label is
    Can then be used to find where to draw liens
    :param curr_ax:
    :return:
    """
    labels = curr_ax.get_xticklabels()
    locs = curr_ax.get_xticks()
    label_text = [str(x.get_text()) for x in labels]
    label_loc_dict = dict(zip(label_text, locs))
    return label_loc_dict


def sig_locs_get(df: pd.DataFrame,
                 sig_col: str = "p-tukey",
                 sig_val: float = 0.05,
                 index_level2val: int = 0):
    """
    Finds where the sig_col is less than the sig_val for the index_level2val
    Used for a posthoc tukeys df as example where 0 =baseline-disrupted
    1=baseline-recovery etc.
    :param df:
    :param sig_col:
    :param sig_val:
    :param index_level2val:
    :return:
    """
    sig_mask = df[sig_col] < sig_val
    sig_vals = df[sig_mask]
    sig_index = sig_vals.loc[idx[:, index_level2val], :
                ].index.get_level_values(0)
    return sig_index


def sig_line_coord_get(curr_ax,
                       sig_line_ylevel: float = 0.9):
    """
    Finds the sig_line_level in axes co-ordinates
    :param curr_ax:
    :param sig_line_ylevel:
    :return:
    """
    axes_to_data = curr_ax.transLimits.inverted()
    ycoords = (0.5, sig_line_ylevel)
    ycoords_data = axes_to_data.transform(ycoords)
    ycoord_data_val = ycoords_data[1]
    
    return ycoord_data_val
