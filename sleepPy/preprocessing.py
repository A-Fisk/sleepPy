# Script for preprocessing EEG data
# that has been scored and outputed
# as time series with labels and fourier
# transform power in columns
# single file for each animal/day to analyse

import pandas as pd

# Class to remove header from EEG FFT output files
class remove_header_FFT_files():
    """
    Class object for removing header from FFT files
    Globs directory for files, the searches for start of table
    in each file, then saves all in a subdirectory
    :param file_path: string - directory of where to find the
        files
    :param subdir_name: string - where to save output
        default "Clean/"
    :param search_suffix - string, what to glob for
        default ".csv"
    :return: saves output in subdirectory in the
        file path string
    """
    
    def __init__(self,
                 input_dir,
                 search_suffix='.csv',
                 subdir_name="clean/"):
        # find all the files in the input
        # directory by globbing for csv files
        self.input_dir = input_dir
        self.search_suffix = search_suffix
        self.file_list = list(self.input_dir.glob("*" +
                                                  self.search_suffix
                                                  )
                              )
        self.subdir_name = subdir_name
        
    def remove_header(self):
    
def scan_sliceoff_header():
    # TODO write scane sliceoffheader
def create_new_filename():
    # TODO write create new file name
def save_filecontents():
    # TODO write save file contents