"""
Class Features

Name:          drv_configuration_hmc_run
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import os
import re

import numpy as np

from hmc.algorithm.namelist.lib_namelist import write_namelist_file

from hmc.algorithm.utils.lib_utils_list import convert_string_2_list, convert_list_2_string
from hmc.algorithm.utils.lib_utils_dict import get_dict_value
from hmc.algorithm.utils.lib_utils_string import fill_tags2string
from hmc.algorithm.utils.lib_utils_system import create_folder, split_path, copy_file

from hmc.algorithm.default.lib_default_args import logger_name

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to configure run
class ModelRun:

    # -------------------------------------------------------------------------------------
    # Method class initialization
    def __init__(self, obj_run_info_ref, template_run=None,
                 tag_var_name='{var_name}_{ens_name}',
                 tag_run_probabilistic='probabilistic_{var_name}_{ens_name}',
                 tag_run_deterministic='deterministic', **kwargs):

        self.obj_run_info_ref = obj_run_info_ref

        self.tag_var_name = tag_var_name
        self.tag_run_probabilistic = tag_run_probabilistic
        self.tag_run_deterministic = tag_run_deterministic

        self.tag_executable = 'executable'
        self.tag_library = 'library'
        self.tag_temp = 'tmp'

        self.tag_folder = 'file_folder'
        self.tag_filename = 'file_name'
        self.tag_arguments = 'arguments'
        self.tag_deps = 'dependencies'

        self.tag_run_root_generic = 'run_root_generic'
        self.tag_run_root_main = 'run_root_main'

        self.obj_template_run_ref = template_run

        self.obj_run_info_filled, self.obj_template_run_filled = self.set_run_mode()
        self.obj_run_info_filled, self.obj_run_path = self.set_run_path()
        self.obj_run_info_filled, self.obj_run_args = self.set_run_arguments()

        self.line_indent = 4 * ' '

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize run dependencies
    def organize_run_dependencies(self, tag_location='run_location'):

        # Starting information
        log_stream.info(' ----> Organize run dependencies information ... ')

        tags_deps = self.tag_deps
        obj_library_raw = self.obj_run_info_ref[tag_location]['library']

        run_info_obj = {}
        deps_obj = {}
        for run_key, run_step in self.obj_run_info_filled.items():
            deps_tmp = obj_library_raw[tags_deps]

            if isinstance(deps_tmp, str):
                deps_tmp = [deps_tmp]
            deps_obj[tags_deps] = deps_tmp

            run_tmp = {**run_step, **deps_obj}
            run_info_obj[run_key] = run_tmp

        # Ending information
        log_stream.info(' ----> Organize run dependencies information ... DONE')

        return run_info_obj

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize run execution
    def organize_run_execution(self, obj_namelist_filename, obj_namelist_structure):

        # Starting information
        log_stream.info(' ----> Organize run execution information ... ')

        # Method to set run executable
        run_executable_status = self.set_run_executable()
        # Method to set run namelist
        run_namelist_status = self.set_run_namelist(obj_namelist_filename, obj_namelist_structure)

        # Method to set run command-line
        if run_executable_status and run_namelist_status:
            run_cline_obj = self.set_run_commandline()
        else:
            log_stream.error(' ===> Set run executable or namelist failed')
            raise RuntimeError('Run is not correctly set.')

        # Ending information
        log_stream.info(' ----> Organize run execution information ... DONE')

        return run_cline_obj

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set run commandline
    def set_run_commandline(self):
        run_cline_obj = {}
        for run_key, run_step in self.obj_run_info_filled.items():
            run_exec_step = run_step[self.tag_executable]
            run_args_step = run_step[self.tag_arguments]

            if run_args_step.endswith('.txt'):
                run_folder, run_filename = os.path.split(run_exec_step)
                run_args_step = os.path.join(run_folder, run_args_step)

            run_cline_obj[run_key] = ' '.join([run_exec_step, run_args_step])

        return run_cline_obj
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set run executable
    def set_run_executable(self):

        tag_executable = self.tag_executable
        tag_library = self.tag_library

        run_executable_status = True
        for run_key, run_step in self.obj_run_info_filled.items():
            try:
                run_exec_file_path = run_step[tag_executable]
                run_library_file_path = run_step[tag_library]

                run_exec_file_folder, run_exec_file_name = split_path(run_exec_file_path)
                create_folder(run_exec_file_folder)

                if os.path.exists(run_library_file_path):
                    copy_file(run_library_file_path, run_exec_file_path)
                else:
                    log_stream.error(' ===> Run executable ' + run_library_file_path + ' not found')
                    raise RuntimeError('Run executable is unavailable. Exit.')
            except RuntimeError as run_error:
                log_stream.error(' ===> Run executable is not set! ' + (str(run_error)))
                raise RuntimeError('Run executable is corrupted. Exit.')
        return run_executable_status
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set run namelist
    def set_run_namelist(self, obj_namelist_filename, obj_namelist_structure):

        tag_executable = self.tag_executable

        run_namelist_status = True
        for run_key, run_step in self.obj_run_info_filled.items():
            try:
                run_exec_file_path = run_step[tag_executable]

                run_exec_file_folder, run_exec_file_name = split_path(run_exec_file_path)
                create_folder(run_exec_file_folder)

                namelist_filename = obj_namelist_filename[run_key]
                namelist_structure = obj_namelist_structure[run_key]

                namelist_filepath = os.path.join(run_exec_file_folder, namelist_filename)

                write_namelist_file(namelist_filepath, namelist_structure, line_indent=self.line_indent)

            except RuntimeError as run_error:
                log_stream.error(' ===> Run namelist is not set! ' + (str(run_error)))
                raise RuntimeError('Run namelist is corrupted. Exit.')

        return run_namelist_status
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set run arguments
    def set_run_arguments(self, tag_location='run_location'):

        obj_run_filled = self.obj_run_info_filled

        obj_tmpl_ref = self.obj_template_run_ref
        obj_tmpl_filled = self.obj_template_run_filled

        obj_location_raw = self.obj_run_info_ref[tag_location]

        obj_args_def = {}
        for obj_key, obj_value_raw in obj_location_raw.items():
            for tmpl_key, tmpl_value in obj_tmpl_filled.items():

                if self.tag_arguments in list(obj_value_raw.keys()):

                    if tmpl_key not in list(obj_args_def.keys()):
                        obj_args_def[tmpl_key] = {}

                    args_str_raw = get_dict_value(obj_value_raw, self.tag_arguments)
                    args_list_raw = convert_string_2_list(args_str_raw, ' ')

                    args_list_def = []
                    for args_step in args_list_raw:
                        obj_tmp = fill_tags2string(args_step, obj_tmpl_ref, tmpl_value)
                        args_list_def.append(obj_tmp)

                    args_str_def = convert_list_2_string(args_list_def, ' ')

                    obj_args_def[tmpl_key][self.tag_arguments] = args_str_def

        for obj_args_key, obj_args_dict in obj_args_def.items():
            for obj_dict_key, obj_dict_value in obj_args_dict.items():
                obj_run_filled[obj_args_key][obj_dict_key] = obj_dict_value

        return obj_run_filled, obj_args_def
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set run mode
    def set_run_mode(self, tag_type='run_type'):

        obj_type = self.obj_run_info_ref[tag_type]

        if 'run_mp' in obj_type:
            run_mp = obj_type['run_mp']
            obj_type.pop('run_mp')
        else:
            log_stream.warning(' ===> Run Multiprocessing is not set. Default configuration is false')
            run_mp = False

        if 'run_mode' in obj_type:
            obj_mode = obj_type['run_mode']
        else:
            log_stream.error(' ===> Run Mode is not callable! Check your algorithm file!')
            raise ValueError('Value not valid')

        if 'run_cpu' in obj_type:
            run_cpu = obj_type['run_cpu']
        else:
            log_stream.error(' ===> Run CPU is not callable! CPUs used by processes will be 1')
            run_cpu = 1

        if obj_mode['ens_active']:
            run_mode_raw = self.tag_run_probabilistic
            var_name_raw = self.tag_var_name

            ens_id_min = obj_mode['ens_variable']['var_min']
            ens_id_max = obj_mode['ens_variable']['var_max'] + 1

            run_name = np.arange(ens_id_min, ens_id_max, obj_mode['ens_variable']['var_step']).tolist()
            run_n = np.arange(1, run_name.__len__() + 1, 1).tolist()

            run_mp = [run_mp] * run_n.__len__()
            run_cpu = [run_cpu] * run_n.__len__()

            run_mode = []
            run_var = []
            for run_name_step, run_id in zip(run_name, run_n):
                run_name_step = "{:03d}".format(run_name_step)

                tag_name_step = obj_mode['ens_variable']['var_name']

                if (tag_name_step is None) or (not tag_name_step):
                    var_name_raw = '{ens_name}'
                    run_mode_raw = 'probabilistic_{ens_name}'
                    var_name_step = var_name_raw.format(ens_name=run_name_step)
                    run_mode_step = run_mode_raw.format(ens_name=run_name_step)
                else:
                    var_name_step = var_name_raw.format(var_name=tag_name_step, ens_name=run_name_step)
                    run_mode_step = run_mode_raw.format(var_name=tag_name_step, ens_name=run_name_step)

                run_var.append(var_name_step)
                run_mode.append(run_mode_step)
        else:
            run_mode = [self.tag_run_deterministic]
            run_var = [self.tag_run_deterministic]
            run_name = [1]
            run_n = [1]
            run_mp = [False]
            run_cpu = [1]

        obj_type_upd = {}
        for obj_key, obj_value in obj_type.items():
            if obj_key == 'run_mode':
                obj_type_upd['run_mode'] = run_mode
            else:
                obj_type_upd[obj_key] = [obj_value] * run_mode.__len__()
        obj_type_upd['run_var'] = run_var
        obj_type_upd['run_cpu'] = run_cpu

        run_obj = {}
        for i, (var_step, mode_step, run_step, n_step, mp_step, cpu_step) in enumerate(zip(
                run_var, run_mode, run_name, run_n, run_mp, run_cpu)):
            run_obj[var_step] = {}
            run_obj[var_step]['run_var'] = var_step
            run_obj[var_step]['run_mode'] = mode_step
            run_obj[var_step]['run_name'] = run_step
            run_obj[var_step]['run_id'] = n_step
            run_obj[var_step]['run_mp'] = mp_step
            run_obj[var_step]['run_cpu'] = cpu_step

            for tmpl_step, tmpl_value in obj_type_upd.items():
                run_obj[var_step][tmpl_step] = {}
                run_obj[var_step][tmpl_step] = tmpl_value[i]

        run_template = {}
        for i, var_step in enumerate(run_var):
            run_template[var_step] = {}
            for tmpl_step, tmpl_value in obj_type_upd.items():
                run_template[var_step][tmpl_step] = {}
                run_template[var_step][tmpl_step] = tmpl_value[i]

        return run_obj, run_template

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set run path(s)
    def set_run_path(self, tag_location='run_location'):

        obj_run_filled = self.obj_run_info_filled

        obj_location_raw = self.obj_run_info_ref[tag_location]

        obj_tmpl_ref = self.obj_template_run_ref
        obj_tmpl_filled = self.obj_template_run_filled

        loc_list = [self.tag_folder, self.tag_filename]

        obj_location_def = {}
        for obj_key, obj_value_raw in obj_location_raw.items():
            for tmpl_key, tmpl_value in obj_tmpl_filled.items():

                if tmpl_key not in list(obj_location_def.keys()):
                    obj_location_def[tmpl_key] = {}

                loc_filled = []
                for loc_step in loc_list:
                    obj_tmp = fill_tags2string(obj_value_raw[loc_step], obj_tmpl_ref, tmpl_value)
                    loc_filled.append(obj_tmp)

                if (loc_filled[0] is not None) and (loc_filled[1] is not None):
                    loc_merge = os.path.join(loc_filled[0], loc_filled[1])
                elif (loc_filled[0] is not None) and (loc_filled[1] is None):
                    loc_merge = loc_filled[0]
                elif (loc_filled[0] is None) and (loc_filled[1] is not None):
                    loc_merge = loc_filled[1]
                else:
                    loc_merge = None

                obj_location_def[tmpl_key][obj_key] = loc_merge

                # Set executable path (add conditions)
                if obj_key == self.tag_executable:
                    loc_folder = loc_list[0]
                    folder_name_raw = obj_value_raw[loc_folder]
                    folder_name_tag = re.findall('\{.*?\}', folder_name_raw)

                    if folder_name_tag.__len__() > 0:
                        first_occurrence = folder_name_tag[0]
                        last_occurrence = folder_name_tag[-1]

                        folder_run_root = folder_name_raw.split(first_occurrence)[0]
                        folder_run_main = folder_name_raw.split(last_occurrence)[0]
                        folder_run_main = fill_tags2string(folder_run_main, obj_tmpl_ref, tmpl_value)

                    else:
                        folder_run_root = fill_tags2string(folder_run_main, obj_tmpl_ref, tmpl_value)
                        folder_run_main = fill_tags2string(folder_run_main, obj_tmpl_ref, tmpl_value)

                    obj_location_def[tmpl_key][self.tag_run_root_generic] = folder_run_root
                    obj_location_def[tmpl_key][self.tag_run_root_main] = folder_run_main

        for obj_loc_key, obj_loc_dict in obj_location_def.items():
            for obj_dict_key, obj_dict_value in obj_loc_dict.items():
                obj_run_filled[obj_loc_key][obj_dict_key] = obj_dict_value

        return obj_run_filled, obj_location_def

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
