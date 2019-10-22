"""
Class Features

Name:          cpl_manager
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

######################################################################################
# Logging
import logging
from copy import deepcopy

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default

from hmc.default.lib_default_args import sFileExec as sFileExec_Default

from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default
from hmc.default.lib_default_namelist import oDataNamelist as oDataNamelist_Default
from hmc.default.lib_default_namelist import sFileNamelist as sFileNamelist_Default
from hmc.default.lib_default_time import oDataTime as oDataTime_Default

from hmc.driver.builder.drv_builder_info import HMC_Builder_Info
from hmc.driver.builder.drv_builder_namelist import HMC_Builder_Namelist
from hmc.driver.builder.drv_builder_datastatic import HMC_Builder_DataStatic

from hmc.driver.builder.drv_builder_datadynamic_restart import HMC_Builder_DataDynamic_Restart
from hmc.driver.builder.drv_builder_datadynamic_forcing_gridded import HMC_Builder_DataDynamic_Forcing_Gridded
from hmc.driver.builder.drv_builder_datadynamic_forcing_point import HMC_Builder_DataDynamic_Forcing_Point
from hmc.driver.builder.drv_builder_datadynamic_forcing_timeseries import HMC_Builder_DataDynamic_Forcing_TimeSeries
from hmc.driver.builder.drv_builder_datadynamic_updating_gridded import HMC_Builder_DataDynamic_Updating_Gridded
from hmc.driver.builder.drv_builder_datadynamic_time import HMC_Builder_DataDynamic_Time

from hmc.driver.runner.drv_runner_info import HMC_Runner_Info
from hmc.driver.runner.drv_runner_exec import HMC_Runner_Exec

from hmc.driver.finalizer.drv_finalizer_data import HMC_Finalizer_Data
from hmc.driver.finalizer.drv_finalizer_timeseries import HMC_Finalizer_TimeSeries

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
from hmc.debug.lib_debug import saveWorkspace, restoreWorkspace
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class run manager coupler
class cpl_manager:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataVarStatic = {}
    oDataVarDynamic = {}
    oDataNamelist = {}
    oDataTime = {}
    sFileNamelist = None

    sFileNameExec = None
    sPathNameExec = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, oDataSettings=oDataSettings_Default,
                 oDataTags=oConfigTags_Default,
                 oDataVarStatic=oDataStatic_Default,
                 oDataVarDyn=oDataDynamic_Default,
                 oDataNamelist=oDataNamelist_Default,
                 oDataTime=oDataTime_Default,
                 sFileNamelist=sFileNamelist_Default,
                 sFileNameExec=sFileExec_Default):
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get information
        self.oDataSettings = oDataSettings
        self.oDataTags = oDataTags
        self.oDataVarStatic = oDataVarStatic
        self.oDataVarDynamic = oDataVarDyn
        self.oDataTime = oDataTime

        self.oDataNamelist = oDataNamelist
        self.sFileNamelist = sFileNamelist
        self.sFileNameExec = sFileNameExec
        self.sPathNameExec = None

        # Store to execute ensemble mode
        self.oDataSettings_VAR = oDataSettings
        self.oDataTags_VAR = oDataTags
        self.oDataVarStatic_VAR = oDataVarStatic
        self.oDataVarDynamic_VAR = oDataVarDyn
        self.oDataTime_VAR = oDataTime
        self.oDataNamelist_VAR = oDataNamelist
        self.sFileNamelist_VAR = sFileNamelist
        self.sFileNameExec_VAR = sFileNameExec
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to builder instance
    def Builder(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' --> BuilderInstance [RunType: ' + sRunMode + '] ... ')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Initialize builder for settings
        oDrv_Builder_Info = HMC_Builder_Info(oDataSettings=deepcopy(self.oDataSettings_VAR),
                                             oDataTags=deepcopy(self.oDataTags_VAR),
                                             oDataVarStatic=deepcopy(self.oDataVarStatic_VAR),
                                             oDataVarDynamic=deepcopy(self.oDataVarDynamic_VAR),
                                             oDataTime=self.oDataTime)
        # Method to update settings
        [self.oDataSettings, self.oDataTags,
         self.oDataVarStatic, self.oDataVarDynamic] = oDrv_Builder_Info.updateInfo(sRunMode, oRunArgs)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Initialize builder for data static
        oDrv_Builder_DataStatic = HMC_Builder_DataStatic(
            oDataSettings=self.oDataSettings,
            oDataTags=self.oDataTags,
            oDataVarStatic=self.oDataVarStatic)

        # Method to get and set static file(s)
        self.oDataVarStatic = oDrv_Builder_DataStatic.getFile()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Initialize builder for data dynamic restart gridded/point
        oDrv_Builder_DataDynamic_Restart = HMC_Builder_DataDynamic_Restart(
            oDataSettings=self.oDataSettings,
            oDataTags=self.oDataTags,
            oDataVarStatic=self.oDataVarStatic,
            oDataVarDynamic=self.oDataVarDynamic,
            oDataTime=self.oDataTime)
        # Method to get data dynamic restart gridded/point file(s)
        self.oDataTime = oDrv_Builder_DataDynamic_Restart.getFile(sRunMode, oRunArgs)

        # Initialize builder for data dynamic forcing point
        oDrv_Builder_DataDynamic_Forcing_Point = HMC_Builder_DataDynamic_Forcing_Point(
            oDataSettings=self.oDataSettings,
            oDataTags=self.oDataTags,
            oDataVarStatic=self.oDataVarStatic,
            oDataVarDynamic=self.oDataVarDynamic,
            oDataTime=self.oDataTime)

        # Method to get data dynamic forcing point file(s)
        self.oDataTime = oDrv_Builder_DataDynamic_Forcing_Point.getFile(sRunMode, oRunArgs)

        # Initialize builder for data dynamic forcing timeseries
        oDrv_Builder_DataDynamic_Forcing_TimeSeries = HMC_Builder_DataDynamic_Forcing_TimeSeries(
            oDataSettings=self.oDataSettings,
            oDataTags=self.oDataTags,
            oDataVarStatic=self.oDataVarStatic,
            oDataVarDynamic=self.oDataVarDynamic,
            oDataTime=self.oDataTime)

        # Method to get data dynamic forcing timeseries file(s)
        self.oDataTime = oDrv_Builder_DataDynamic_Forcing_TimeSeries.getFile(sRunMode, oRunArgs)

        # Initialize builder for data dynamic forcing gridded
        oDrv_Builder_DataDynamic_Forcing_Gridded = HMC_Builder_DataDynamic_Forcing_Gridded(
            oDataSettings=self.oDataSettings,
            oDataTags=self.oDataTags,
            oDataVarStatic=self.oDataVarStatic,
            oDataVarDynamic=self.oDataVarDynamic,
            oDataTime=self.oDataTime)

        # Method to get data dynamic forcing gridded file(s)
        self.oDataTime = oDrv_Builder_DataDynamic_Forcing_Gridded.getFile(sRunMode, oRunArgs)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Initialize builder for data dynamic updating gridded
        oDrv_Builder_DataDynamic_Updating_Gridded = HMC_Builder_DataDynamic_Updating_Gridded(
            oDataSettings=self.oDataSettings,
            oDataTags=self.oDataTags,
            oDataVarStatic=self.oDataVarStatic,
            oDataVarDynamic=self.oDataVarDynamic,
            oDataTime=self.oDataTime)

        # Method to get data dynamic updating gridded file(s)
        self.oDataTime = oDrv_Builder_DataDynamic_Updating_Gridded.getFile(sRunMode, oRunArgs)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Initialize builder for data dynamic time
        oDrv_Builder_DataDynamic_Time = HMC_Builder_DataDynamic_Time(oDataSettings=self.oDataSettings,
                                                                     oDataTags=self.oDataTags,
                                                                     oDataVarDynamic=self.oDataVarDynamic,
                                                                     oDataTime=self.oDataTime)

        # Method to get and update time and data dynamic
        [self.oDataTime, self.oDataVarDynamic] = oDrv_Builder_DataDynamic_Time.computeTime(sRunMode, oRunArgs)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Initialize builder for namelist file
        oDrv_Builder_Namelist = HMC_Builder_Namelist(oDataSettings=self.oDataSettings,
                                                     oDataTags=self.oDataTags,
                                                     oDataVarStatic=self.oDataVarStatic,
                                                     oDataVarDynamic=self.oDataVarDynamic,
                                                     oDataTime=self.oDataTime,
                                                     oDataNamelist=deepcopy(self.oDataNamelist_VAR),
                                                     sFileNamelist=deepcopy(self.sFileNamelist_VAR))
        # Method to write namelist file
        [self.sFileNamelist, self.oDataNamelist] = oDrv_Builder_Namelist.writeNML(sRunMode, oRunArgs)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Info end
        oLogStream.info(' --> BuilderInstance [RunType: ' + sRunMode + '] ... OK')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Debug (save builder workspace)
        saveWorkspace(self.oDataSettings.FileBuilder,
                      oDataSettings=self.oDataSettings,
                      oDataTags=self.oDataTags, oDataTime=self.oDataTime,
                      oDataNamelist=self.oDataNamelist, sFileNamelist=self.sFileNamelist,
                      oDataVarStatic=self.oDataVarStatic, oDataVarDynamic=self.oDataVarDynamic)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to runner instance
    def Runner(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Debug (restore builder workspace)
        self.__dict__.update(restoreWorkspace(self.oDataSettings.FileBuilder))
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' --> RunnerInstance [RunType: ' + sRunMode + '] ... ')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Initialize runner for info Data
        oDrv_Runner_Info = HMC_Runner_Info(oDataSettings=self.oDataSettings,
                                           oDataTags=self.oDataTags,
                                           oDataVarStatic=self.oDataVarStatic,
                                           oDataVarDynamic=self.oDataVarDynamic,
                                           oDataTime=self.oDataTime,
                                           oDataNamelist=self.oDataNamelist,
                                           sFileNamelist=self.sFileNamelist,
                                           sFileNameExec=deepcopy(self.sFileNameExec)
                                           )
        # Method to collect information
        self.sFileNameExec, self.sPathNameExec = oDrv_Runner_Info.collectInfo(sRunMode, oRunArgs)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Initialize runner for info Data
        oDrv_Runner_Exec = HMC_Runner_Exec(oDataSettings=self.oDataSettings,
                                           oDataTags=self.oDataTags,
                                           oDataVarStatic=self.oDataVarStatic,
                                           oDataVarDynamic=self.oDataVarDynamic,
                                           oDataTime=self.oDataTime,
                                           oDataNamelist=self.oDataNamelist,
                                           sFileNamelist=self.sFileNamelist,
                                           sFileNameExec=self.sFileNameExec,
                                           sPathNameExec=self.sPathNameExec)
        # Method to collect information
        oDrv_Runner_Exec.runExecution(sRunMode, oRunArgs)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Info end
        oLogStream.info(' --> RunnerInstance [RunType: ' + sRunMode + '] ... OK')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Debug (save runner workspace)
        saveWorkspace(self.oDataSettings.FileRunner,
                      oDataSettings=self.oDataSettings,
                      oDataTags=self.oDataTags, oDataTime=self.oDataTime,
                      oDataNamelist=self.oDataNamelist, sFileNamelist=self.sFileNamelist,
                      oDataVarStatic=self.oDataVarStatic, oDataVarDynamic=self.oDataVarDynamic,
                      sFileNameExec=self.sFileNameExec, sPathNameExec=self.sPathNameExec)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to finalizer instance
    def Finalizer(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Debug (restore runner workspace)
        self.__dict__.update(restoreWorkspace(self.oDataSettings.FileRunner))
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' --> FinalizerInstance [RunType: ' + sRunMode + '] ... ')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Initialize finalizer to collect Data
        oDrv_Finalizer_Data = HMC_Finalizer_Data(oDataSettings=self.oDataSettings,
                                                 oDataTags=self.oDataTags,
                                                 oDataVarStatic=self.oDataVarStatic,
                                                 oDataVarDynamic=self.oDataVarDynamic,
                                                 oDataTime=self.oDataTime)
        # Method to collect Data
        oDrv_Finalizer_Data.collectData(sRunMode, oRunArgs)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Initialize finalizer to collect Data
        oDrv_Finalizer_TimeSeries = HMC_Finalizer_TimeSeries(oDataSettings=self.oDataSettings,
                                                             oDataTags=self.oDataTags,
                                                             oDataVarStatic=self.oDataVarStatic,
                                                             oDataVarDynamic=self.oDataVarDynamic,
                                                             oDataTime=self.oDataTime)
        # Method to collect Data
        oDrv_Finalizer_TimeSeries.writeData(sRunMode, oRunArgs)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' --> Finalizer Instance [RunType: ' + sRunMode + '] ... OK')
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
