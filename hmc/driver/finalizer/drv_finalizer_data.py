"""
Class Features

Name:          drv_finalizer_data
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
from os.path import join, split, exists
from copy import deepcopy

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_tags import oStaticTags as oStaticTags_Default
from hmc.default.lib_default_tags import oDynamicTags as oDynamicTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default
from hmc.default.lib_default_time import oDataTime as oDataTime_Default

from hmc.utils.lib_utils_apps_tags import updateRunTags, mergeRunTags

from hmc.utils.lib_utils_op_system import copyFile, createFolder
from hmc.utils.lib_utils_op_string import defineString

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class FinalizerData
class HMC_Finalizer_Data:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataVarStatic = {}
    oDataVarDynamic = {}

    sTimeNow = None
    oDataTime = {}

    oDataOutcomeGridded = None
    oDataOutcomePoint = None
    oDataOutcomeTimeSeries = None

    oDataObsPoint = None

    oDataStateGridded = None
    oDataStatePoint = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, oDataSettings=oDataSettings_Default,
                 oDataTags=oConfigTags_Default,
                 oDataVarStatic=oDataStatic_Default,
                 oDataVarDynamic=oDataDynamic_Default,
                 oDataTime=oDataTime_Default):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = oDataSettings
        self.oDataTags = oDataTags
        self.oDataVarStatic = oDataVarStatic
        self.oDataVarDynamic = oDataVarDynamic
        self.oDataTime = oDataTime['DataTime']['TimeSummary']
        self.sTimeNow = oDataTime['DataTime']['TimeNow']

        self.oDataOutcomeGridded = oDataVarDynamic['DataOutcome']['Gridded']
        self.oDataOutcomePoint = oDataVarDynamic['DataOutcome']['Point']
        self.oDataOutcomeTimeSeries = oDataVarDynamic['DataOutcome']['TimeSeries']

        self.oDataObsPoint = oDataVarDynamic['DataObs']['Point']

        self.oDataStateGridded = oDataVarDynamic['DataState']['Gridded']
        self.oDataStatePoint = oDataVarDynamic['DataState']['Point']
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect data
    def collectData(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Collect model results ... ')

        # Collect data point
        self.__collectDataPoint(sRunMode, oRunArgs)

        # Collect data gridded
        self.__collectDataGridded(sRunMode, oRunArgs)

        # Collect data timeseries
        self.__collectDataTimeSeries(sRunMode, oRunArgs)

        # Info end
        oLogStream.info(' ---> Collect model results ... OK')
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect data timeseries
    def __collectDataTimeSeries(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Get variable information
        oDataOutcome = self.oDataOutcomeTimeSeries

        # Get time now
        sTimeNow = self.sTimeNow

        # Create Data archive
        oDataArchive = {'Outcome': oDataOutcome}
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Cycle(s) over Data archive(s)
        for sArchiveKey, oArchiveValue in iter(oDataArchive.items()):

            # -------------------------------------------------------------------------------------
            # Get Data variable(s)
            oDataVars = oArchiveValue['FileVars']['ARCHIVE']['VarName']
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Cycle(s) over variable(s)
            for sDataKey, oDataValue in iter(oDataVars.items()):

                # -------------------------------------------------------------------------------------
                # Info variable start
                oLogStream.info(' ----> Get variable ' + sDataKey + ' - Type: ' + sArchiveKey + ' timeseries data ... ')
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Get time reference (for time-series data is time now)
                sDataTime = sTimeNow

                # Define tags and filename LOAD
                oDynamicTags_LOAD = updateRunTags({'Year': sDataTime[0:4],
                                                   'Month': sDataTime[4:6], 'Day': sDataTime[6:8],
                                                   'Hour': sDataTime[8:10], 'Minute': sDataTime[10:12],
                                                   'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                  deepcopy(oDynamicTags_Default))
                oTagsUpd_LOAD = mergeRunTags(oDynamicTags_LOAD, self.oDataTags)

                sFilePath_LOAD = defineString(deepcopy(oArchiveValue['FilePath']), oTagsUpd_LOAD)
                sFileName_LOAD = defineString(deepcopy(oArchiveValue['FileName']), oTagsUpd_LOAD)

                sFile_LOAD = join(sFilePath_LOAD, sFileName_LOAD)
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Check file availability
                if exists(sFile_LOAD):

                    # -------------------------------------------------------------------------------------
                    # Define tags and filename SAVE
                    oDynamicTags_SAVE = updateRunTags({'Year': sTimeNow[0:4],
                                                       'Month': sTimeNow[4:6], 'Day': sTimeNow[6:8],
                                                       'Hour': sTimeNow[8:10], 'Minute': sTimeNow[10:12],
                                                       'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                      deepcopy(oDynamicTags_Default))
                    oTagsUpd_SAVE = mergeRunTags(oDynamicTags_SAVE, self.oDataTags)

                    sFilePath_SAVE = defineString(deepcopy(oDataValue['FilePath']), oTagsUpd_SAVE)
                    sFileName_SAVE = defineString(deepcopy(oDataValue['FileName']), oTagsUpd_LOAD)

                    sFile_SAVE = join(sFilePath_SAVE, sFileName_SAVE)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Create destination folder
                    createFolder(split(sFile_SAVE)[0])

                    # Archive file in a new folder
                    copyFile(sFile_LOAD, sFile_SAVE)
                    # -------------------------------------------------------------------------------------
                else:
                    # -------------------------------------------------------------------------------------
                    # Info variable end
                    Exc.getExc(
                        ' =====> WARNING: TimeStep: ' + sDataTime + ' File: ' + sFile_LOAD +
                        ' is not available! Check run data!', 2, 1)
                    # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Info variable end
                oLogStream.info(' ----> Get variable ' + sDataKey + ' - Type: ' + sArchiveKey +
                                ' timeseries data ... OK')
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect data point
    def __collectDataPoint(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Get variable information
        oDataOutcome = self.oDataOutcomePoint
        oDataState = self.oDataStatePoint
        oDataObs = self.oDataObsPoint

        # Get time now
        sTimeNow = self.sTimeNow

        # Create Data archive
        oDataArchive = {'Obs': oDataObs, 'Outcome': oDataOutcome, 'State': oDataState}
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Cycle(s) over Data archive(s)
        for sArchiveKey, oArchiveValue in iter(oDataArchive.items()):

            # -------------------------------------------------------------------------------------
            # Get Data variable(s)
            oDataVars = oArchiveValue['FileVars']['ARCHIVE']['VarName']
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Cycle(s) over variable(s)
            for sDataKey, oDataValue in iter(oDataVars.items()):

                # -------------------------------------------------------------------------------------
                # Info variable start
                oLogStream.info(' ----> Get variable ' + sDataKey + ' - Type: ' + sArchiveKey + ' point data ... ')
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Cycle(s) over time(s)
                for iDataTime, (sDataTime, sDataType) in enumerate(
                        zip(self.oDataTime['TimeStep'], self.oDataTime['DataType'])):

                    # -------------------------------------------------------------------------------------
                    # Define tags and filename LOAD
                    oDynamicTags_LOAD = updateRunTags({'Year': sDataTime[0:4],
                                                       'Month': sDataTime[4:6], 'Day': sDataTime[6:8],
                                                       'Hour': sDataTime[8:10], 'Minute': sDataTime[10:12],
                                                       'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                      deepcopy(oDynamicTags_Default))
                    oTagsUpd_LOAD = mergeRunTags(oDynamicTags_LOAD, self.oDataTags)

                    sFilePath_LOAD = defineString(deepcopy(oArchiveValue['FilePath']), oTagsUpd_LOAD)
                    sFileName_LOAD = defineString(deepcopy(oArchiveValue['FileName']), oTagsUpd_LOAD)

                    sFile_LOAD = join(sFilePath_LOAD, sFileName_LOAD)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check file availability
                    if exists(sFile_LOAD):

                        # -------------------------------------------------------------------------------------
                        # Define tags and filename SAVE
                        oDynamicTags_SAVE = updateRunTags({'Year': sTimeNow[0:4],
                                                           'Month': sTimeNow[4:6], 'Day': sTimeNow[6:8],
                                                           'Hour': sTimeNow[8:10], 'Minute': sTimeNow[10:12],
                                                           'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                          deepcopy(oDynamicTags_Default))
                        oTagsUpd_SAVE = mergeRunTags(oDynamicTags_SAVE, self.oDataTags)

                        sFilePath_SAVE = defineString(deepcopy(oDataValue['FilePath']), oTagsUpd_SAVE)
                        sFileName_SAVE = defineString(deepcopy(oDataValue['FileName']), oTagsUpd_LOAD)

                        sFile_SAVE = join(sFilePath_SAVE, sFileName_SAVE)
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Create destination folder
                        createFolder(split(sFile_SAVE)[0])

                        # Archive file in a new folder
                        copyFile(sFile_LOAD, sFile_SAVE)
                        # -------------------------------------------------------------------------------------
                    else:
                        # -------------------------------------------------------------------------------------
                        # Info variable end
                        Exc.getExc(
                            ' =====> WARNING: TimeStep: ' + sDataTime + ' TimeType: ' + sDataType +
                            ' File: ' + sFile_LOAD + ' is not available! Check run data!', 2, 1)
                        # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Info variable end
                oLogStream.info(' ----> Get variable ' + sDataKey + ' - Type: ' + sArchiveKey + ' point data ... OK')
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect data gridded
    def __collectDataGridded(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Get variable information
        oDataOutcome = self.oDataOutcomeGridded
        oDataState = self.oDataStateGridded
        # Get time now
        sTimeNow = self.sTimeNow

        # Create Data archive
        oDataArchive = {'Outcome': oDataOutcome, 'State': oDataState}
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Cycle(s) over Data archive(s)
        for sArchiveKey, oArchiveValue in iter(oDataArchive.items()):

            # -------------------------------------------------------------------------------------
            # Get Data variable(s)
            oDataVars = oArchiveValue['FileVars']['ARCHIVE']['VarName']
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Cycle(s) over variable(s)
            for sDataKey, oDataValue in iter(oDataVars.items()):

                # -------------------------------------------------------------------------------------
                # Info variable start
                oLogStream.info(' ----> Get variable ' + sDataKey + ' - Type: ' + sArchiveKey + ' gridded data ... ')
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Cycle(s) over time(s)
                for iDataTime, (sDataTime, sDataType) in enumerate(
                        zip(self.oDataTime['TimeStep'], self.oDataTime['DataType'])):

                    # -------------------------------------------------------------------------------------
                    # Define tags and filename LOAD
                    oDynamicTags_LOAD = updateRunTags({'Year': sDataTime[0:4],
                                                       'Month': sDataTime[4:6], 'Day': sDataTime[6:8],
                                                       'Hour': sDataTime[8:10], 'Minute': sDataTime[10:12],
                                                       'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                      deepcopy(oDynamicTags_Default))
                    oTagsUpd_LOAD = mergeRunTags(oDynamicTags_LOAD, self.oDataTags)

                    sFilePath_LOAD = defineString(deepcopy(oArchiveValue['FilePath']), oTagsUpd_LOAD)
                    sFileName_LOAD = defineString(deepcopy(oArchiveValue['FileName']), oTagsUpd_LOAD)

                    sFile_LOAD = join(sFilePath_LOAD, sFileName_LOAD)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check file availability
                    if exists(sFile_LOAD):

                        # -------------------------------------------------------------------------------------
                        # Define tags and filename SAVE
                        oDynamicTags_SAVE = updateRunTags({'Year': sTimeNow[0:4],
                                                           'Month': sTimeNow[4:6], 'Day': sTimeNow[6:8],
                                                           'Hour': sTimeNow[8:10], 'Minute': sTimeNow[10:12],
                                                           'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                          deepcopy(oDynamicTags_Default))
                        oTagsUpd_SAVE = mergeRunTags(oDynamicTags_SAVE, self.oDataTags)

                        sFilePath_SAVE = defineString(deepcopy(oDataValue['FilePath']), oTagsUpd_SAVE)
                        sFileName_SAVE = defineString(deepcopy(oDataValue['FileName']), oTagsUpd_LOAD)

                        sFile_SAVE = join(sFilePath_SAVE, sFileName_SAVE)
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Create destination folder
                        createFolder(split(sFile_SAVE)[0])

                        # Archive file in a new folder
                        copyFile(sFile_LOAD, sFile_SAVE)
                        # -------------------------------------------------------------------------------------
                    else:
                        # -------------------------------------------------------------------------------------
                        # Info variable end
                        Exc.getExc(
                            ' =====> WARNING: TimeStep: ' + sDataTime + ' TimeType: ' + sDataType +
                            ' File: ' + sFile_LOAD + ' is not available! Check run data!', 2, 1)
                        # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Info variable end
                oLogStream.info(' ----> Get variable ' + sDataKey + ' - Type: ' + sArchiveKey + ' gridded data ... OK')
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
