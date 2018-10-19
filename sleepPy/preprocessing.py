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
    
def scan_sliceoff_header(file_path,
                         header="Signal"):
    """
    Function to read file from file
    path and scan for the start of the
    header (start of the actual data)
    Returns the file contents
    :param file_path: string
    :param header: string - default "Signal"
    :return: file contents cut from
        header start
    """
    # read the file
    # scan for the start
    # slice from the start
    with open(file_path, 'r', encoding='utf-8') as current_file:
        file_contents = current_file.read()
        start_of_table = re.search(header, file_contents).start()
        file_contents_modified = file_contents[start_of_table:]
    return file_contents_modified
        
def create_new_filename(old_file_path,
                        subdir_name):
    """
    function to take old file path, take the parent
    directory and then create new directory in parent
    directory and save new file in there
    :param old_file_path:
    :param subdir_name:
    :return:
    """
    # TODO write create new file name
    
def save_filecontents():
    # TODO write save file content

#  Function to check subdirectory and create if doesn't exist
def create_subdir(input_directory, subdir_name):
    """
    Function takes in Path object of input_directory
    and string of subdir name, adds them together, checks if it
    exists and if it doesn't creates new directory

    :param input_directory:
    :param subdir_name:
    :return:
    """

    # create path name
    # check if exists
    # create it if it doesn't exist
    # return path name

    sub_dir_path = input_directory / subdir_name
    if not sub_dir_path.exists():
        sub_dir_path.mkdir()
    return sub_dir_path
s