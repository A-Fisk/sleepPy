# script to run to check remove header working as expected
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
save_dir = input_dir.parents[1]
subdir_name = "03_analysis_outputs/03_spectrum/01_ct0_12/"

der_names = ["fro", "occ", "foc"]
stage_list = ["W", "NR", "R"]
subdir_list = []
for stage in stage_list:
    for der in der_names:
        temp_name = subdir_name + "/" + stage + "/" + der
        subdir_list.append(temp_name)

init_kwargs = {
    "input_directory": input_dir,
    "save_directory": save_dir,
    "subdir_name": subdir_name,
    "func": (prep, "read_file_to_df"),
    "search_suffix": ".csv",
    "readfile": True,
    "index_col": [0, 1, 2],
    "header": [0]
}
spectrum_object = prep.SaveObjectPipeline(**init_kwargs)

process_kwargs = {
    "function": (prep, "_get_spectrum_between_times"),
    "savecsv": False,
    "stage": ["W"],
    "stage_col": "Stage",
    "time_start": "12:00:00",
    "time_end": "00:00:00",
}
spectrum_object.process_file(**process_kwargs)

spectrum_list = prep._get_spectrum_between_times(df, **kwargs)

spectrum_df = spectrum_list[0]

data = spectrum_list

plot_kwargs = {
    "fname": file,
    "legend": True,
}

plot._plot_spectrum(data, **plot_kwargs)


