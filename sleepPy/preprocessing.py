# Script for preprocessing EEG data
# that has been scored and outputed
# as time series with labels and fourier
# transform power in columns
# single file for each animal/day to analyse

import re

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
                 save_dir,
                 subdir_name,
                 search_suffix='.txt'):
        # find all the files in the input
        # directory by globbing for csv files
        self.input_dir = input_dir
        self.search_suffix = search_suffix
        self.file_list = list(self.input_dir.glob("*" +
                                                  self.search_suffix
                                                  )
                              )
        self.save_dir = save_dir
        self.subdir = subdir_name
        self.save_dir_path = create_new_directory(self.save_dir,
                                                  self.subdir)
    def remove_all_headers(self):
        """
        function to loop through all file in input directory
        slice off the header adn save in a directory
        :return:
        """
        for file in self.file_list:
            remove_header_and_save(file,
                                   save_dir_path=self.save_dir_path,
                                   save_suffix="_clean.csv")
        
def remove_header_and_save(file,
                           save_dir_path,
                           save_suffix):
    """
    Function to scan through file name, remove
    the header and save the rest of the file
    to a new file in another directory
    :return:
    """
    file_contents = scan_sliceoff_header(file)
    new_file_name = create_new_filename(file,
                                        new_subdir_path=save_dir_path,
                                        save_suffix=save_suffix)
    save_filecontents(file_contents=file_contents,
                      save_path=new_file_name)
    
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
    
def create_new_directory(input_directory,
                         new_dir_name):
    """
    function to take old file path, take the parent
    directory and then create new directory in parent
    directory and save new file in there
    :param old_file_path:
    :param subdir_name:
    :return:
    """
    parent = input_directory.parent
    new_dir = parent / new_dir_name
    if not new_dir.exists():
        new_dir.mkdir()
    return new_dir
  
def save_filecontents(file_contents,
                      save_path):
    """
    function to save the given file contents
    in the save path
    :param file_contents:
    :param save_path:
    :return:
    """
    with open(save_path, 'w', encoding='utf-8') as new_file:
        new_file.write(file_contents)
    
def create_new_filename(old_filename,
                        new_subdir_path,
                        save_suffix):
    """
    function to take old file name, new subdir
    path and new save suffix, then
    add on the suffix to the end
    of the file to be able to save to
    this path
    :param old_filename:
    :param save_suffix:
    :return:
    """
    
    old_file_stem = old_filename.stem
    new_file_path = (new_subdir_path /
                     (old_file_stem +
                     save_suffix))
    return new_file_path
   
