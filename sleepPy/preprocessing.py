# Script for preprocessing EEG data
# that has been scored and outputed
# as time series with labels and fourier
# transform power in columns
# single file for each animal/day to analyse

import re
import sys
import pandas as pd
import numpy as np
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/07_python_package/"
                "actigraphy_analysis")
from actigraphy_analysis.preprocessing \
    import SaveObjectPipeline, create_file_name_path, create_subdir, \
        remove_object_col, read_file_to_df


####### Functions for read original FFT file #######

def _create_index_list(data=(),
                       no_of_channels=()):
    """
    # create a list containing the correct number of signal strings
    # and create a filter to find where they are in the data
    :param data:
    :param no_of_channels:
    :return:
    """
    # create a list containing the correct number of signal strings
    # and create a filter to find where they are in the data
    signal_list = ["Signal %s" % num for num in range(no_of_channels)]
    filter = data.iloc[:,0].isin(signal_list)
    index_times = list(data.index[filter])
    index_times.insert(0, 0)
    final_index = data.index[-1]
    index_times.append(final_index)
    return index_times


def _slice_by_index_times(data=(),
                          index_times=()):
    """
    Function to create list of dataframes between the index times given
    :param data:
    :param index_times:
    :return:
    """
    # Create list of dataframes by slicing between the index times
    list_of_dfs = []
    for index_start, index_end in zip(index_times[:-1], index_times[1:]):
        temp_df = data.loc[index_start:index_end].copy()
        list_of_dfs.append(temp_df)
    return list_of_dfs


def _remove_str_rows(data=(),
                     test_index_range=(),
                     col_no=0):
    """
    Function to test the test index row in col given for a float,
    removes the row if can't turn into float
    :param data:
    :param test_index_range:
    :param col_no:
    :return:
    """
    remove_index=[]
    df = data.copy()
    col_data = df.iloc[:,col_no]
    test_index = col_data.index[test_index_range]
    for index in test_index:
        try:
            float(col_data[index])
        except:
            remove_index.append(index)
    df.drop(remove_index, inplace=True)
    return df


def _remove_str_row_list(data_list=(),
                         test_index_range=(),
                         col_no=0):
    """
    Function to loop over each dataframe in given list and remove
    the non-floatable rows
    :param data_list:
    :param test_index_range:
    :param col_no:
    :return:
    """
    modified_list = []
    for df in data_list:
        temp_df = _remove_str_rows(df,
                                   test_index_range=test_index_range,
                                   col_no=col_no)
        modified_list.append(temp_df)
    return modified_list


def _add_derivation_and_index(data_list=(),
                              derivation_list=("fro", "occ", "foc"),
                              der_label="Derivation",
                              time_column="Time"):
    """
    Function to add in derivation column and re-index the time column
    starting at 00:00:00
    :param data_list:
    :param derivation_list:
    :param der_label:
    :return:
    """
    # Create column labelling between the signals as the derivation
    # which can then be used to create a multi-index
    for dataframe, derivation in zip(data_list, derivation_list):
        dataframe.loc[:,der_label] = derivation
        # alter the time column as index too
        dataframe.set_index(time_column, inplace=True)
        dataframe = reindex_file(dataframe)
        dataframe.reset_index(inplace=True)
        dataframe.rename(columns={
            dataframe.columns[0]:time_column
        }, inplace=True
        )
    return data_list


def read_clean_fft_file(file=(),
                        header=17,
                        derivation_list=["fro", "occ", "foc"],
                        der_label="Derivation",
                        time_index_column=(2),
                        test_index_range=[0,1,2,-2,-1],
                        check_cols=True,
                        rename_cols=True,
                        **kwargs):
    """
    Function to read in the raw file from sleepsign output and tidy properly
    creates multi-index of derivations and resets time index
    returns as a multi-indexed cleaned dataframe
    :param args:
    :param kwargs:
    :return:
    """
    no_of_channels = len(derivation_list)
    # read the file into a dataframe and slice off the header
    df = pd.read_csv(file,
                     header=header)
    df.pop(df.columns[-1])
    
    # find the places where "Signal" isi n the index
    index_times = _create_index_list(data=df,
                                     no_of_channels=no_of_channels)
    # Create list of index columns we can use later to set the correct
    # index columns
    index_columns = [der_label, df.columns[time_index_column]]

    # Separate df out into a list with a single dataframe for each
    # derivation
    list_of_dfs = _slice_by_index_times(data=df,
                                        index_times=index_times)
    
    # Remove all non-float values (remaining "Signal" in the EpochNo columns)
    modified_list = _remove_str_row_list(data_list=list_of_dfs,
                                         test_index_range=test_index_range)
    
    # add the derivation as a final column
    # and set the time index to start at 00:00:00
    derivation_dfs = _add_derivation_and_index(data_list=modified_list,
                                              derivation_list=derivation_list,
                                              der_label=der_label,
                                              time_column=index_columns[1])

    # put back together and set the index as we want it
    final_df = pd.concat(derivation_dfs)
    final_df.set_index(index_columns, inplace=True)
    final_df.pop(final_df.columns[0])
    final_df.name = file.stem
    
    if check_cols:
        check_data_columns(final_df)
    if rename_cols:
        final_df = remove_extra_zeros(final_df)
    
    return final_df


####### Functions for reading all files for an animal #######
##### Functions for creating list of animal files #####

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


def _create_single_animal_file_list(anim_str,
                                    input_dir=()):
    # get a list of all the unique files for just one animal
    animal_file_list = sorted(input_dir.glob((anim_str + "*.txt")))
    
    return animal_file_list


def create_dict_of_animal_lists(file_list,
                                input_dir,
                                anim_range,
                                **kwargs):
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
        animal_file_list = _create_single_animal_file_list(anim,
                                                           input_dir)
        dict_of_animal_lists[anim] = animal_file_list
        
    return dict_of_animal_lists


##### Functions for creating df for a given list of files #####

def _label_dict():
    "Just hides the label dict creation"
    # generate a dictionary of labels to use for each day
    keys = ["1804%02d" %x for x in range(9,27)]
    baseline_labels = ["Baseline_-%s" %x for x in range(1,-1,-1)]
    post_labels = ["Post_%s" %x for x in range(0,2)]
    ll_labels = ["LL_day%s" %x for x in range(len(keys)-(len(baseline_labels) +
                                                      len(post_labels)))]
    labels = baseline_labels + ll_labels + post_labels
    label_dict = dict(zip(keys, labels))
    return label_dict


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
    last_index_time = masked_data[::-1].first_valid_index()[2]
    # grab the first index so can slice between
    start_index_time = data.iloc[0].name[2]

    # Now need to slice up until the last timestamp for all derivations
    data_sliced = data.xs(slice(start_index_time,
                                last_index_time),
                          level= "Time",
                          drop_level= False)
    
    return data_sliced


def _create_set_day(day_file=(),
                    label_dict=(),
                    day_range=(),
                    period_label=(),
                    **kwargs):
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
    day_df = read_clean_fft_file(day_file, **kwargs)
    day_df[period_label] = label

    # set the index with label as the first level of the index
    temp_day = day_df.set_index(period_label, append=True)
    set_day = temp_day.reorder_levels([2,0,1])
    set_day = _remove_tail(set_day, **kwargs)
    
    return set_day


def single_df_for_animal(animal_file_list=(),
                         day_range=(-6),
                         period_label="Light_period",
                         label_dict=None,
                         **kwargs):
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
    if not label_dict:
        label_dict = _label_dict()
    # create list to hold set days
    list_of_days = []
    # loop through all the days for a given animal
    for day_file in animal_file_list:
        # get the properly ordered df
        set_day_df = _create_set_day(day_file=day_file,
                                     label_dict=label_dict,
                                     day_range=day_range,
                                     period_label=period_label,
                                     **kwargs)
        
        # put this day into a list
        list_of_days.append(set_day_df)
    # concatenate all the days into a giant df
    animal_df = pd.concat(list_of_days)
    
    return animal_df


####### Functions for


def check_data_columns(data):
        """
        checks data has been imported correctly by checking the value
        of the first column
        
        """
        hz_column = data.columns[3]
        if not hz_column == "0.500000Hz":
            raise ValueError("Incorrect column name")
        return None

def remove_extra_zeros(data):
    """
    Function to remove last 4 zeros from column names to make easier to slice
    """
    col_list = []
    for col in data.columns:
        if "0000" in col:
            col = col[:-6] + col[-2:]
        col_list.append(col)
    data.columns = col_list
    return data
    

def artefacts_null(data,
                   stage_column="Stage",
                   stages_list=["W","NR","R"],
                   other=np.nan,
                   **kwargs):
    """
    Function to set all values which aren't in
     stages_list to np.nan, aimed to remove artefact values
    :param data:
    :param stage_column:
    :param stages_list:
    :return:
    """
    # create a mask of where the Stage is in the whitelist
    # remove object column
    # set all the values outside the mask to be nan
    # reset the object column
    # return the new data
    artefact_mask = data.loc[:,stage_column].isin(stages_list)
    df_nocol, cols = remove_object_col(data, return_cols=True)
    masked_data = df_nocol.where(artefact_mask, other=other)
    for col in cols:
        col_name = col.name
        masked_data[col_name] = col
    return masked_data

def sum_power(data,
              range_to_sum):
    """
    Function to sum over the range given as a string for column names
    :param data:
    :param range_to_sum:
    :return:
    """
    # select just the columns want to sum and return those values
    start = data.columns.get_loc(range_to_sum[0])
    fin = data.columns.get_loc(range_to_sum[1])
    sliced_by_freq = data.iloc[:,start:fin]
    summed = pd.DataFrame(sliced_by_freq.sum(axis=1))
    return summed

def create_df_for_single_band(data,
                              name_of_band=(),
                              range_to_sum=()):
    """
    Function to remove object column, sum up frequency, then add
    back in the sleep stage data and name the column
    :param data:
    :param name_of_band:
    :param range_to_sum:
    :return:
    """
    data_removed, cols = remove_object_col(data, return_cols=True)
    data_summed = sum_power(data_removed,
                            range_to_sum=range_to_sum)
    data_summed.columns = name_of_band
    for col in cols:
        data_summed[col.name] = col
    return data_summed

def create_scored_df(data,
                     stages_to_score,
                     stage_col="Stage"):
    """
    Function to create dataframe scoring the given stages all as 1
        returns same dataframe and full FFT but changes stage column
        to int of stages, can be used to score sleep and wake totals
    :param data:
    :param stages_to_score:
    :param stage_col:
    :return:
    """
    df = data.copy()
    scored_column = df.loc[:,stage_col].isin(stages_to_score).astype(int)
    df[stage_col] = scored_column
    return df


def get_all_files_per_animal(file_list,
                             anim_range=[0,3]):
    """
    Function to get a list of file names for a single animal
    each animal
    :param file_list:
    :param anim_range:
    :param derivation_range:
    :return:
    """
    
    # get all the animal names and derivation_names
    anim_list = []
    for file in file_list:
        anim = file.name[anim_range[0]:anim_range[-1]]
        anim_list.append(anim)
    unique_anim = list(set(anim_list))

    # read all the file names for a single or all derivations into the dict
    dict_animal_day_files = {}
    for animal in unique_anim:
        animal_day_files = sorted(
             input_dir.glob(animal+"*.csv")
        )
        dict_animal_day_files[animal] = animal_day_files
    
    return dict_animal_day_files


def create_stage_csv(input_dir,
                     save_dir,
                     subdir_name,
                     save_suffix="_stages.csv",
                     **kwargs):
    """
    Function to take in input dir and then save all in an output
    :param input_dir:
    :param save_path:
    :return:
    """
    save_subdir = create_subdir(save_dir, subdir_name)
    all_files_per_animal = get_all_files_per_animal(input_dir=input_dir)
    for animal in all_files_per_animal:
        save_path = save_subdir / (animal + save_suffix)
        stage_df = create_stage_df(all_files_per_animal[animal],**kwargs)
        stage_df.to_csv(save_path)
        
        
def reindex_file(data,
                 start_index="2018-01-01 00:00:00",
                 freq="4S"):
    """
    Function to take in old dataframe, create new index and return
    :param data:
    :param start_index:
    :param freq:
    :return:
    """
    index = pd.DatetimeIndex(start=start_index,
                             freq=freq,
                             periods=len(data))
    data.index = index
    return data


def score_whole_df(data,
                   stages):
    """
    Function to score all the columns in the df - useful for stage df
    :param data:
    :param stages:
    :return:
    """
    sleep_df = data.copy()
    for col in sleep_df.columns:
        sleep_df = create_scored_df(sleep_df,
                                    stages_to_score=stages,
                                    stage_col=col)
    return sleep_df

def convert_to_units(data,
                     base_freq,
                     target_freq):
    """
    Function to convert data from current frequency
    :param data:
    :param base_freq:
    :param target_freq:
    :return:
    """
    base_secs = pd.Timedelta(base_freq).total_seconds()
    target_secs = pd.Timedelta(target_freq).total_seconds()
    new_data = data.copy()
    new_data = (new_data * base_secs) / target_secs
    return new_data


def _get_index_values(data,
                      level_of_index=0):
    index_values = data.index.get_level_values(level_of_index).unique()
    return index_values
    
def _split_list_of_derivations(data,
                               level_of_index=0):
    """
    Function to take dataframe in and split into a list of dataframes
    based on value of given level of multi-index
    :param data:
    :return:
    """
    # step one, get all the derivation values
    derivation_values = _get_index_values(data,
                                          level_of_index=level_of_index)

    # Step two, slice the df by derivation and put in list
    list_of_dfs = []
    for derivation in derivation_values:
        temp_df = data.loc[derivation]
        temp_df.name = derivation
        list_of_dfs.append(temp_df)
        
    return list_of_dfs


def _sep_by_top_index(df):
    """
    Function returns list of dataframes defined by the level 0 of the
    multi-index
    :param df:
    :return:
    """
    # create list of unique values of given index level
    index_vals = _get_index_values(df, level_of_index=0)

    # loop through and slice the df based on the unique index vals
    separated_list = []
    for value in index_vals:
        temp_df = df.loc[value]
        temp_df.name = value
        separated_list.append(temp_df)
    
    return separated_list


def create_stage_df(df,
                    stage_col="Stage",
                    remove_artefacts=False,
                    artefact_stage_col="Stage",
                    stages="",
                    der_no=0,
                    **kwargs):
    """
    Function to take in the dataframe with multi-index of day-derivation-time
    and return a dataframe of time, with "stage col" as a separate column for
    each original day
    :param df:
    :param stage_col:
    :param kwargs:
    :return:
    """
    # only use the stages given if asked.
    if remove_artefacts:
        df = artefacts_null(df,
                            artefact_stage_col,
                            stages_list=stages,
                            **kwargs)
        
    # Step one, select just the stage column from each day
    # only select one derivation so not duplicating
    second_level = df.index.get_level_values(1).unique()
    der_to_use = second_level[der_no]
    single_der_df = df.xs(der_to_use, level=1)

    # get the values of the first level
    first_level = df.index.get_level_values(0).unique()
    # loop through each day and select the stage for that day
    stage_day_dict = {}
    for day in first_level:
        temp_df = single_der_df.loc[day, stage_col]
        stage_day_dict[day] = temp_df
        
    # Create the final df
    stage_df = pd.concat(stage_day_dict, axis=1)
    stage_df.name = der_to_use

    return stage_df

# TODO update to remove 0 values <- where "Stage" = nan
