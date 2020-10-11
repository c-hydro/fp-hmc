"""
Library Features:

Name:          lib_utils_fortran
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import math
import re

import numpy as np

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to translate variable from python to fortran
def translate_var_py2fortran(var_python, var_format='float32'):
    # Transpose and rotate 2d array
    var_tmp = np.transpose(np.rot90(var_python, -1))
    # Cast variable to float32 to match real(kind = 4) in fortran routine
    if hasattr(np, var_format):
        obj_format = getattr(np, var_format)
    else:
        obj_format = None
    if obj_format:
        var_fortran = obj_format(var_tmp)
    else:
        var_fortran = np.float32(var_tmp)

    return var_fortran

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to translate variable from fortran to python
def translate_var_fortran2py(var_fortran, var_format='float32'):
    # Transpose and rotate 2d array
    var_tmp = np.rot90(np.transpose(var_fortran), 1)
    # Cast variable to float32 to match real(kind = 4) in fortran routine
    if hasattr(np, var_format):
        obj_format = getattr(np, var_format)
    else:
        obj_format = None
    if obj_format:
        var_python = obj_format(var_tmp)
    else:
        var_python = np.float32(var_tmp)

    return var_python

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to look-up var precision (type format = '{0:.3f}')
def lookup_var_precision(format_string):
    return int(re.findall(r'\d+', format_string)[1])
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get variable precision
def get_var_precision(x):
    max_digits = 14
    int_part = int(abs(x))
    magnitude = 1 if int_part == 0 else int(math.log10(int_part)) + 1
    if magnitude >= max_digits:
        return magnitude, 0

    frac_part = abs(x) - int_part
    multiplier = 10 ** (max_digits - magnitude)
    frac_digits = multiplier + int(multiplier * frac_part + 0.5)
    while frac_digits % 10 == 0:
        frac_digits /= 10
    scale = int(math.log10(frac_digits))
    return magnitude + scale, scale
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to define variable array format
def define_var_format(a, format_string='{0:.4f}'):
    values = []
    for i, v in enumerate(a):
        [magnitude, scale] = get_var_precision(v)
        precision_req = lookup_var_precision(format_string)

        if precision_req >= scale:
            values.append(v)
        else:
            values.append(format_string.format(v, i))

    return values
# -------------------------------------------------------------------------------------
