"""
Class Features

Name:          drv_builder_datadynamic_time
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
from copy import deepcopy
from numpy import linspace, append, int32, full, arange, min, max

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_time import oDataTime as oDataTime_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default

from hmc.time.lib_time import updateTimeData

from hmc.utils.lib_utils_op_dict import checkDictKeys
from hmc.utils.lib_utils_op_list import enumListBool, getListElement

from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class Builder DataDynamic Time
class HMC_Builder_DataDynamic_Time:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataTime = {}
    oDataVarDynamic = {}

    oSummaryTime = {}

    a1oRunTotalType = []
    a1iRunTotalIndex = -9999
    a1bRunTotalIndex = False
    a1bExtraTotalIndex = False

    iRunLength = None

    dDataFGPerc = 0.0
    dDataFPPerc = 0.0
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, oDataSettings=oDataSettings_Default, oDataTags=oConfigTags_Default,
                 oDataVarDynamic=oDataDynamic_Default,
                 oDataTime=oDataTime_Default):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = oDataSettings
        self.oDataTags = oDataTags
        self.oDataTime = oDataTime
        self.oDataVarDynamic = oDataVarDynamic

        self.oSummaryTime = oDataTime['DataTime']['TimeSummary']
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute time information
    def computeTime(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Get Data dynamic time ... ')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Update time index
        self.__updateTimeIndex()

        # Update time information
        self.__updateTimeSummary()

        # Update time Data
        self.__updateTimeData()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Info end (ok)
        oLogStream.info(' ---> Get Data dynamic time ... OK')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return variable(s)
        return self.oDataTime, self.oDataVarDynamic
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to update time Data
    def __updateTimeData(self):

        # Check on simulation length
        if self.iRunLength < 0:
            Exc.getExc(' =====> ERROR: simulation steps are less than zero! Check your model settings!', 1, 1)
        elif self.iRunLength == 0:
            Exc.getExc(' =====> WARNING: simulation steps are equal to zero! Check your model settings!', 2, 1)
        else:
            pass

        # Updated workspace value(s)
        oDictUpd = {'SimLength': self.iRunLength,
                    'TimeNow': self.oDataTime['DataTime']['TimeNow'],
                    'TimeRun': self.oDataTime['DataTime']['TimeRun'],
                    'TimeStatus': self.oDataTime['DataTime']['TimeStatus'],
                    'TimeRestart': self.oDataTime['DataTime']['TimeRestart'],
                    'TimeFrom': self.oSummaryTime['TimeStep'][0],
                    'TimeTo': self.oSummaryTime['TimeStep'][-1],
                    'TimeCorrivation': self.oDataTime['DataTime']['TimeCorrivation'],
                    'TimeSummary': self.oSummaryTime}

        # Updated time dictionary to global workspace
        self.oDataTime['DataTime'] = updateTimeData(deepcopy(self.oDataTime['DataTime']), oDictUpd)

        # Updated Data dynamic dictionary to global workspace
        self.oDataVarDynamic['DataAnalysis']['Gridded']['ForcingDataThr'] = self.dDataFGPerc
        self.oDataVarDynamic['DataAnalysis']['Point']['ForcingDataThr'] = self.dDataFPPerc

        # Info time
        oLogStream.info(' ----> Simulation info ... ')
        oLogStream.info(' ----> Simulation steps: ' + str(self.oDataTime['DataTime']['SimLength']))
        oLogStream.info(' ----> Simulation time restart: ' + str(self.oDataTime['DataTime']['TimeRestart']))
        oLogStream.info(' ----> Simulation time start: ' + str(self.oDataTime['DataTime']['TimeRestart']))
        oLogStream.info(' ----> Simulation time run: ' + str(self.oDataTime['DataTime']['TimeRun']))
        oLogStream.info(' ----> Simulation time now: ' + str(self.oDataTime['DataTime']['TimeNow']))
        oLogStream.info(' ----> Simulation forcing gridded data available: ' + str(self.dDataFGPerc) + ' [%]')
        oLogStream.info(' ----> Simulation forcing point data available: ' + str(self.dDataFPPerc) + ' [%]')
        oLogStream.info(' ----> Simulation info ... OK')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to update time information
    def __updateTimeSummary(self):

        # Get information
        oSummaryTime = deepcopy(self.oSummaryTime)
        a1oRunTotalType = self.a1oRunTotalType
        a1iRunTotalIndex = self.a1iRunTotalIndex
        a1bRunTotalIndex = self.a1bRunTotalIndex
        a1bExtraTotalIndex = self.a1bExtraTotalIndex

        # Time steps and Data type updates
        oSummaryTime['TimeStep'] = getListElement(self.oSummaryTime['TimeStep'], a1iRunTotalIndex)
        oSummaryTime['DataType'] = a1oRunTotalType

        # Data dynamic updates
        oSummaryTime['DataForcingGridded'] = getListElement(self.oSummaryTime['DataForcingGridded'],
                                                            a1iRunTotalIndex)
        oSummaryTime['DataForcingPoint'] = getListElement(self.oSummaryTime['DataForcingPoint'],
                                                          a1iRunTotalIndex)
        oSummaryTime['DataForcingTimeSeries'] = getListElement(self.oSummaryTime['DataForcingTimeSeries'],
                                                               a1iRunTotalIndex)
        oSummaryTime['DataUpdatingGridded'] = getListElement(self.oSummaryTime['DataUpdatingGridded'],
                                                             a1iRunTotalIndex)
        oSummaryTime['DataUpdatingPoint'] = getListElement(self.oSummaryTime['DataUpdatingPoint'],
                                                           a1iRunTotalIndex)
        oSummaryTime['DataRestartGridded'] = getListElement(self.oSummaryTime['DataRestartGridded'],
                                                            a1iRunTotalIndex)
        oSummaryTime['DataRestartPoint'] = getListElement(self.oSummaryTime['DataRestartPoint'],
                                                          a1iRunTotalIndex)
        # Data check updates
        oSummaryTime['DataCheck'] = getListElement(self.oSummaryTime['DataCheck'],
                                                   a1iRunTotalIndex)
        # Data extra updates
        oSummaryTime['DataExtra'] = a1bExtraTotalIndex

        # Save variable to global workspace
        self.oSummaryTime = oSummaryTime

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to check time summary workspace
    def __updateTimeIndex(self):

        # Get forcing steps indexes and tags (point and gridded)
        [a1iForcingStepIndexGT, a1iForcingStepIndexGF] = enumListBool(self.oSummaryTime['DataForcingGridded'])
        a1iForcingStepIndexGT_Upd = arange(min(a1iForcingStepIndexGT), max(a1iForcingStepIndexGT) + 1, 1)
        a1oForcingStepTypeG = getListElement(self.oSummaryTime['DataType'], a1iForcingStepIndexGT_Upd)

        dRunForcingAvailableG = checkDictKeys(getListElement(self.oSummaryTime['DataForcingGridded'],
                                                             a1iForcingStepIndexGT_Upd), 'gridded forcing step(s)')[1]

        [a1iForcingStepIndexPT, a1iForcingStepIndexPF] = enumListBool(self.oSummaryTime['DataForcingPoint'])
        a1iForcingStepIndexPT_Upd = arange(min(a1iForcingStepIndexPT), max(a1iForcingStepIndexPT) + 1, 1)
        a1oForcingStepTypeP = getListElement(self.oSummaryTime['DataType'], a1iForcingStepIndexPT_Upd)

        dRunForcingAvailableP = checkDictKeys(getListElement(self.oSummaryTime['DataForcingPoint'],
                                                             a1iForcingStepIndexPT_Upd), 'point forcing step(s)')[1]

        # Get extra steps indexes and tags
        [a1iExtraStepIndexT, a1iExtraStepIndexF] = enumListBool(self.oSummaryTime['DataExtra'])
        a1iExtraStepIndexT_Upd = arange(min(a1iExtraStepIndexT), max(a1iExtraStepIndexT) + 1, 1)
        a1oExtraStepType = getListElement(self.oSummaryTime['DataType'], a1iExtraStepIndexT_Upd)

        # Get check steps indexes and tags
        [a1iCheckStepIndexT, a1iCheckStepIndexF] = enumListBool(self.oSummaryTime['DataCheck'])
        a1iCheckStepIndexT_Upd = arange(min(a1iCheckStepIndexT), max(a1iCheckStepIndexT) + 1, 1)
        a1oCheckStepType = getListElement(self.oSummaryTime['DataType'], a1iCheckStepIndexT_Upd)

        # Define updated indexes
        a1iRunExtraIndex = int32(linspace(max(a1iForcingStepIndexGT_Upd) + 1,
                                          max(a1iForcingStepIndexGT_Upd) + a1iExtraStepIndexT_Upd.size,
                                          num=a1iExtraStepIndexT_Upd.size, endpoint=True))
        a1iRunForcingIndexG = int32(a1iForcingStepIndexGT_Upd)
        a1iRunTotalIndex = int32(append(a1iRunForcingIndexG, a1iRunExtraIndex))

        # Define boolean run index (true=forcing steps, false=extra steps)
        a1bRunTotalIndex = full((len(a1iRunTotalIndex)), False, dtype=bool)
        a1bRunTotalIndex[a1iRunForcingIndexG] = True
        a1bRunTotalIndex[a1iRunExtraIndex] = False

        # Define boolean extra index (false=forcing steps, true=extra steps)
        a1bExtraTotalIndex = full((len(a1iRunTotalIndex)), False, dtype=bool)
        a1bExtraTotalIndex[a1iRunExtraIndex] = True

        # Define list run type (OBS/FOR/CORR)
        a1oRunTotalType = a1oForcingStepTypeG + a1oExtraStepType

        # Define simulation length (based only on forcing time steps)
        iRunLength = a1iForcingStepIndexGT_Upd.size

        # Global variable(s)
        self.a1oRunTotalType = a1oRunTotalType
        self.a1iRunTotalIndex = a1iRunTotalIndex
        self.a1bRunTotalIndex = a1bRunTotalIndex
        self.a1bExtraTotalIndex = a1bExtraTotalIndex

        self.iRunLength = iRunLength

        self.dDataFGPerc = dRunForcingAvailableG
        self.dDataFPPerc = dRunForcingAvailableP

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
