"""
Class Features

Name:          drv_builder_datadynamic_forcing_point
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

from hmc.utils.lib_utils_op_dict import getDictValue, checkDictKeys
from hmc.utils.lib_utils_op_var import convertVarType

from hmc.data_dynamic.lib_datadynamic_forcing_ascii import getForcingPoint_ASCII, saveForcingPoint_ASCII

from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class Builder DataDynamic Forcing Point
class HMC_Builder_DataDynamic_Forcing_Point:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataDynamic = {}

    sPathTemp = None

    oSummaryTime = {}
    oDataTime = {}

    oDataStaticGridded = {}

    oDataDynamicPoint_INIT = {}
    oDataDynamicPoint_RUN = {}
    oDataDynamicPoint_GET = {}

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

        self.oDataDynamicPoint_INIT = oDataVarDynamic['DataForcing']['Point']
        self.oDataDynamicPoint_RUN = oDataDynamic_Default['DataAllocate']['Point']
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get dynamic file(s)
    def getFile(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Get data dynamic forcing point ... ')

        # Method to get observed dynamic point file(s)
        self.__getFilePoint_Obs(sRunMode, getDictValue(self.oDataDynamicPoint_INIT, ['FileType']))

        # Info end
        oLogStream.info(' ---> Get data dynamic forcing point ... OK')

        return self.oDataTime
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get observed dynamic point file(s)
    def __getFilePoint_Obs(self, sRunMode, iFileType):

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
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Check file type
                if iFileType == 1:

                    # -------------------------------------------------------------------------------------
                    # Method to get variable from different file(s) --> ASCII
                    [oDataDynamicPoint_GET, oDataDynamicPoint_CHECK] = getForcingPoint_ASCII(
                        sDataTime, sRunMode, sDataFlag,
                        None, 15,
                        self.oDataTags,
                        self.oDataStaticGridded,
                        self.oDataDynamicPoint_INIT,
                        deepcopy(self.oDataDynamicPoint_RUN),
                        self.sPathTemp)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Method to check file gridded
                    a1bDataCheck[iDataID] = checkDictKeys(oDataDynamicPoint_CHECK)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check saving Data
                    if convertVarType(a1bDataCheck[iDataID]) is True:

                        # Method to save Data in forcing folder
                        saveForcingPoint_ASCII(
                            sDataTime,
                            join(self.oDataDynamicPoint_INIT['FilePath'], self.oDataDynamicPoint_INIT['FileName']),
                            sRunMode, sDataFlag,
                            self.oDataSettings, self.oDataTags,
                            oDataDynamicPoint_GET)

                        # Put summary time information
                        self.oSummaryTime = putTimeSummary(sDataTime, self.oSummaryTime,
                                                           convertVarType(a1bDataCheck[iDataID]), 'DataForcingPoint')

                        # Info end (ok)
                        oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... '
                                        'OK')
                    else:
                        # Info end (skip)
                        oLogStream.info(' ----> DataTime ' + sDataTime + ' DataType: ' + sDataFlag + ' ... '
                                        'SKIP - ALL DATA ARE NOT AVAILABLE ')
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
        # Pass Data checking
        self.a1bDataCheck_Obs = a1bDataCheck
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
