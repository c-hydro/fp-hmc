"""
Library Features:

Name:          lib_utils_dataframe
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '1.0.0'
"""

#######################################################################################
# Library
import logging
import pandas as pd

from hmc.algorithm.default.lib_default_args import logger_name

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to convert dictionary to dataframe
def convert_dict_2_df(obj_dict, idx_name='run_tag', idx_pivot='key'):
    if idx_pivot == 'key':
        obj_df = pd.DataFrame.from_dict(obj_dict, orient='index')
    else:
        log_stream.error(' ===> DataFrame orientation not implemented yet!')
        raise NotImplementedError('DataFrame orientation is not implemented')
    obj_df.index.name = idx_name
    return obj_df
# -------------------------------------------------------------------------------------
