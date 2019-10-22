"""
Class Features

Name:          drv_finalizer_timeseries
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
from os.path import join, split
from copy import deepcopy

from hmc.default.lib_default_args import sLoggerName

from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_tags import oDynamicTags as oDynamicTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default
from hmc.default.lib_default_time import oDataTime as oDataTime_Default

from hmc.data_dynamic.lib_datadynamic_results import getFilePoint_1D, getFilePoint_2D
from hmc.data_dynamic.lib_datadynamic_timeseries import writeTS_Default, writeTS_Dewetra, writeTS_HydrApp

from hmc.utils.lib_utils_op_string import defineString
from hmc.utils.lib_utils_op_dict import getDictValue
from hmc.utils.lib_utils_apps_file import createFolder
from hmc.utils.lib_utils_apps_tags import updateRunTags, mergeRunTags

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Define data format
oDataFormat = {'Obs': {'Discharge': ['ID', 'Data'],
                       'DamV': ['ID', 'Data', 'Ref'],
                       'DamL': ['ID', 'Data', 'Ref']}}
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class FinalizerTimeSeries
class HMC_Finalizer_TimeSeries:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataVarStatic = {}
    oDataVarDynamic = {}

    sTimeNow = None
    oDataTime = {}

    oDataStaticPoint = None

    oDataOutputPoint = None
    oDataOutputTimeSeries = None

    oDataObsPoint = None

    oDataAllocateTimeSeries = None

    oDataWorkspace = None
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

        self.oDataStaticPoint = oDataVarStatic['DataAllocate']['Point']

        self.oDataObsPoint = oDataVarDynamic['DataObs']['Point']

        self.oDataOutcomePoint = oDataVarDynamic['DataOutcome']['Point']
        self.oDataOutcomeTimeSeries = oDataVarDynamic['DataOutcome']['TimeSeries']

        self.oDataAllocateTimeSeries = oDataVarDynamic['DataAllocate']['TimeSeries']
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to write time series
    def writeData(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Write model time-series ... ')

        # Get data in point format
        self.oDataWorkspace = self.__createDataTimeSeries(sRunMode, oRunArgs)

        # Write data point in timeseries generic format
        self.__writeDataTimeSeries(sRunMode, oRunArgs)

        # Info end
        oLogStream.info(' ---> Write model time-series ... OK')
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to create data in timeseries format
    def __createDataTimeSeries(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Get variable information
        oDataObs = self.oDataObsPoint
        oDataOutcome = self.oDataOutcomePoint

        # Create Data archive dictionary
        oDataArchive = {'Obs': oDataObs, 'Outcome': oDataOutcome}
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Cycle(s) over Data archive(s)
        oDataWorkspace = {}
        for sArchiveKey, oArchiveValue in oDataArchive.items():

            # -------------------------------------------------------------------------------------
            # Get Data variable(s)
            oDataVars = getDictValue(oArchiveValue, ['FileVars', 'ARCHIVE', 'VarName'], 0)

            # Get data format(s)
            if sArchiveKey in oDataFormat:
                oFormatVars = oDataFormat[sArchiveKey]
            else:
                oFormatVars = None
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Check variable workspace
            if oDataVars:

                # -------------------------------------------------------------------------------------
                # Cycle(s) over variable(s)
                oDataWorkspace[sArchiveKey] = {}
                for sDataKey, oDataValue in oDataVars.items():

                    # -------------------------------------------------------------------------------------
                    # Info variable start
                    oLogStream.info(
                        ' ----> Get variable ' + sDataKey + ' - Type: ' + sArchiveKey + ' point data ... ')
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Get data column in variable file (according with format definition)
                    if oFormatVars and (sDataKey in oFormatVars):
                        oFormatVar = oFormatVars[sDataKey]
                        iVarCol = oFormatVar.index('Data')
                    else:
                        iVarCol = None
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Cycle(s) over time(s)
                    oTimeStep = []
                    oTimeType = []
                    oDataWorkspace[sArchiveKey][sDataKey] = {}
                    for iDataTime, (sDataTime, sDataType) in enumerate(
                            zip(self.oDataTime['TimeStep'], self.oDataTime['DataType'])):

                        # -------------------------------------------------------------------------------------
                        # Define tags and filename LOAD
                        oDynamicTags = updateRunTags({'Year': sDataTime[0:4],
                                                           'Month': sDataTime[4:6], 'Day': sDataTime[6:8],
                                                           'Hour': sDataTime[8:10], 'Minute': sDataTime[10:12],
                                                           'RunMode': sRunMode, 'VarName': oDataValue['FileVar']},
                                                          deepcopy(oDynamicTags_Default))
                        oTagsUpd = mergeRunTags(oDynamicTags, self.oDataTags)

                        sFilePath_STEP = defineString(deepcopy(oArchiveValue['FilePath']), oTagsUpd)
                        sFileName_STEP = defineString(deepcopy(oArchiveValue['FileName']), oTagsUpd)

                        sFile_STEP = join(sFilePath_STEP, sFileName_STEP)
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Get Data
                        if sDataKey == 'VarAnalysis':
                            oDataPoint = getFilePoint_2D(sFile_STEP)
                        else:
                            oDataPoint = getFilePoint_1D(sFile_STEP, iVarCol)
                        # Store data point
                        oDataWorkspace[sArchiveKey][sDataKey][sDataTime] = oDataPoint

                        # Define time information
                        oTimeStep.append(sDataTime)
                        oTimeType.append(sDataType)
                        # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Store time information
                    if 'TimeStep' not in oDataWorkspace:
                        oDataWorkspace['TimeStep'] = oTimeStep
                    if 'DataTime' not in oDataWorkspace:
                        oDataWorkspace['DataTime'] = oTimeType
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Info variable start
                    oLogStream.info(
                        ' ----> Get variable ' + sDataKey + ' - Type: ' + sArchiveKey + ' point data ... OK')
                    # -------------------------------------------------------------------------------------

            else:

                # -------------------------------------------------------------------------------------
                # Variable workspace not defined
                oDataWorkspace[sArchiveKey] = None
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return Data
        return oDataWorkspace
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to write Data in timeseries format
    def __writeDataTimeSeries(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Get variable information
        oDataPoint = self.oDataStaticPoint
        oDataOutcome = self.oDataOutcomeTimeSeries
        oDataAllocate = self.oDataAllocateTimeSeries

        # Get Data information
        oDataWorkspace = self.oDataWorkspace

        # Get time information
        sTimeNow = self.sTimeNow
        sTimeFrom = self.oDataTime['TimeStep'][0]
        iEnsN = int(oRunArgs[2])

        # Get data section(s) and dam(s)
        oSectionData = getDictValue(oDataPoint, ['FileVars', 'Section', 'Data'], 0)
        oDamData = getDictValue(oDataPoint, ['FileVars', 'Dam', 'Data'], 0)
        # Get data variable(s)
        oVarAllocateTS = getDictValue(oDataAllocate, ['FileVars', 'ARCHIVE'], 0)
        oVarOutcomeTS = getDictValue(oDataOutcome, ['FileVars', 'ARCHIVE', 'VarName'], 0)
        oVarHydrAppTS = getDictValue(oDataOutcome, ['FileVars', 'HYDRAPP', 'VarName'], 0)

        # Create Data timeseries dictionary
        oDataWorkspaceTS = {'TimeSeries': oDataWorkspace}
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Iterate over workspace(s)
        for sVarKeyTS, oVarDataTS in oDataWorkspaceTS.items():

            # -------------------------------------------------------------------------------------
            # Iterate over variables name
            for sVarNameTS in oVarAllocateTS.keys():

                # -------------------------------------------------------------------------------------
                # Get variable attributes
                if sVarNameTS in oVarOutcomeTS:
                    oVarOutcomeTS_ATTRS = oVarOutcomeTS[sVarNameTS]
                else:
                    oVarOutcomeTS_ATTRS = None
                if sVarNameTS in oVarHydrAppTS:
                    oVarHydrAppTS_ATTRS = oVarOutcomeTS[sVarNameTS]
                else:
                    oVarHydrAppTS_ATTRS = None
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Get data observed and modelled
                if sVarNameTS in oVarDataTS['Outcome']:
                    oVarDataTS_MOD = getDictValue(oVarDataTS['Outcome'], [sVarNameTS], 0)
                else:
                    oVarDataTS_MOD = None

                if sVarNameTS in oVarDataTS['Obs']:
                    oVarDataTS_OBS = getDictValue(oVarDataTS['Obs'], [sVarNameTS], 0)
                else:
                    oVarDataTS_OBS = None
                # Get data header
                if sVarNameTS in oVarAllocateTS:
                    oVarHeaderTS = oVarAllocateTS[sVarNameTS]['Attrs']
                else:
                    oVarHeaderTS = None
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Define filename outcome
                if oVarOutcomeTS_ATTRS:
                    oDynamicTagsTS = updateRunTags({'Year': sTimeNow[0:4],
                                                     'Month': sTimeNow[4:6], 'Day': sTimeNow[6:8],
                                                     'Hour': sTimeNow[8:10], 'Minute': sTimeNow[10:12],
                                                     'RunMode': sRunMode, 'VarName': oVarOutcomeTS_ATTRS['FileVar']},
                                                    deepcopy(oDynamicTags_Default))
                    oTagsTS = mergeRunTags(oDynamicTagsTS, self.oDataTags)

                    sFilePathTS = defineString(deepcopy(oVarOutcomeTS_ATTRS['FilePath']), oTagsTS)
                    sFileNameTS = defineString(deepcopy(oVarOutcomeTS_ATTRS['FileName']), oTagsTS)

                    sFileOutcomeTS = join(sFilePathTS, sFileNameTS)

                    # Create destination folder
                    createFolder(split(sFileOutcomeTS)[0])
                else:
                    sFileOutcomeTS = None

                # Define filename hydrapp
                if oVarHydrAppTS_ATTRS:
                    oDynamicTagsTS = updateRunTags({'Year': sTimeNow[0:4],
                                                    'Month': sTimeNow[4:6], 'Day': sTimeNow[6:8],
                                                    'Hour': sTimeNow[8:10], 'Minute': sTimeNow[10:12],
                                                    'RunMode': sRunMode, 'VarName': oVarHydrAppTS_ATTRS['FileVar']},
                                                   deepcopy(oDynamicTags_Default))
                    oTagsTS = mergeRunTags(oDynamicTagsTS, self.oDataTags)

                    sFilePathTS = defineString(deepcopy(oVarHydrAppTS_ATTRS['FilePath']), oTagsTS)
                    sFileNameTS = defineString(deepcopy(oVarHydrAppTS_ATTRS['FileName']), oTagsTS)

                    sFileHydrappTS = join(sFilePathTS, sFileNameTS)

                    # Create destination folder
                    createFolder(split(sFileHydrappTS)[0])
                else:
                    sFileHydrappTS = None
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Save time-series
                if sVarNameTS == 'Section':

                    if sFileOutcomeTS:
                        writeTS_Default(sFileOutcomeTS, oVarDataTS_MOD, oVarHeaderTS)
                    if sFileHydrappTS:
                        writeTS_HydrApp(sFileHydrappTS, sTimeNow, sTimeFrom,
                                        oVarDataTS_MOD, oVarDataTS_OBS, oSectionData, 60, iEnsN, sRunMode)

                if sVarNameTS == 'DamV':
                    if sFileOutcomeTS:
                        writeTS_Default(sFileOutcomeTS, oVarDataTS_MOD, oVarHeaderTS)
                if sVarNameTS == 'DamL':
                    if sFileOutcomeTS:
                        writeTS_Default(sFileOutcomeTS, oVarDataTS_MOD, oVarHeaderTS)
                if sVarNameTS == 'VarAnalysis':
                    if sFileOutcomeTS:
                        writeTS_Default(sFileOutcomeTS, oVarDataTS_MOD, oVarHeaderTS)
                # -------------------------------------------------------------------------------------

                print('ciao')

                # -------------------------------------------------------------------------------------
                # Info variable end
                oLogStream.info(' ----> Save Variable ' + sDataKey_TS + ' TimeSeries ... OK')
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Write data point in timeseries dewetra format
    def __writeDataDewetra(self, sRunMode, oRunArgs):

        '''
        # Convert array from float to string
        a1sDataObs = [a1dDataObs.tolist()]

        # Save update information
        oModelData = {}

        # Flag information
        oModelData['Line_01'] = 'Procedure=' + str(sRunType) + ' \n'
        oModelData['Line_02'] = 'DateMeteoModel=' + str(sTimeNow) + ' \n'
        oModelData['Line_03'] = 'DateStart=' + str(sTimeFrom) + ' \n'
        oModelData['Line_04'] = 'Temp.Resolution=' + str(iTimeRes) + ' \n'
        oModelData['Line_05'] = 'SscenariosNumber=' + str(int(iEnsN)) + ' \n'
        oModelData['Line_06'] = (' '.join(map(str, a1sDataObs[0]))) + ' \n'

        # Cycle(s) on Data dimension(s)
        sDigit = '%02d';
        for iEns in range(0, iEnsN):
            sLineName = 'Line_' + str(sDigit % (iEns + 7))

            a1dDataModel = a2dDataModel[iEns]
            a1sDataModel = [a1dDataModel.tolist()]

            oModelData[sLineName] = (' '.join(map(str, a1sDataModel[0]))) + ' \n'

        # Dictionary sorting
        oModelDataOrd = collections.OrderedDict(sorted(oModelData.items()))

        # Open ASCII file (to save all Data)
        oFileHandler = open(sFileName, 'w');

        # Write Data in ASCII file
        oFileHandler.writelines(oModelDataOrd.values())
        # Close ASCII file
        oFileHandler.close()

        print()




        '''
        pass
    # -------------------------------------------------------------------------------------