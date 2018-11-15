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
save_dir = input_dir.parent
subdir_name = "07_clean_fft_files"

file_list = sorted(input_dir.glob("*.txt"))
file = file_list[0]


read_kwargs = {
    "period_label":"Light_period",
    "anim_range":(0,3),
    "day_range":(-6)
}



test_object = prep.SaveObjectPipeline(input_directory=input_dir,
                                      save_directory=save_dir,
                                      search_suffix=".txt",
                                      readfile=False)

animal_file_list = prep.create_dict_of_animal_lists(test_object.file_list,
                                                    input_dir,
                                                    **read_kwargs)
kwargs = {
    "save_suffix_file":"_clean.csv",
    "savecsv":True,
    "function":(prep, "single_df_for_animal"),
    "subdir_name":subdir_name,
    "object_list":animal_file_list.values(),
    "file_list":animal_file_list.keys(),
    "header":17,
    "derivation_list":["fro", "occ", "foc"],
    "der_label":"Derivation",
    "time_index_column":(2),
    "test_index_range":[0,1,2,-2,-1],
    "period_label":"Light_period",
    "anim_range":(0,3),
    "day_range":(-6)
}

test_object.process_file(**kwargs)


# # df = prep.read_clean_fft_file(file)
#
# animals_lists = prep.create_dict_of_animal_lists(file_list,
#                                                  input_dir,
#                                                  anim_range)
#
# animals_lists.keys()
#
#
# animal_df = prep.single_df_for_animal(animals_lists["LL1"],
#                                       day_range=day_range,
#                                       period_label=period_label)


