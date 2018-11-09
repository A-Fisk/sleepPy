# Script for plotting data from EEG frequency bands

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from actigraphy_analysis.preprocessing \
    import separate_by_condition

# Function for plotting by stage
def plot_by_stage(data,
                  label_col):
    """
    Function to plot the data by each stage type on a single axis
    :param data:
    :param label_col:
    :return:
    """
    separated_data_list = separate_by_condition(data,
                                                label_col=label_col)
    fig, ax = plt.subplots()
    for df in separated_data_list:
        ax.plot(df)
    
