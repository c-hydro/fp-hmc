"""
Library Features:

Name:          lib_utils_cmd
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20221019'
Version:       '2.0.0'
"""
# -------------------------------------------------------------------------------------
# Library
import logging
import subprocess

from copy import deepcopy

from lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to join the command-line of the application
def join_cmd(script_settings, script_sep=' ', script_order=None):

    if script_order is None:
        script_order = ['executable', 'args']

    script_list_part = []
    for script_key in script_order:
        if script_key in list(script_settings.keys()):
            script_element_obj = script_settings[script_key]
        else:
            log_stream.error(' ===> The "' + script_key + '" is not defined in the script settings object')
            raise RuntimeError('The key must be defined for running the application')

        if isinstance(script_element_obj, str):
            script_element_part = deepcopy(script_element_obj)
            script_list_part.append(script_element_part)
        elif isinstance(script_element_obj, dict):
            for script_element_key, script_element_value in script_element_obj.items():
                script_element_part = script_sep.join([script_element_key, script_element_value])
                script_list_part.append(script_element_part)
        else:
            log_stream.error(' ===> The "script_element" must be defined by string or dictionary')
            raise NotImplementedError('Case not implemented yet')

    script_cmd = script_sep.join(script_list_part)

    return script_cmd

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to compose the command-line of the application
def compose_cmd(script_obj_settings_generic, script_obj_main, script_obj_args,
                script_time=None, script_interpreter='python', script_sep=' ',
                tag_script_executable='executable', tag_script_args='args'):

    script_obj_settings_defined = {}
    if tag_script_executable in list(script_obj_settings_generic.keys()):
        script_executable_reference = script_obj_settings_generic[tag_script_executable]
        script_obj_settings_defined[tag_script_executable] = None
    else:
        log_stream.error(' ===> The "' + tag_script_executable +
                         '" obj is not available in the application entrypoint settings.')
        raise RuntimeError('The "' + tag_script_executable +
                           '" obj must be declared in the application entrypoint setting')

    if tag_script_args in list(script_obj_settings_generic.keys()):
        script_args_reference = script_obj_settings_generic[tag_script_args]
        script_obj_settings_defined[tag_script_args] = None
    else:
        log_stream.error(' ===> The "' + tag_script_args +
                         '" obj is not available in the application entrypoint settings.')
        raise RuntimeError('The "' + tag_script_args +
                           '" obj must be declared in the application entrypoint setting')

    if not isinstance(script_executable_reference, str):
        log_stream.error(' ===> The "' + tag_script_executable + '" obj must be defined in string format')
        raise NotImplementedError('Case not implemented yet')

    if not isinstance(script_args_reference, dict):
        log_stream.error(' ===> The "' + tag_script_args + '" obj must be defined in dictionary format')
        raise NotImplementedError('Case not implemented yet')

    if script_executable_reference in list(script_obj_main.keys()):
        script_executable_tmp = script_obj_main[script_executable_reference]
        script_executable_filled = script_sep.join([script_interpreter, script_executable_tmp])
    else:
        log_stream.error(' ===> The "' + script_executable_reference + '" key is not available in the "script_obj_main"')
        raise RuntimeError('The "' + script_executable_reference + '" key must be defined in the configuration file')

    script_args_filled = {}
    for script_args_key, script_args_value in script_args_reference.items():
        if script_args_key != '-time':
            if script_args_value in list(script_obj_args.keys()):
                script_args_filled[script_args_key] = script_obj_args[script_args_value]
            else:
                log_stream.error(' ===> The "' + script_args_value + '" key is not available in the "script_obj_args"')
                raise RuntimeError('The "' + script_args_value + '" key must be defined in the configuration file')

        else:
            if script_time:
                script_time = '"{}"'.format(script_time)
                script_args_filled[script_args_key] = script_time
            else:
                log_stream.error(' ===> The "time" key is defined by NoneType in the collected arguments')
                raise RuntimeError('The "time" key must be defined by a valid time format')

    # Compose settings defined obj
    script_obj_settings_defined[tag_script_executable] = script_executable_filled
    script_obj_settings_defined[tag_script_args] = script_args_filled

    return script_obj_settings_defined
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to execute cmd
def execute_cmd(command_line):

    try:
        # Info start
        log_stream.info(' -----> Process execution [' + command_line + '] ... ')

        # Check command-line calling
        # subprocess.check_call(command_line, shell=True)
        # Execute command-line calling
        return_code = subprocess.call(command_line, shell=True)

        if return_code != 0:
            log_stream.warning(' -----> Process execution [' + command_line + '] ... RETURN ERROR(S)!')
            log_stream.warning(' -----> Return Code: ' + str(return_code))
        else:
            log_stream.info(' -----> Process execution [' + command_line + '] ... OK')

    except subprocess.CalledProcessError as err:
        log_stream.error(' -----> Process execution [' + command_line + '] ... FAILED!')
        log_stream.error(' -----> Process error(s): ' + str(err))
        raise subprocess.CalledProcessError("Process execution FAILED!")
    except OSError as err:
        log_stream.error(' -----> Process execution [' + command_line + '] ... FAILED!')
        log_stream.error(' -----> Process error(s): ' + str(err))
        raise OSError("Process execution FAILED!")

# -------------------------------------------------------------------------------------
