"""
Class Features

Name:          drv_builder_datadynamic_forcing_gridded
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging

from numpy import full
from os.path import join
from copy import deepcopy

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default
from hmc.default.lib_default_time import oDataTime as oDataTime_Default

from hmc.time.lib_time import putTimeSummary

from hmc.data_dynamic.lib_datadynamic_forcing_netcdf import getForcingGridded_Obs_NC, \
    getForcingGridded_For_NC, saveForcingGridded_NC, copyForcingGridded_NC
from hmc.data_dynamic.lib_datadynamic_forcing_binary import getForcingGridded_Binary, saveForcingGridded_Binary

from hmc.utils.lib_utils_op_dict import getDictValue
from hmc.utils.lib_utils_op_dict import checkDictKeys
from hmc.utils.lib_utils_op_var import convertVarType

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# from Lib_HMC_Apps_Debug import savePickle, restorePickle
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class Builder DataDynamic Forcing Gridded
class HMC_Builder_DataDynamic_Forcing_Gridded:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataDynamic = {}

    sPathTemp = None

    oSummaryTime = {}
    oDataTime = {}

    oDataStaticGridded = {}

    oDataDynamicGridded_INIT = {}
    oDataDynamicGridded_RUN = {}
    oDataDynamicGridded_GET = {}

    a1bDataCheck_For = None
    a1bDataCheck_Obs = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, oDataSettings=oDataSettings_Default, oDataTags=oConfigTags_Default,
                 oDataVarStatic=oDataStatic_Default,
                 oDataVarDynamic=oDataDynamic_Default,
                 oDataTime=oDataTime_Default):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = oDataSettings
        self.oDataTags = oDataTags
        self.oDataDynamic = oDataVarDynamic

        self.sPathTemp = oDataSettings['ParamsInfo']['Run_Path']['PathTemp']

        self.oDataTime = oDataTime
        self.oSummaryTime = oDataTime['DataTime']['TimeSummary']

        self.oDataStaticGridded = oDataVarStatic['DataAllocate']['Gridded']

        self.oDataDynamicGridded_INIT = oDataVarDynamic['DataForcing']['Gridded']
        self.oDataDynamicGridded_RUN = oDataDynamic_Default['DataAllocate']['Gridded']
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get dynamic file(s)
    def getFile(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Get data dynamic forcing gridded ... ')

        # Method to get observed dynamic gridded file(s)
        self.__getFileGridded_Obs(sRunMode, getDictValue(self.oDataDynamicGridded_INIT, ['FileType']))

        # Method to get forecast dynamic gridded file(s)
        self.__getFileGridded_For(sRunMode, getDictValue(self.oDataDynamicGridded_INIT, ['FileType']))

        # Info end
        oLogStream.info(' ---> Get data dynamic forcing gridded ... OK')

        return self.oDataTime
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get forecast dynamic gridded file(s)
    def __getFileGridded_For(self, sRunMode, iFileType):

        # -------------------------------------------------------------------------------------
        # Cycle(s) over time(s)
        sDataFlag = 'FOR'
        a1bDataCheck = full((len(self.oSummaryTime['TimeStep'])), False, dtype=bool)
        for iDataID, sDataTime in enumerate(self.oSummaryTime['TimeStep']):

            # -------------------------------------------------------------------------------------
            # Select FOR step(s)
            if sDataFlag in self.oSummaryTime['DataType'][iDataID]:

                # -------------------------------------------------------------------------------------
                # Info start
                oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... ')
                # Get time index
                iDataIndex = self.oSummaryTime['TimeStep'].index(sDataTime)
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Check file type
                if iFileType == 1:

                    # -------------------------------------------------------------------------------------
                    # Method to get variable from different file(s) --> BINARY
                    [oDataDynamicGridded_GET, oDataDynamicGridded_CHECK] = getForcingGridded_Binary(
                        sDataTime, sRunMode, sDataFlag,
                        None, 15,
                        self.oDataTags,
                        self.oDataStaticGridded,
                        self.oDataDynamicGridded_INIT,
                        deepcopy(self.oDataDynamicGridded_RUN),
                        self.sPathTemp)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Method to check file gridded
                    a1bDataCheck[iDataIndex] = checkDictKeys(oDataDynamicGridded_CHECK)[0]
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check saving Data
                    if convertVarType(a1bDataCheck[iDataIndex]) is True:

                        # Method to save Data in forcing folder
                        saveForcingGridded_Binary(
                            sDataTime,
                            join(self.oDataDynamicGridded_INIT['FilePath'], self.oDataDynamicGridded_INIT['FileName']),
                            sRunMode, sDataFlag,
                            self.oDataSettings, self.oDataTags,
                            oDataDynamicGridded_GET)

                        # Put summary time information
                        self.oSummaryTime = putTimeSummary(sDataTime, self.oSummaryTime,
                                                           convertVarType(a1bDataCheck[iDataIndex]),
                                                           'DataForcingGridded')

                        # Info end (ok)
                        oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... '
                                        'OK')
                    else:
                        # Info end (skip)
                        oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... '
                                        'SKIP - ALL DATA ARE NOT AVAILABLE ')
                    # -------------------------------------------------------------------------------------

                elif iFileType == 2:

                    # -------------------------------------------------------------------------------------
                    # Method to get variable from different file(s)
                    [oDataDynamicGridded_GET, oDataDynamicGridded_CHECK,
                     oDataDynamicGridded_FILE, bDataDynamicGridded_OP] = getForcingGridded_For_NC(
                        sDataTime, sRunMode, sDataFlag,
                        self.oDataTime['DataTime']['TimeNow'], 15,
                        self.oDataTags,
                        self.oDataStaticGridded,
                        self.oDataDynamicGridded_INIT,
                        deepcopy(self.oDataDynamicGridded_RUN),
                        self.sPathTemp)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check merge condition
                    if bDataDynamicGridded_OP:

                        # -------------------------------------------------------------------------------------
                        # Info about forcing file outcome
                        oLogStream.info(' -----> Variable(s) file(s) adjust and save to execution forcing folder')
                        # Method to check file gridded
                        a1bDataCheck[iDataIndex] = checkDictKeys(oDataDynamicGridded_CHECK)[0]
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Check saving Data
                        if convertVarType(a1bDataCheck[iDataIndex]) is True:

                            # Method to save in a common file
                            saveForcingGridded_NC(
                                sDataTime,
                                join(self.oDataDynamicGridded_INIT['FilePath'],
                                     self.oDataDynamicGridded_INIT['FileName']),
                                sRunMode, sDataFlag,
                                self.oDataSettings, self.oDataTags,
                                oDataDynamicGridded_GET)

                            # Put summary time information
                            self.oSummaryTime = putTimeSummary(sDataTime, self.oSummaryTime,
                                                               convertVarType(a1bDataCheck[iDataIndex]),
                                                               'DataForcingGridded')

                            # Info end (ok)
                            oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... OK')
                        else:
                            # Info end (skip)
                            oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... SKIP')
                        # -------------------------------------------------------------------------------------

                    else:

                        # -------------------------------------------------------------------------------------
                        # Info about forcing file outcome
                        oLogStream.info(' -----> Variable(s) file(s) copy to execution forcing folder')

                        # Method to check file gridded
                        a1bDataCheck[iDataIndex] = True

                        bForcingGridded_NC = copyForcingGridded_NC(sDataTime,
                                                                   join(self.oDataDynamicGridded_INIT['FilePath'],
                                                                        self.oDataDynamicGridded_INIT['FileName']),
                                                                   oDataDynamicGridded_FILE,
                                                                   sRunMode, sDataFlag,
                                                                   self.oDataSettings, self.oDataTags)
                        # Check copying file procedure
                        if bForcingGridded_NC:

                            # Put summary time information
                            self.oSummaryTime = putTimeSummary(sDataTime, self.oSummaryTime,
                                                               convertVarType(a1bDataCheck[iDataIndex]),
                                                               'DataForcingGridded')

                            # Info end (ok)
                            oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... OK')
                        else:
                            # Info end (skip)
                            oLogStream.info(
                                ' ----> DataTime ' + sDataTime +
                                ' DataType: ' + sDataFlag + ' ...  SKIP - FILE IS NOT CORRECTLY COPIED')
                        # -------------------------------------------------------------------------------------

                else:

                    # -------------------------------------------------------------------------------------
                    # Exit for file type mismatch
                    Exc.getExc(' =====> ERROR: FileType flag is not correctly set! Check your settings!', 1, 1)
                    # -------------------------------------------------------------------------------------

            else:

                # -------------------------------------------------------------------------------------
                # Pass for time step not match with Data flag
                pass
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get observed dynamic gridded file(s)
    def __getFileGridded_Obs(self, sRunMode, iFileType):

        # -------------------------------------------------------------------------------------
        # Cycle(s) over time(s)
        sDataFlag = 'OBS'
        a1bDataCheck = full((len(self.oSummaryTime['TimeStep'])), False, dtype=bool)
        for iDataID, sDataTime in enumerate(self.oSummaryTime['TimeStep']):

            # -------------------------------------------------------------------------------------
            # Select OBS step(s)
            if sDataFlag in self.oSummaryTime['DataType'][iDataID]:

                # -------------------------------------------------------------------------------------
                # Info start
                oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... ')
                # Get time index
                iDataIndex = self.oSummaryTime['TimeStep'].index(sDataTime)
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Check file type
                if iFileType == 1:

                    # -------------------------------------------------------------------------------------
                    # Method to get variable from different file(s) --> BINARY
                    [oDataDynamicGridded_GET, oDataDynamicGridded_CHECK] = getForcingGridded_Binary(
                        sDataTime, sRunMode, sDataFlag,
                        None, 15,
                        self.oDataTags,
                        self.oDataStaticGridded,
                        self.oDataDynamicGridded_INIT,
                        deepcopy(self.oDataDynamicGridded_RUN),
                        self.sPathTemp)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Method to check file gridded
                    a1bDataCheck[iDataIndex] = checkDictKeys(oDataDynamicGridded_CHECK)[0]
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check saving Data
                    if convertVarType(a1bDataCheck[iDataIndex]) is True:

                        # Method to save Data in forcing folder
                        saveForcingGridded_Binary(
                            sDataTime,
                            join(self.oDataDynamicGridded_INIT['FilePath'], self.oDataDynamicGridded_INIT['FileName']),
                            sRunMode, sDataFlag,
                            self.oDataSettings, self.oDataTags,
                            oDataDynamicGridded_GET)

                        # Put summary time information
                        self.oSummaryTime = putTimeSummary(sDataTime, self.oSummaryTime,
                                                           convertVarType(a1bDataCheck[iDataIndex]),
                                                           'DataForcingGridded')

                        # Info end (ok)
                        oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... '
                                        'OK')
                    else:
                        # Info end (skip)
                        oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... '
                                        'SKIP - ALL DATA ARE NOT AVAILABLE ')
                    # -------------------------------------------------------------------------------------

                elif iFileType == 2:

                    # -------------------------------------------------------------------------------------
                    # Method to get variable from different file(s) --> netCDF
                    [oDataDynamicGridded_GET, oDataDynamicGridded_CHECK,
                     oDataDynamicGridded_FILE, bDataDynamicGridded_OP] = \
                        getForcingGridded_Obs_NC(sDataTime, sRunMode, sDataFlag,
                                                 None, 15,
                                                 self.oDataTags,
                                                 self.oDataStaticGridded,
                                                 self.oDataDynamicGridded_INIT,
                                                 deepcopy(self.oDataDynamicGridded_RUN),
                                                 self.sPathTemp)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check merge condition
                    if bDataDynamicGridded_OP:

                        # -------------------------------------------------------------------------------------
                        # Info about forcing file outcome
                        oLogStream.info(' -----> Variable(s) file(s) adjust and save to execution forcing folder')

                        # Method to check file gridded
                        a1bDataCheck[iDataIndex] = checkDictKeys(oDataDynamicGridded_CHECK)[0]
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Check saving Data
                        if convertVarType(a1bDataCheck[iDataIndex]) is True:

                            # Method to save Data in forcing folder
                            saveForcingGridded_NC(
                                sDataTime,
                                join(self.oDataDynamicGridded_INIT['FilePath'],
                                     self.oDataDynamicGridded_INIT['FileName']),
                                sRunMode, sDataFlag,
                                self.oDataSettings, self.oDataTags,
                                oDataDynamicGridded_GET)

                            # Put summary time information
                            self.oSummaryTime = putTimeSummary(sDataTime, self.oSummaryTime,
                                                               convertVarType(a1bDataCheck[iDataIndex]),
                                                               'DataForcingGridded')
                            # Info end (ok)
                            oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... OK')
                        else:
                            # Info end (skip)
                            oLogStream.info(
                                ' ----> DataTime ' + sDataTime +
                                ' DataType: ' + sDataFlag + ' ...  SKIP - ALL DATA ARE NOT AVAILABLE')
                        # -------------------------------------------------------------------------------------

                    else:
                        # -------------------------------------------------------------------------------------
                        # Info about forcing file outcome
                        oLogStream.info(' -----> Variable(s) file(s) copy to execution forcing folder')

                        # Method to check file gridded
                        a1bDataCheck[iDataIndex] = True

                        bForcingGridded_NC = copyForcingGridded_NC(sDataTime,
                                                                   join(self.oDataDynamicGridded_INIT['FilePath'],
                                                                        self.oDataDynamicGridded_INIT['FileName']),
                                                                   oDataDynamicGridded_FILE,
                                                                   sRunMode, sDataFlag,
                                                                   self.oDataSettings, self.oDataTags)
                        # Check copying file procedure
                        if bForcingGridded_NC:

                            # Put summary time information
                            self.oSummaryTime = putTimeSummary(sDataTime, self.oSummaryTime,
                                                               convertVarType(a1bDataCheck[iDataIndex]),
                                                               'DataForcingGridded')
                            # Info end (ok)
                            oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... OK')
                        else:
                            # Info end (skip)
                            oLogStream.info(
                                ' ----> DataTime ' + sDataTime +
                                ' DataType: ' + sDataFlag + ' ...  SKIP - FILE IS NOT CORRECTLY COPIED')
                        # -------------------------------------------------------------------------------------

                else:
                    # -------------------------------------------------------------------------------------
                    # Exit for file type mismatch
                    Exc.getExc(' =====> ERROR: FileType flag is not correctly set! Check your settings!', 1, 1)
                    # -------------------------------------------------------------------------------------

            else:
                # -------------------------------------------------------------------------------------
                # Pass for time step not match with Data flag
                pass
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
