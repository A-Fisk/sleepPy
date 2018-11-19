# script to run to check remove header working as expected
import pathlib
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                   "07_python_package/sleepPy")
import sleepPy.preprocessing as prep
import sleepPy.plots as plot

# define import dir
input_dir = pathlib.Path("/Users/angusfisk/Documents/01_PhD_files/01_projects"
                         "/P3_LLEEG_Chapter3/01_data_files/06_fft_files")
save_dir = input_dir.parent
subdir_name = "07_clean_fft_files"

file_list = sorted(input_dir.glob("*.txt"))
file = file_list

# Got remove_tail working!!!

df = prep.single_df_for_animal(file)

def _remove_tail(data, stage_col="Stage", none_label= "None", **kwargs):
    """
    Function to remove the tail of Nan scored value from df
    takes in singel day df and finds the last point where scored
    slices between the two and returns
    :param data:
    :param stage_col:
    :param none_label:
    :param kwargs:
    :return:
    """
    # Trying to figure out how to remove tail of Nan scored area
    # Need to grab the last index where still has a stage
    # and remove everything after that
    # Step one, grab the last index.
    mask = data.loc[:,stage_col] == none_label
    masked_data = data.mask(mask)
    last_index_time = masked_data[::-1].first_valid_index()[1]
    # grab the first index so can slice between
    start_index_time = data.iloc[0].name[1]

    # Now need to slice up until the last timestamp for all derivations
    data_sliced = data.xs(slice(start_index_time,
                                last_index_time),
                          level= "Time",
                          drop_level= False)
    
    return data_sliced
