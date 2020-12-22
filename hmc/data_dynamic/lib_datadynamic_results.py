"""
Class Features

Name:          lib_datadynamic_results
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""
#######################################################################################
# Library
import logging

from os.path import exists

from hmc.default.lib_default_args import sLoggerName

from hmc.driver.data.drv_data_io_type import Drv_Data_IO
from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to collect file output in 2D point format (var-analysis file)
def getFilePoint_2D(sFileName):

    # Check file availability
    if exists(sFileName):

        # Open file
        oDrv_IO = Drv_Data_IO(sFileName).oFileWorkspace
        oFile_DATA = oDrv_IO.oFileLibrary.openFile(sFileName, 'r')
        oDataArray = oDrv_IO.oFileLibrary.getLines(oFile_DATA)
        oDrv_IO.oFileLibrary.closeFile(oFile_DATA)

        oDataWS = []
        for oDataLine in oDataArray:
            oDataLine = oDataLine.strip()
            oDataCols = oDataLine.split()
            oDataWS.extend(oDataCols)

    else:
        # File not found
        oDataWS = None

    return oDataWS
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to collect file output in 1D point format (discharge, dam-level and dam-volume files)
def getFilePoint_1D(sFileName, iVarCol=None):

    # Check file availability
    if exists(sFileName):

        # Open file
        oDrv_IO = Drv_Data_IO(sFileName).oFileWorkspace
        oFile_DATA = oDrv_IO.oFileLibrary.openFile(sFileName, 'r')
        oDataArray = oDrv_IO.oFileLibrary.getVar(oFile_DATA)
        oDrv_IO.oFileLibrary.closeFile(oFile_DATA)

        if oDataArray is not None:
            oDataWS = []
            for oDataLine in oDataArray:

                if iVarCol is not None:
                    oDataValue = oDataLine[iVarCol]
                else:
                    oDataValue = oDataLine[0]
                oDataWS.append(oDataValue)
        else:
            # Data not found
            oDataWS = None

    else:
        # File not found
        oDataWS = None

    return oDataWS
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to collect file output in gridded format
def getFileGridded():
    pass
# -------------------------------------------------------------------------------------
