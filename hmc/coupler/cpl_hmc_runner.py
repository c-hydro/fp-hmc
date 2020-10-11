"""
Class Features

Name:          cpl_hmc_runner
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import os
from multiprocessing import Pool, cpu_count

from hmc.algorithm.default.lib_default_args import logger_name

from hmc.algorithm.utils.lib_utils_dict import get_dict_value
from hmc.algorithm.utils.lib_utils_process import exec_process

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to run model application
class ModelRunner:

    # -------------------------------------------------------------------------------------
    # Method time info
    def __init__(self, time_info=None, run_info=None, command_line_info=None,
                 obj_args=None,
                 tag_run_mp='run_mp', tag_run_cpu='run_cpu', tag_run_deps='dependencies'):

        self.time_info = time_info
        self.run_info = run_info
        self.command_line_info = command_line_info

        self.obj_args = obj_args

        run_mp_tmp = get_dict_value(self.run_info, tag_run_mp, [])
        run_mp_unique = list(set(run_mp_tmp))
        if run_mp_unique.__len__() != 1:
            log_stream.warning(' ===> Run multiprocessing flag is not unique.')
        self.run_mp = run_mp_unique[0]

        run_cpu_tmp = get_dict_value(self.run_info, tag_run_cpu, [])
        run_cpu_unique = list(set(run_cpu_tmp))
        if run_cpu_unique.__len__() != 1:
            log_stream.warning(' ===> Run CPUs flag is not unique.')
        self.run_cpu = run_cpu_unique[0]

        run_deps_tmp = get_dict_value(self.run_info, tag_run_deps, [])
        run_deps_unique = list(set(run_deps_tmp))
        for model_dep in run_deps_unique:
            os.environ['LD_LIBRARY_PATH'] = 'LD_LIBRARY_PATH:' + model_dep

        self.run_list = list(self.run_info.keys())
        self.run_cpu = self.set_cpu(self.run_cpu)

        self.flag_cleaning_dynamic_outcome = self.obj_args.obj_datasets['Flags']['cleaning_ancillary_dynamic_outcome']

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to select the cpus used by the model
    @staticmethod
    def set_cpu(run_cpu_usr):

        run_cpu_max = cpu_count() - 2
        if run_cpu_max <= 0:
            run_cpu_max = 1

        if run_cpu_usr <= run_cpu_max:
            run_cpu_select = run_cpu_usr
        else:
            run_cpu_select = run_cpu_max

        return run_cpu_select

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to configure execution
    def configure_execution(self, ancillary_datasets_collections, ancillary_tag_type='dynamic_outcome'):

        log_stream.info(' #### Configure execution ... ')

        file_path_ancillary = ancillary_datasets_collections[ancillary_tag_type]
        if self.flag_cleaning_dynamic_outcome:
            if os.path.exists(file_path_ancillary):
                os.remove(file_path_ancillary)

        if not os.path.exists(file_path_ancillary):

            # Configure sequential or multiprocessing execution mode
            if self.run_mp:
                worker_response = self.worker_mp(process_n=self.run_cpu)
            else:
                worker_response = self.worker_seq()

            # Example of worker response
            # worker_response = [[[None, None, 0], [None, None, 0], [None, None, 0]]]

            worker_response = worker_response[0]
            for run_step, worker_step in zip(self.run_list, worker_response):
                log_stream.info(' ----> Analyze run ' + run_step + ' ... ')
                log_stream.info(' -----> StdOut: ' + str(worker_step[0]))
                log_stream.info(' -----> StdErr: ' + str(worker_step[1]))
                log_stream.info(' -----> StdExit: ' + str(worker_step[2]))
                log_stream.info(' ----> Analyze run ' + run_step + ' ... DONE')

            log_stream.info(' #### Configure execution ... DONE')

        elif os.path.exists(file_path_ancillary):

            # Ending info
            log_stream.info(' #### Configure execution ... SKIPPED. Outcome datasets stored in: ' + file_path_ancillary)

        else:
            # Error in ancillary file
            log_stream.info(' #### Configure execution ... FAILED')
            log_stream.error(' ===> Ancillary file for outcome datasets collections is not correctly defined')
            raise RuntimeError('Bad definition of ancillary dynamic file')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run model in sequential mode
    def worker_seq(self):

        exec_response_list = []
        for run_key, run_cline in self.command_line_info.items():
            exec_response = exec_process(run_cline)
            exec_response_list.append(exec_response)
        return exec_response_list

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run model in multiprocessing mode
    def worker_mp(self, process_n=2):

        run_cline_list = []
        for run_key, run_cline in self.command_line_info.items():
            run_cline_list.append(run_cline)

        log_stream.info(' -----> Pooling requests ... ')
        exec_response_list = []
        if run_cline_list:
            with Pool(processes=process_n, maxtasksperchild=1) as process_pool:
                exec_response = process_pool.map(exec_process, run_cline_list, chunksize=1)
                process_pool.close()
                process_pool.join()
                exec_response_list.append(exec_response)
            log_stream.info(' -----> Pooling requests ... DONE')
        else:
            log_stream.info(' -----> Pooling requests ... SKIPPED. PREVIOUSLY DONE')

        return exec_response_list
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
