"""
Class Features

Name:          drv_manager_configuration
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
import time
from os.path import join
from copy import deepcopy

from hmc.default.lib_default_args import sTimeFormat, sTimeType, sLoggerName
from hmc.default.lib_default_args import sFileBuilder as sFileBuilder_Default
from hmc.default.lib_default_args import sFileRunner as sFileRunner_Default
from hmc.default.lib_default_args import sFileFinalizer as sFileFinalizer_Default
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_tags import oStaticTags as oStaticTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default
from hmc.default.lib_default_time import oDataTime as oDataTime_Default

from hmc.settings.lib_settings import setRunSettings, setRunMode

from hmc.time.lib_time import getTimeRun, computeTimeCorrivation, computeTimeRestart, defineTimeSummary, updateTimeData

from hmc.utils.lib_utils_file_config import getFileConfig
from hmc.utils.lib_utils_apps_tags import setRunTags, updateRunTags
from hmc.utils.lib_utils_apps_geo import readGeoHeader
from hmc.utils.lib_utils_apps_time import getTimeNow, getTimeFrom, getTimeTo, getTimeSteps
from hmc.utils.lib_utils_op_string import defineString
from hmc.utils.lib_utils_op_dict import getDictValue

from hmc.debug.lib_debug import setFileName

from hmc.driver.data.drv_data_io_geo import DataGeo
from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class Config Parameter(s)
class HMC_Configuration_Params:

    # -------------------------------------------------------------------------------------
    # Global Variable(s)
    oDataSettings = {}
    oDataAttributes = {}
    oDataTags = {}

    oDataRunMode = {}
    sVarRunMode = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method class initialization
    def __init__(self, oDataSettings=oDataSettings_Default, oDataTags=oConfigTags_Default):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = oDataSettings
        self.oDataTags = oDataTags
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set run configuration
    def configParams(self, sAlgFolder=None):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Configure parameter(s) ... ')

        # Set run mode
        self.__setRunMode()

        # Set run tags
        self.__setRunTags()

        # Set run settings
        self.__setRunSettings()

        # Set run temporary file(s)
        self.__setRunTemp(sAlgFolder)

        # Info end
        oLogStream.info(' ---> Configure parameter(s) ... OK')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return variable(s)
        return self.oDataSettings, self.oDataTags, self.oDataRunMode
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set temporary file(s)
    def __setRunTemp(self, sAlgFolder=None):

        # Set temporary file(s)
        sFileBuilder = setFileName(sAlgFolder, sFileBuilder_Default)
        sFileRunner = setFileName(sAlgFolder, sFileRunner_Default)
        sFileFinalizer = setFileName(sAlgFolder, sFileFinalizer_Default)
        # Set settings attribute(s)
        setattr(self.oDataSettings, 'FileBuilder', sFileBuilder)
        setattr(self.oDataSettings, 'FileRunner', sFileRunner)
        setattr(self.oDataSettings, 'FileFinalizer', sFileFinalizer)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set run tags
    def __setRunTags(self):

        # Get ensemble mode
        oEnsMode = getDictValue(self.oDataSettings, ['ParamsInfo', 'Run_Params', 'RunMode', 'EnsMode'])

        # Apply mode to update running tag(s)
        if oEnsMode is True:
            setRunTags(oTags=self.oDataTags, oSettings=self.oDataSettings, oSkipTags=[self.sVarRunMode])
        else:
            setRunTags(oTags=self.oDataTags, oSettings=self.oDataSettings, oSkipTags=[])
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set run settings
    def __setRunSettings(self):
        setRunSettings(oTags=self.oDataTags, oSettings=self.oDataSettings)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set run mode
    def __setRunMode(self):

        # Get mode settings
        bEnsMode = getDictValue(self.oDataSettings, ['ParamsInfo', 'Run_Params', 'RunMode', 'EnsMode'])
        oEnsVar = getDictValue(self.oDataSettings, ['ParamsInfo', 'Run_Params', 'RunMode', 'EnsVar'])

        # Define mode instance(s)
        self.oDataRunMode = setRunMode(bEnsMode,
                                       sVarName=oEnsVar['VarName'],
                                       iVarMin=oEnsVar['VarMin'], iVarMax=oEnsVar['VarMax'],
                                       oVarStep=oEnsVar['VarStep'])
        self.sVarRunMode = oEnsVar['VarName']
    # -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class Config Variable(s)
class HMC_Configuration_Vars:

    # -------------------------------------------------------------------------------------
    # Global Variable(s)
    oDataVar = {}
    oDataVarStatic = {}
    oDataVarDynamic = {}
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method class initialization
    def __init__(self, oDataSettings=oDataSettings_Default, oDataTags=oConfigTags_Default):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = oDataSettings
        self.oDataTags = oDataTags

        self.oDataStatic = oDataStatic_Default
        self.oDataDynamic = oDataDynamic_Default
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set executable variable(s)
    def configVars(self):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Configure variable(s) ... ')

        # Get static variable(s)
        self.oDataVar = self.__getVarData('FileData')

        # Set static variable(s)
        self.oDataVarStatic = self.__setVarStatic()
        # Update static variable(s)
        self.oDataVarDynamic = self.__setVarDynamic()

        # Info end
        oLogStream.info(' ---> Configure variable(s) ... OK')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return variable(s)
        return self.oDataVarStatic, self.oDataVarDynamic
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------------------
    # Method to get static variable(s)
    def __getVarData(self, sDataAttribute):

        # Get static variable(s)
        if hasattr(self.oDataSettings, sDataAttribute):
            sFileName = getattr(self.oDataSettings, sDataAttribute)
        else:
            sFileName = None
            Exc.getExc(' =====> ERROR: file static variable(s) not found! Check your settings file!', 1, 1)

        [oFileVar, bFileVar] = getFileConfig(sFileName)

        return oFileVar

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set static variable(s)
    def __setVarStatic(self):
        oDataVarStatic = deepcopy(oDataStatic_Default)
        for sVarKey, oVarItem in oDataStatic_Default.items():
            if sVarKey in self.oDataVar:
                oVarWS = self.oDataVar[sVarKey]
                oDataVarStatic[sVarKey] = oVarWS
            else:
                pass
        return oDataVarStatic
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set dynamic variable(s)
    def __setVarDynamic(self):
        oDataVarDynamic = deepcopy(oDataDynamic_Default)
        for sVarKey, oVarItem in oDataDynamic_Default.items():
            if sVarKey in self.oDataVar:
                oVarWS = self.oDataVar[sVarKey]
                oDataVarDynamic[sVarKey] = oVarWS
            else:
                pass
        return oDataVarDynamic
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class Config Time
class HMC_Configuration_Time:

    # -------------------------------------------------------------------------------------
    # Global Variable(s)
    sTimeNow = None
    sTimeRun = None
    sTimeFrom = None
    sTimeTo = None
    sTimeRestart = None

    iTimeStepObs = None
    iTimeStepFor = None
    iTimeStepCheck = None
    iTimeDelta = None

    iTimeStepRestart = None
    sTimeHHRestart = None

    a1oTimeCorrivation = None
    iTimeCorrivation = None

    a1oTimeStep = {}
    a1oTimeCheck = {}
    a1oTimeSummary = {}

    oDataTime = {}
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method class initialization
    def __init__(self, oDataSettings=oDataSettings_Default,
                       oDataStatic=oDataStatic_Default,
                       oTimeArg=time.strftime(sTimeFormat, time.gmtime())):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = oDataSettings
        self.oDataGridded = oDataStatic['DataLand']['Gridded']
        self.sTimeArg = oTimeArg

        self.oFlagParams = oDataSettings['ParamsInfo']['HMC_Flag']
        self.oTimeParams = oDataSettings['ParamsInfo']['Time_Params']

        self.oDataTime = oDataTime_Default
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set times
    def configTime(self):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Configure time ... ')

        self.sTimeNow = self.oTimeParams['TimeNow']
        self.iTimeStepObs = self.oTimeParams['TimeStepObs']
        self.iTimeStepFor = self.oTimeParams['TimeStepFor']
        self.iTimeStepCheck = self.oTimeParams['TimeStepCheck']
        self.iTimeDelta = self.oTimeParams['TimeDelta']
        self.iTimeStepRestart = self.oTimeParams['TimeRestart']['RestartStep']
        self.sTimeHHRestart = self.oTimeParams['TimeRestart']['RestartHH']

        # Get time now
        self.__getTimeNow()
        # Get running time
        self.__getTimeRun()

        # Get corrivation time
        self.__computeCorrivationTime(oFileMap=['FileName'],
                                      oPathMap=['FilePath'],
                                      oVarMap=['FileVars', 'Terrain', 'Name'])

        # Get initial time step (taking care restart time condition)
        self.__getTimeFrom(oFlagMap=['Flag_Restart'])
        # Get ending time step (taking care corrivation time condition)
        self.__getTimeTo()

        # Compute period time steps
        self.__computeTimePeriodSteps()
        # Compute check time steps
        self.__computeTimeCheckSteps()
        # Compute summary time steps (OBS, FOR, CHECK and other information)
        self.__defineTimeSummary()

        # Update time Data
        self.__updateTimeData()

        # Info end
        oLogStream.info(' ---> Configure time ... OK')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return variable(s)
        return self.oDataTime
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to update time Data
    def __updateTimeData(self):

        # Updated value(s)
        oDictUpd = {'SimLength': len(self.a1oTimeSummary['TimeStep']),
                    'TimeNow': self.sTimeNow,
                    'TimeRun': self.sTimeRun,
                    'TimeStatus': self.sTimeRun,
                    'TimeRestart': self.sTimeRestart,
                    'TimeFrom': self.sTimeFrom,
                    'TimeTo': self.sTimeTo,
                    'TimeCorrivation': self.iTimeCorrivation,
                    'TimeSummary': self.a1oTimeSummary
        }

        # Pass updated dictionary
        self.oDataTime['DataTime'] = updateTimeData(deepcopy(self.oDataTime['DataTime']), oDictUpd)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get TimeNow
    def __getTimeNow(self):
        self.sTimeNow = getTimeNow(self.sTimeNow, sTimeType)[0]
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set time now
    def __getTimeRun(self):
        self.sTimeRun = getTimeRun(self.sTimeNow, self.sTimeArg, sTimeType)
        self.sTimeNow = self.sTimeRun
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute corrivation time
    def __computeCorrivationTime(self, oFileMap, oPathMap, oVarMap):

        # Get run information
        sFileName = getDictValue(self.oDataGridded, oFileMap)
        sFilePath = getDictValue(self.oDataGridded, oPathMap)
        sVarName = getDictValue(self.oDataGridded, oVarMap)

        # Get filename
        sFileNameGeneric = join(sFilePath, sFileName)
        oStaticTags = updateRunTags({'VarName': sVarName}, deepcopy(oStaticTags_Default))
        sFileName = defineString(sFileNameGeneric, oStaticTags)

        # Get Data
        oDataTerrain = DataGeo(sFileName).getDataGeo()
        [iRows, iCols, dGeoXMin, dGeoYMin, dGeoXStep, dGeoYStep, dNoData] = readGeoHeader(oDataTerrain.a1oGeoHeader)

        # Compute corrivation time
        iTc = computeTimeCorrivation(oDataTerrain.a2dGeoData,
                                     oDataTerrain.a2dGeoX, oDataTerrain.a2dGeoY, dGeoXStep, dGeoYStep)

        # Pass to global variable(s)
        self.iTimeCorrivation = iTc
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define time restart
    def __getTimeFrom(self, oFlagMap):

        # -------------------------------------------------------------------------------------
        # Restart flag
        iTimeFlagRestart = getDictValue(self.oFlagParams, oFlagMap)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Restart time condition
        if iTimeFlagRestart:

            # Select max time period steps
            if self.iTimeStepObs >= self.iTimeStepRestart:
                iTimePeriod = self.iTimeStepObs
            else:
                iTimePeriod = self.iTimeStepRestart

            # Evaluation of time restart and time from
            sTimeRestart = computeTimeRestart(self.sTimeRun, self.sTimeHHRestart, self.iTimeDelta, iTimePeriod)
            sTimeFrom = sTimeRestart

        else:

            # Evaluation of time restart and time from
            sTimeFrom = getTimeFrom(sTimeTo=self.sTimeRun, iTimeDelta=self.iTimeDelta, iTimeStep=self.iTimeStepObs)[0]
            sTimeRestart = sTimeFrom
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Pass to global variable(s)
        self.sTimeFrom = sTimeFrom
        self.sTimeRestart = sTimeRestart
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get time to
    def __getTimeTo(self):

        # -------------------------------------------------------------------------------------
        # Evaluation of time to
        sTimeTo = getTimeTo(sTimeFrom=self.sTimeRun, iTimeDelta=self.iTimeDelta,
                            iTimeStep=self.iTimeStepFor + self.iTimeCorrivation)[0]
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Evaluation of corrivation time period
        if self.iTimeCorrivation <= 0:
            self.iTimeCorrivation = 1
        else:
            pass

        sTimeCorrivationFrom = getTimeTo(sTimeFrom=sTimeTo, iTimeDelta=self.iTimeDelta,
                                         iTimeStep=-(self.iTimeCorrivation - 1))[0]

        sTimeCorrivationTo = getTimeTo(sTimeFrom=sTimeCorrivationFrom, iTimeDelta=self.iTimeDelta,
                                       iTimeStep=self.iTimeCorrivation - 1)[0]

        a1oTimeCorrivation = getTimeSteps(sTimeFrom=sTimeCorrivationFrom, sTimeTo=sTimeCorrivationTo, iTimeDelta=self.iTimeDelta)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Pass to global variable(s)
        self.sTimeTo = sTimeCorrivationTo
        self.a1oTimeCorrivation = a1oTimeCorrivation
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute period time steps
    def __computeTimePeriodSteps(self):

        # -------------------------------------------------------------------------------------
        # Evaluation of time steps period
        a1oTimeStep = getTimeSteps(sTimeFrom=self.sTimeFrom, sTimeTo=self.sTimeTo, iTimeDelta=self.iTimeDelta)
        self.a1oTimeStep = a1oTimeStep
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute check time steps
    def __computeTimeCheckSteps(self):

        # -------------------------------------------------------------------------------------
        # Evaluation of time steps Data check
        if self.iTimeStepCheck > 0:
            a1oTimeCheck = getTimeSteps(sTimeTo=self.sTimeRun, iTimeDelta=self.iTimeDelta,
                                        iTimeStep=self.iTimeStepCheck - 1)
        elif self.iTimeStepCheck == 0:
            a1oTimeCheck = [self.sTimeRun]
        elif self.iTimeStepCheck < 0:
            # Exit status with warning
            Exc.getExc(' =====> WARNING: Data check steps are set less than 0! Update to 0', 2, 1)
            a1oTimeCheck = [self.sTimeRun]
            self.iTimeStepCheck = 0
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Pass to global variable(s)
        self.a1oTimeCheck = a1oTimeCheck
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define summary time steps (OBS, FOR, CHECK and other information)
    def __defineTimeSummary(self):

        # -------------------------------------------------------------------------------------
        # Define time summary workspace
        a1oTimeSummary = defineTimeSummary(self.sTimeRun,
                                           self.oDataTime['DataTime']['TimeSummary'],
                                           self.a1oTimeStep, self.a1oTimeCheck, self.a1oTimeCorrivation)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Update generic time information using Data summary
        self.sTimeRun = a1oTimeSummary['TimeStep'][0]
        self.sTimeStatus = a1oTimeSummary['TimeStep'][0]
        self.sTimeRestart = a1oTimeSummary['TimeStep'][0]
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Pass to global variable(s)
        self.a1oTimeSummary = a1oTimeSummary
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
