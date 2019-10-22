"""
Class Features

Name:          drv_builder_datadynamic_restart
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging

from hmc.default.lib_default_args import sLoggerName

from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default
from hmc.default.lib_default_time import oDataTime as oDataTime_Default

from hmc.utils.lib_utils_op_dict import getDictValue, checkDictKeys
from hmc.utils.lib_utils_op_var import convertVarType

from hmc.time.lib_time import putTimeSummary

from hmc.data_dynamic.lib_datadynamic_restart_binary import getRestartGridded_Binary
from hmc.data_dynamic.lib_datadynamic_restart_netcdf import getRestartGridded_NetCDF
from hmc.data_dynamic.lib_datadynamic_restart_ascii import getRestartPoint_ASCII

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class Builder DataDynamic Restart Gridded/Point
class HMC_Builder_DataDynamic_Restart:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataDynamic = {}

    sTimeRestart = None
    oDataTime = {}
    oSummaryTime = []

    sPathTemp = None

    oDataStaticGridded = {}
    oDataDynamicGridded = {}
    oDataDynamicPoint = {}
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, oDataSettings=oDataSettings_Default, oDataTags=oConfigTags_Default,
                 oDataVarStatic=oDataStatic_Default, oDataVarDynamic=oDataDynamic_Default,
                 oDataTime=oDataTime_Default):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = oDataSettings
        self.oDataTags = oDataTags
        self.oDataDynamic = oDataVarDynamic
        self.oDataTime = oDataTime

        self.sTimeRestart = oDataTime['DataTime']['TimeRestart']
        self.oSummaryTime = oDataTime['DataTime']['TimeSummary']

        self.sPathTemp = oDataSettings['ParamsInfo']['Run_Path']['PathTemp']

        self.oDataStaticGridded = oDataVarStatic['DataAllocate']['Gridded']
        self.oDataDynamicGridded = oDataVarDynamic['DataRestart']['Gridded']
        self.oDataDynamicPoint = oDataVarDynamic['DataRestart']['Point']
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get dynamic file(s)
    def getFile(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Get Data dynamic restart gridded/point ... ')

        # Get restart flag
        iFlagRestart = getDictValue(self.oDataSettings, ['ParamsInfo', 'HMC_Flag', 'Flag_Restart'])
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Restart condition
        if iFlagRestart == 1:

            # -------------------------------------------------------------------------------------
            # Method to get restart dynamic gridded file(s)
            self.__getFileGridded_Restart(sRunMode, getDictValue(self.oDataDynamicGridded, ['FileType']))

            # Method to get restart dynamic point file(s)
            self.__getFilePoint_Restart(sRunMode, getDictValue(self.oDataDynamicPoint, ['FileType']))

            # Info end (ok)
            oLogStream.info(' ---> Get Data dynamic restart gridded/point ... OK')
            # -------------------------------------------------------------------------------------

        else:

            # -------------------------------------------------------------------------------------
            # Info end (skip)
            oLogStream.info(' ---> Get Data dynamic restart gridded/point ... SKIP - RESTART NOT ACTIVATED')
            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return variable(s)
        return self.oDataTime
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get restart dynamic gridded file(s)
    def __getFileGridded_Restart(self, sRunMode, iFileType):

        # -------------------------------------------------------------------------------------
        # Info start
        sDataFlag = 'ARCHIVE'
        oLogStream.info(' ----> DataTime ' + self.sTimeRestart + ' DataType: ' + sDataFlag + ' (GRIDDED) ... ')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Check file type
        if iFileType == 1:

            # -------------------------------------------------------------------------------------
            # Method to get restart gridded Data from different file(s) --> BINARY
            oRestartGridded_CHECK = getRestartGridded_Binary(
                self.sTimeRestart, sRunMode, sDataFlag,
                self.sTimeRestart, 15,
                self.oDataTags,
                self.oDataDynamicGridded,
                self.sPathTemp)
            # Method to check variable(s) in gridded file(s)
            iRestartGridded_CHECK = checkDictKeys(oRestartGridded_CHECK)

            # Exit code from restart gridded Data
            if convertVarType(iRestartGridded_CHECK) is True:

                # Update summary time information
                self.oSummaryTime = putTimeSummary(self.sTimeRestart, self.oSummaryTime,
                                                   iRestartPoint_CHECK, 'DataRestartGridded')

                # Info end (ok)
                oLogStream.info(' ----> DataTime ' + self.sTimeRestart + ' DataType: ' + sDataFlag + ' (GRIDDED) ... '
                                'OK')
            else:
                # Info end (skip)
                oLogStream.info(' ----> DataTime ' + self.sTimeRestart + ' DataType: ' + sDataFlag + ' (GRIDDED) ... '
                                'SKIP - ALL DATA ARE NOT AVAILABLE ')
            # -------------------------------------------------------------------------------------

        elif iFileType == 2:

            # -------------------------------------------------------------------------------------
            # Method to get restart gridded Data from different file(s) --> NetCDF
            oRestartGridded_CHECK = getRestartGridded_NetCDF(
                self.sTimeRestart, sRunMode, sDataFlag,
                self.sTimeRestart, 15,
                self.oDataTags,
                self.oDataDynamicGridded,
                self.sPathTemp)
            # Method to check variable(s) in gridded file(s)
            oRestartGridded_CHECK = checkDictKeys(oRestartGridded_CHECK)
            iRestartGridded_CHECK = oRestartGridded_CHECK[0]

            # Exit code from restart gridded Data
            if convertVarType(iRestartGridded_CHECK) is True:

                # Put summary time information
                self.oSummaryTime = putTimeSummary(self.sTimeRestart, self.oSummaryTime,
                                                   convertVarType(iRestartGridded_CHECK), 'DataRestartGridded')

                # Info end (ok)
                oLogStream.info(' ----> DataTime ' + self.sTimeRestart + ' DataType: ' + sDataFlag + ' (GRIDDED) ... '
                                'OK')
            else:
                # Info end (skip)
                oLogStream.info(' ----> DataTime ' + self.sTimeRestart + ' DataType: ' + sDataFlag + ' (GRIDDED) ... '
                                'SKIP - ALL DATA ARE NOT AVAILABLE ')
            # -------------------------------------------------------------------------------------

        else:

            # -------------------------------------------------------------------------------------
            # Exit for file type mismatch
            Exc.getExc(' =====> ERROR: FileType flag is not correctly set! Check your settings!', 1, 1)
            # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get restart dynamic point file(s)
    def __getFilePoint_Restart(self, sRunMode, iFileType):

        # -------------------------------------------------------------------------------------
        # Info start
        sDataFlag = 'ARCHIVE'
        oLogStream.info(' ----> DataTime ' + self.sTimeRestart + ' DataType: ' + sDataFlag + ' (POINT) ... ')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Check file type
        if iFileType == 1:

            # Method to get restart point Data from different file(s) --> BINARY
            oRestartPoint_CHECK = getRestartPoint_ASCII(
                self.sTimeRestart, sRunMode, sDataFlag,
                self.sTimeRestart, 15,
                self.oDataTags,
                self.oDataDynamicPoint,
                self.sPathTemp)
            # Method to check variable(s) in gridded file(s)
            oRestartPoint_CHECK = checkDictKeys(oRestartPoint_CHECK)
            iRestartPoint_CHECK = oRestartPoint_CHECK[0]

            # Exit code from restart gridded Data
            if convertVarType(iRestartPoint_CHECK) is True:

                # Put summary time information
                self.oSummaryTime = putTimeSummary(self.sTimeRestart, self.oSummaryTime,
                                                   convertVarType(iRestartPoint_CHECK), 'DataRestartPoint')
                # Info end (ok)
                oLogStream.info(' ----> DataTime ' + self.sTimeRestart + ' DataType: ' + sDataFlag + ' (POINT) ... '
                                'OK')
            else:
                # Info end (skip)
                oLogStream.info(' ----> DataTime ' + self.sTimeRestart + ' DataType: ' + sDataFlag + ' (POINT) ... '
                                'SKIP - ALL DATA ARE NOT AVAILABLE ')
            # -------------------------------------------------------------------------------------

        else:

            # -------------------------------------------------------------------------------------
            # Exit for file type mismatch
            Exc.getExc(' =====> ERROR: FileType flag is not correctly set! Check your settings!', 1, 1)
            # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
