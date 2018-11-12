# script to run to check remove header working as expected
import pathlib
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                   "07_python_package/sleepPy")
import sleepPy.preprocessing as prep
import sleepPy.plots as plot
import seaborn as sns
sns.set()

# define import dir
input_dir = pathlib.Path("/Users/angusfisk/Documents/01_PhD_files/01_projects"
                         "/P3_LLEEG_Chapter3/01_data_files/08_stage_df")

file_list = list(input_dir.glob("*.csv"))

kwargs = {"index_col":0,
          "header":0,
          "check_cols":False,
          "rename_cols":False,
          "drop_cols":False}
df = prep.read_file_to_df(file_list[1],
                          **kwargs)

sleep_stages = ["NR","R", "NR1","R1"]

sleep_df = prep.score_whole_df(df,sleep_stages)

wake_stage = ["W", "W1", "M"]

wake_df = prep.score_whole_df(df,wake_stage)




sleep_cumsum = sleep_df.cumsum()
data = sleep_cumsum.copy()
base_freq = "4S"
target_freq = "1H"

data = prep.convert_to_units(data,
                             base_freq,
                             target_freq)

import matplotlib.pyplot as plt

def my_decorator(func):
    def wrapper():
        print("Something before")
        fig, ax = func()
        ax.set_xlabel("a label")
        print("Something after")
    return wrapper

def second_decorator(func):
    def second_wrap():
        print("Another before")
        fig, ax = plt.subplots()
        fig, ax = func(fig, ax)
        fig.suptitle("A title")
        print("Another after")
        return fig, ax
    return second_wrap

@my_decorator
@second_decorator
def function(fig, ax):
    data = [10 for x in range(10)]
    ax.plot(data)
    print("something in the middle")
    return fig, ax


# trying to create all the ylabel, xlabel, and title functions as deocrators
def single_plot_kwarg_decorator(func):
    """
    Strictly decorating function intended to tidy up all the xlabels, ylabels
    , titles, and savefig/showfig functions
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        # this is only for a single plot so can set xlabel and ylabel
        # can call plots here
        fig, ax = plt.subplots()
        print(kwargs)

        # call the plotting function which will create the plots
        # and set the default values for all the labels
        fig, ax, params_dict = func(data, fig, ax)

        # set the extra values in kwargs
        fig.autofmt_xdate()
        xfmt = mdates.DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(xfmt)
        
        interval = params_dict["interval"]
        if "interval" in kwargs:
            interval = kwargs["interval"]
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=interval))
        
        title = params_dict["title"]
        if "title" in kwargs:
            title = kwargs["title"]
        fig.suptitle(title)
        
        xlabel = params_dict["xlabel"]
        if "xlabel" in kwargs:
            xlabel = kwargs["xlabel"]
        ax.set_xlabel(xlabel)
        ylabel = params_dict["ylabel"]
        if "ylabel" in kwargs:
            ylabel = kwargs["ylabel"]
        ax.set_ylabel(ylabel)
        return fig, ax
    return wrapper

def show_savefig_decorator(func):
    """
    Decotator for only creating the savefig, showfig and figsize kwarg
    arguments
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        
        fig, ax = func(*args, **kwargs)
        
        if "figsize" in kwargs:
            fig.set_size_inches(kwargs["figsize"])
        if "showfig" in kwargs and kwargs["showfig"]:
            plt.show()
        if "savefig" in kwargs and kwargs["savefig"]:
            plt.savefig(kwargs["fname"])
            plt.close()
            
    return wrapper

@show_savefig_decorator
@single_plot_kwarg_decorator
def cumsum(data, fig, ax):
    """
    Function to plot cumulative sum
    """
    for col in data:
        data_to_plot = data.loc[:,col]
        ax.plot(data_to_plot,
                label=col)
    fig.legend()
    params_dict = {"xlabel":"ZT/CT",
                   "ylabel":"hours",
                   "title":"Cumulative stage",
                   "interval":2}
    return fig, ax, params_dict


#
# for col in data:
#     data_to_plot = data.loc[:,col]
#     ax.plot(data_to_plot,
#             label=col)
# fig.legend()
#
# # tidy up with kwargs and labels
# fig.autofmt_xdate()
# xfmt = mdates.DateFormatter("%H:%M:%S")
# ax.xaxis.set_major_formatter(xfmt)
# ax.xaxis.set_major_locator(mdates.HourLocator(interval=interval))
#
#
# xlabel = "ZT/CT"
# if "xlabel" in kwargs:
#     xlabel = kwargs["xlabel"]
# ax.set_xlabel(xlabel)
#
# ylabel = "Cumulative Sleep (Hours)"
# if "ylabel" in kwargs:
#     ylabel = kwargs["ylabel"]
# ax.set_ylabel(ylabel)
#
# title = "Cumulative stage over days"
# if "title" in kwargs:
#     title = kwargs["title"]
# fig.suptitle(title)
#
# if "figsize" in kwargs:
#     fig.set_size_inches(kwargs["figsize"])
# if "showfig" in kwargs and kwargs["showfig"]:
#     plt.show()
# if "savefig" in kwargs and kwargs["savefig"]:
#     plt.savefig(kwargs["fname"])
#     plt.close()
#
# plt.show()