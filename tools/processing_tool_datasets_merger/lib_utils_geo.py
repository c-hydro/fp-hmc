"""
Library Features:

Name:          lib_utils_geo
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20220324'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Libraries
import logging
import numpy as np

from copy import deepcopy

from tools.processing_tool_datasets_merger.lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create index map
def create_map_idx(grid_values):

    grid_rows = grid_values.shape[0]
    grid_cols = grid_values.shape[1]
    grid_n = grid_rows * grid_cols
    grid_idxs = np.arange(grid_n).reshape(grid_rows, grid_cols)

    return grid_idxs
# -------------------------------------------------------------------------------------
