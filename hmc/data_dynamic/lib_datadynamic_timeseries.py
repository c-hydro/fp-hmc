"""
Class Features

Name:          lib_datadynamic_timeseries
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""
#######################################################################################
# Library
import logging
import os
import re
import collections
import numpy as np
from os.path import exists

from hmc.utils.lib_utils_op_string import defineString
from hmc.default.lib_default_args import sLoggerName

from hmc.driver.data.drv_data_io_type import Drv_Data_IO
from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to write timeseries data in hydrapp format
def writeTS_HydrApp(sFileName, sTimeNow, sTimeFrom, oDataModel, oDataObs=None, oFileSection=None, iTimeDelta=60,
                    iEnsN=1, sRunType='deterministic'):

    pass

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to write timeseries data in dewetra format
def writeTS_Dewetra(sFileName, sTimeNow, sTimeFrom, oDataModel, oDataObs=None, oFileSection=None, iTimeDelta=60,
                    iEnsN=1, sRunType='deterministic'):

    # Iterate over section
    for iSectionID, oSectionLine in enumerate(oFileSection):

        # Create file section name
        oSectionTags = {'$SECTION': oSectionLine[2], '$BASIN': oSectionLine[3]}
        sFileNameSection = defineString(sFileName, oSectionTags)

        # Check file existence on disk
        if exists(sFileNameSection):
            os.remove(sFileNameSection)

        oDataWS = []
        for sDataTime, oDataStep in sorted(oDataModel.items()):
            dDataStep = oDataStep[iSectionID]
            oDataWS.append(str(dDataStep))

        if oDataObs is None:
            oDataObs = [-9999.0] * oDataWS.__len__()

        # Save update information
        oDewetraWS = {}

        # Flag information
        oDewetraWS['Line_01'] = 'Procedure=' + str(sRunType) + ' \n'
        oDewetraWS['Line_02'] = 'DateMeteoModel=' + str(sTimeNow) + ' \n'
        oDewetraWS['Line_03'] = 'DateStart=' + str(sTimeFrom) + ' \n'
        oDewetraWS['Line_04'] = 'Temp.Resolution=' + str(iTimeDelta) + ' \n'
        oDewetraWS['Line_05'] = 'SscenariosNumber=' + str(int(iEnsN)) + ' \n'
        oDewetraWS['Line_06'] = (' '.join(map(str, oDataObs))) + ' \n'
        oDewetraWS['Line_07'] = (' '.join(map(str, oDataWS))) + ' \n'

        # Dictionary sorting
        oDewetraWSOrd = collections.OrderedDict(sorted(oDewetraWS.items()))

        # Open ASCII file (to save all Data)
        oFileSection = open(sFileNameSection, 'w')

        # Write Data in ASCII file
        oFileSection.writelines(oDewetraWSOrd.values())
        # Close ASCII file
        oFileSection.close()


# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to write timeseries data in default format
def writeTS_Default(sFileName, oFileData, sFileHeader=None):

    # Check file existence on disk
    if exists(sFileName):
        os.remove(sFileName)

    # Open file driver
    oDrv = Drv_Data_IO(sFileName).oFileWorkspace
    oFile = oDrv.oFileLibrary.openFile(sFileName, 'w')

    # Write header (if present)
    if sFileHeader:
        oDrv.oFileLibrary.writeVar(oFile, sFileHeader)

    # Cycle(s) over step(s) and write Data
    for sTimeData, oVarData in sorted(oFileData.items()):
        # Data parser
        oLineData = oVarData.tolist()
        oLineData.insert(0, sTimeData)
        sLineData = ' '.join(oLineData)
        # Save Data to file
        oDrv.oFileLibrary.writeVar(oFile, sLineData)

    # Close file and driver
    oDrv.oFileLibrary.closeFile(oFile)

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get timeseries Data
def getTimeSeries(sFileName):
    pass
# -------------------------------------------------------------------------------------
