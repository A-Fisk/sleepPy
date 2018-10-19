import unittest
import numpy as np
import pandas as pd
import os
import pathlib
from io import StringIO
import sleepPy.preprocessing as prep

np.random.seed(42)

class tests_preprocessing(unittest.TestCase):
    """
    Class for testing functions to do with preprocessing
    and removing header
    """
    def setUp(self):
        # create file contents and save that to a file
        file_line = np.random.randint(0, 100, 100)
        start_file_contents = [(np.append(file_line, "\n"))
                               for x in range(100)]
        signal_line = np.append(file_line[:-1],
                                ("Signal,\n"))
        end_file_contents = [(np.append(file_line, "\n"))
                             for x in range(20)]
        total_file_contents = np.append(start_file_contents,
                                        np.append(signal_line,
                                                  end_file_contents
                                                  )
                                        )
        total_file_string = ','.join(str(x) for x in total_file_contents)
        self.temp_filename = 'temp_file'
        prep.save_filecontents(total_file_string,
                               self.temp_filename)
        
        # create variables for createnewdir_test
        input_dir = pathlib.Path(os.getcwd())
        test_dir_name = 'test_dir'
        new_dir = prep.create_new_directory(input_dir,
                                            new_dir_name=test_dir_name)
        self.new_dir = new_dir
        
    def test_scansliceoffheader(self):
        # call function, check whether number of lines is
        # correct after scanning
        # if this is correct save_filecontents also working
        modified_contents = prep.scan_sliceoff_header(self.temp_filename)
        modified_iterator = StringIO(modified_contents)
        modified_df = pd.read_csv(modified_iterator)
        number_lines_postscan = len(modified_df)
        self.assertEqual(number_lines_postscan, 20)
        
    def test_create_newdir(self):
        # call function
        # check whether dir exists
        self.assertTrue(self.new_dir.exists())
     
    def tearDown(self):
        # remove written file and directory
        os.remove(self.temp_filename)
        os.rmdir(self.new_dir)
        
    
if __name__ == "__main__":
    unittest.main()
