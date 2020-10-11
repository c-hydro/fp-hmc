"""
Library Features:

Name:          lib_namelist
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import numpy as np

from hmc.algorithm.default.lib_default_args import logger_name

from hmc.algorithm.utils.lib_utils_list import convert_list_2_string
from hmc.algorithm.utils.lib_utils_fortran import define_var_format

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# --------------------------------------------------------------------------------
# Method to write namelist file
def write_namelist_file(filename_namelist, structure_namelist, line_indent=4 * ' '):

    # Write namelist file
    file_obj = open(filename_namelist, 'w')
    try:
        for group_name, group_vars in structure_namelist.items():
            if isinstance(group_vars, list):
                for variables in group_vars:
                    write_namelist_group(file_obj, group_name, variables, line_indent)
            else:
                write_namelist_group(file_obj, group_name, group_vars, line_indent)
    finally:
        file_obj.close()
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# Method to write group namelist
def write_namelist_group(file_obj, group_name, variables, line_indent=4 * ' '):

    # Write group in namelist file
    print('&{0}'.format(group_name), file=file_obj)

    # Cycle(s) over variable(s) and value(s)
    for variable_name, variable_value in sorted(variables.items()):
        if isinstance(variable_value, list):
            # Reduce number precision (if needed)
            variable_list = define_var_format(np.asarray(variable_value))
            line = write_namelist_line(variable_name, variable_list)
            line = line_indent + line
            print('{0}'.format(line), file=file_obj)
        elif isinstance(variable_value, str):
            line = write_namelist_line(variable_name, variable_value)
            line = line_indent + line
            print('{0}'.format(line), file=file_obj)
        else:
            line = write_namelist_line(variable_name, variable_value)
            line = line_indent + line
            print('{0}'.format(line), file=file_obj)

    print('/', file=file_obj)

# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# Method to write line namelist
def write_namelist_line(variable_name, variable_value):

    # Check variable value type
    if isinstance(variable_value, str):
        variable_value_str = variable_value
        variable_value_str = '"' + variable_value_str + '"'
    elif isinstance(variable_value, int):
        variable_value_str = str(int(variable_value))
    elif isinstance(variable_value, float):
        variable_value_str = str(float(variable_value))
    elif isinstance(variable_value, list):
        variable_value_str = convert_list_2_string(variable_value, ',')
    else:
        variable_value_str = str(variable_value)

    # Line definition in Fortran style
    line = str(variable_name) + ' = ' + variable_value_str
    return line

# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# Method to convert template date for model namelist
def convert_template_date(string, template_date=None):

    if template_date is None:
        template_date = {'year': ['%Y', '$yyyy'], 'month': ['%m', '$mm'], 'day': ['%d', '$dd'], 'hour': ['%H', '$HH']}

    for template_key, template_link in template_date.items():
        template_start = template_link[0]
        template_end = template_link[1]

        string = string.replace(template_start, template_end)

    return string
# --------------------------------------------------------------------------------
