"""
Class Features

Name:          drv_runner_exec
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_args import sFileExec as sFileExec_Default
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_tags import oStaticTags as oStaticTags_Default
from hmc.default.lib_default_tags import oDynamicTags as oDynamicTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default
from hmc.default.lib_default_time import oDataTime as oDataTime_Default
from hmc.default.lib_default_namelist import oDataNamelist as oDataNamelist_Default
from hmc.default.lib_default_namelist import sFileNamelist as sFileNamelist_Default

from hmc.utils.lib_utils_apps_process import checkProcess, execProcess

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class RunnerExec
class HMC_Runner_Exec:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataVarStatic = {}
    oDataVarDynamic = {}
    oDataTime = {}

    oDataNML = {}
    sFileNML = None

    sFileExec = None
    sLineExec = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, oDataSettings=oDataSettings_Default,
                 oDataTags=oConfigTags_Default,
                 oDataVarStatic=oDataStatic_Default,
                 oDataVarDynamic=oDataDynamic_Default,
                 oDataTime=oDataTime_Default,
                 oDataNamelist=oDataNamelist_Default,
                 sFileNamelist=sFileNamelist_Default,
                 sFileNameExec=sFileExec_Default,
                 sPathNameExec='/'):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = oDataSettings
        self.oDataTags = oDataTags
        self.oDataVarStatic = oDataVarStatic
        self.oDataVarDynamic = oDataVarDynamic
        self.oDataTime = oDataTime

        self.oDataNML = oDataNamelist
        self.sFileNML = sFileNamelist

        self.sFileExec = sFileNameExec
        self.sPathExec = sPathNameExec
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compose command-line
    def runExecution(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Execute model run ... ')

        # Run executable application
        self.__runExecApp()

        # Info end
        oLogStream.info(' ---> Execute model run ... OK')
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run executable application
    def __runExecApp(self):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ----> Run model executable ... ')

        try:
            # Check process instance
            checkProcess(self.sFileExec, self.sPathExec)
            # Execute process instance
            sStdOut, sStdErr, iStdExit = execProcess(self.sFileExec, self.sPathExec)
            # Info end (ok)
            oLogStream.info(' ----> Run model executable ... OK')
        except BaseException:
            # Info end (fail)
            oLogStream.info(' ----> Run model executable ... FAILED!')
            Exc.getExc(' =====> ERROR: run model FAILED!', 1, 1)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
