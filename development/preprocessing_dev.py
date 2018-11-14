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
                         "/P3_LLEEG_Chapter3/01_data_files/06_fft_files/")
save_dir = input_dir

file_list = sorted(input_dir.glob("*.txt"))
file = file_list[0]

period_label = "Light_period"
anim_range = (0,3)
day_range = (-6)

# df = prep.read_clean_fft_file(file)


def _find_unique_anims(file_list,
                       anim_range):
    """
    Returns a list of the unique strings for the range given in the file list
    :param file_list:
    :param anim_range:
    :return:
    """
    # get a list of all the unique animal values in the file list
    anim_list = []
    for file in file_list:
        anim_str = (file.stem[anim_range[0]:anim_range[-1]])
        anim_list.append(anim_str)
    unique_anims = list(set(anim_list))
    
    return unique_anims


def _create_single_animal_file_list(anim_str):
    # get a list of all the unique files for just one animal
    animal_file_list = sorted(input_dir.glob((anim_str + "*.txt")))
    
    return animal_file_list


def create_dict_of_animal_lists(file_list,
                                anim_range):
    """
    Function to return lists of [list of files for single animal]
    :param file_list:
    :param anim_range:
    :return:
    """
    # find all the unique animals in the file list
    unique_anims = _find_unique_anims(file_list,
                                      anim_range)
    # for each unique animal, create a list of all it's files and save
    # it in a list
    dict_of_animal_lists = {}
    for anim in unique_anims:
        animal_file_list = _create_single_animal_file_list(anim)
        dict_of_animal_lists[anim] = animal_file_list
        
    return dict_of_animal_lists


animals_lists = create_dict_of_animal_lists(file_list,
                                            anim_range)

def _label_dict():
    "Just hides the label dict creation"
    # generate a dictionary of labels to use for each day
    keys = ["1804%02d" %x for x in range(9,27)]
    baseline_labels = ["Baseline_-%s" %x for x in range(1,-1,-1)]
    post_labels = ["Post_%s" %x for x in range(0,2)]
    ll_labels = ["LL_%s" %x for x in range(len(keys)-(len(baseline_labels) +
                                                      len(post_labels)))]
    labels = baseline_labels + ll_labels + post_labels
    label_dict = dict(zip(keys, labels))
    return label_dict


def _create_set_day(day_file=(),
                    label_dict=(),
                    day_range=(),
                    period_label=()):
    """
    Gets the day file with the correct label from the dict as the highest
    level of the multi-index
    :param day_file:
    :param label_dict:
    :param day_range:
    :return:
    """
    # grab just the day from the file_list
    day = day_file.stem[day_range:]

    # find what label that should be based on a given dict
    label = label_dict[day]

    # label the dataframe as that label
    day_df = prep.read_clean_fft_file(day_file)
    day_df[period_label] = label

    # set the index with label as the first level of the index
    temp_day = day_df.set_index(period_label, append=True)
    set_day = temp_day.reorder_levels([2,0,1])
    
    return set_day


def single_df_for_animal(animal_file_list=(),
                         day_range=(),
                         period_label=()):
    """
    Function to loop through all files in file list and put them into
    a big df with labelled multi-index by the label_dict
    :param animal_file_list:
    :param day_range:
    :param label_dict:
    :param period_label:
    :return:
    """
    # create the label_dict
    label_dict = _label_dict()
    # create list to hold set days
    list_of_days = []
    # loop through all the days for a given animal
    for day_file in animal_file_list:
        # get the properly ordered df
        set_day_df = _create_set_day(day_file=day_file,
                                     label_dict=label_dict,
                                     day_range=day_range,
                                     period_label=period_label)
        
        # put this day into a list
        list_of_days.append(set_day_df)
    # concatenate all the days into a giant df
    animal_df = pd.concat(list_of_days)
    
    return animal_df


animals_lists.keys()


animal_df = single_df_for_animal(animals_lists["LL1"],
                                 day_range=day_range,
                                 period_label=period_label)


