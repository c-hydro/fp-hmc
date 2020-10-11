"""
Library Features:

Name:          lib_utils_process
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""
#######################################################################################
# Library
import logging
import subprocess

from os import stat, chmod

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to make executable a bash file
def make_process(file):
    mode = stat(file).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    chmod(file, mode)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to execute process
def exec_process(command_line=None):

    try:

        # Info command-line start
        log_stream.info(' ------> Process execution: ' + command_line + ' ... ')

        # Execute command-line
        process_handle = subprocess.Popen(
            command_line, shell=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Read standard output
        while True:
            string_out = process_handle.stdout.readline()
            if isinstance(string_out, bytes):
                string_out = string_out.decode('UTF-8')

            if string_out == '' and process_handle.poll() is not None:

                if process_handle.poll() == 0:
                    log_stream.warning(' ===> Process POOL = ' + str(process_handle.poll()) + ' KILLED!')
                    break
                else:
                    log_stream.error(' ===> Run failed! Check command-line settings!')
                    raise RuntimeError('Error in executing process')
            if string_out:
                log_stream.info(str(string_out.strip()))

        # Collect stdout and stderr and exitcode
        std_out, std_err = process_handle.communicate()
        std_exit = process_handle.poll()

        if std_out == b'' or std_out == '':
            std_out = None
        if std_err == b'' or std_err == '':
            std_err = None

        # Check stream process
        stream_process(std_out, std_err)

        # Info command-line end
        log_stream.info(' ------> Process execution: ' + command_line + ' ... DONE')
        return [std_out, std_err, std_exit]

    except subprocess.CalledProcessError:
        # Exit code for process error
        log_stream.error(' ===> Process execution FAILED! Errors in the called executable!')
        raise RuntimeError('Errors in the called executable')

    except OSError:
        # Exit code for os error
        log_stream.error(' ===> Process execution FAILED!')
        raise RuntimeError('Executable not found!')

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to stream process
def stream_process(std_out=None, std_err=None):

    if std_out is None and std_err is None:
        return True
    else:
        log_stream.warning(' ===> Exception occurred during process execution!')
        return False
# -------------------------------------------------------------------------------------
