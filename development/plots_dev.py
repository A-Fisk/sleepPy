# script to run to check remove header working as expected
import pathlib
import sys
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                   "07_python_package/sleepPy")
import sleepPy.preprocessing as prep
import sleepPy.plots as splot
import seaborn as sns
sns.set()

# define import dir
input_dir = pathlib.Path("/Users/angusfisk/Documents/01_PhD_files/01_projects"
                         "/P3_LLEEG_Chapter3/01_data_files/07_clean_fft")
save_dir = input_dir.parent / "03_analysis_outputs"
subdir_name = "01_delta_hypnograms"


read_kwargs = {
    "index_col":[0,1],
    "header":[0]
}

file_list = sorted(input_dir.glob("*.csv"))
file = file_list[0]
df = prep.read_file_to_df(file,
                          **read_kwargs)
#
# delta_df = prep.create_df_for_single_band(df,
#                                           name_of_band=["Delta"],
#                                           range_to_sum=("0.50Hz", "4.00Hz"))
# data_list = _split_list_of_derivations(delta_df)

# _plot_hypnogram_from_list(data_list)
    
splot.plot_hypnogram_from_df(df,
                       showfig=True)


