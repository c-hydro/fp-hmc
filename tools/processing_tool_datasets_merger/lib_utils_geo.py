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


def wrap_idx_partial2global(obj_terrain_reference, obj_terrain_domain):
    pass



# -------------------------------------------------------------------------------------
# Method to idxs from partial 2 global domain
def create_idx_partial2global(
        grid_lon_partial, grid_lat_partial,
        rows_ref, cols_ref, xllcorner_ref, yllcorner_reference, cellsize_reference):

    idx_i_reference = np.zeros(shape=[rows_ref, cols_ref])
    idx_j_reference = np.zeros(shape=[rows_ref, cols_ref])
    for i in range(0, grid_lon_partial.shape[0]):
        for j in range(0, grid_lat_partial.shape[1]):

            i_cols = round((grid_lon_partial[i, j] - xllcorner_ref) / cellsize_reference)
            j_rows = round((grid_lat_partial[i, j] - yllcorner_reference) / cellsize_reference)

            j_rows = rows_ref - j_rows

            idx_i_reference[i, j] = i_cols
            idx_j_reference[i, j] = j_rows

            if (j_rows >= 0 and j_rows < geo_mask_reference.shape[0]) and \
                    (i_cols >= 0 and i_cols < geo_mask_reference.shape[1]):
                geo_mask_reference[j_rows, i_cols] = id_domain


    print('ciao')
# -------------------------------------------------------------------------------------
