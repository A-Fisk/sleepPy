# script to run to check remove header working as expected
import pathlib
import sys
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                   "07_python_package/sleepPy")
import sleepPy.preprocessing as prep
import sleepPy.plots as plot

import seaborn as sns
sns.set()

# define import dir
input_dir = pathlib.Path("/Users/angusfisk/Documents/01_PhD_files/01_projects"
                         "/P3_LLEEG_Chapter3/01_data_files/07_clean_fft_files/")
save_dir = input_dir.parents[1] / "03_analysis_outputs"
subdir_name = "01_delta_hypnograms"

plot_kwargs = {
    "showfig":True,
    "savefig":False,
    "figsize":(10,10),
    "name_of_band":["Delta"],
    "range_to_sum":("0.50Hz", "4.00Hz"),
    "level_of_index":0,
    "label_col":-1,
    "base_freq":"4S",
    "plot_epochs":False,
    "set_file_title":False,
    "sharey":False,
    "legend":True
}


init_kwargs = {
   "input_directory":input_dir,
    "save_directory":save_dir,
    "subdir_name":subdir_name,
    "func":(prep, "read_file_to_df"),
    "search_suffix":".csv",
    "readfile":True,
    "index_col":[0,1,2],
    "header":[0]
}
test_object = prep.SaveObjectPipeline(**init_kwargs)

process_kwargs = {
    "function":(prep, "_sep_by_top_index"),
    "savecsv":False
}
test_object.process_file(**process_kwargs)

test_processed_df = test_object.processed_list[0][0]

plot_kwargs["fname"] =test_object.file_list[0]


def _create_file_list(object_list, file):
    """
    Function to create list of file stems
    """
    # generate list of lists of file-names to match processed_df
    file_list = [file for x in range(len(object_list))]
        
    return file_list


def create_file_name_list(object_list, file_list):
    # generate list of file lists
    file_name_list = []
    for sub_list, file in zip(object_list, file_list):
        temp_file_list = _create_file_list(sub_list, file)
        file_name_list = file_name_list + temp_file_list

    return file_name_list

file_name_list = create_file_name_list(test_object.processed_list,
                                       test_object.file_list)

plot.plot_hypnogram_from_df(test_processed_df, **plot_kwargs)

# hypnogram_object = prep.SaveObjectPipeline(input_directory=input_dir,
#                                       save_directory=save_dir,
#                                       read_file_fx=(prep,
#                                                     "read_file_to_df"),
#                                       **read_kwargs)
#

# hypnogram_object.create_plot(function=(plot, "plot_hypnogram_from_df"),
#                              subdir_name=subdir_name,
#                              remove_col=False,
#                              **plot_kwargs)
#
#
#

