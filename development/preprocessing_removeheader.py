# script to run to check remove header working as expected
import pathlib
import sys
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                   "07_python_package/sleepPy")
import sleepPy.preprocessing as prep

# define import dir
input_dir = pathlib.Path("/Users/angusfisk/Documents/01_PhD_files/"
                          "02_test_data/1_EEG_test_data")

remove_object = prep.remove_header_FFT_files(input_dir=input_dir)

remove_object.remove_all_headers()
