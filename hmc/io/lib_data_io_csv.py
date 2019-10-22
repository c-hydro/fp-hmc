"""
Library Features:

Name:          lib_data_io_csv
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180515'
Version:       '1.7.0'
"""
#################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Global libraries
from hmc.debug.drv_hmc_exception import Exc
#################################################################################

# --------------------------------------------------------------------------------
# Method to open csv file
def openFile(sFileName, sFileMode, sFileDelimiter=','):
    import csv

    try:

        if 'r' in sFileMode:
            with open(sFileName) as oFileHandle:
                oFileReader = csv.reader(oFileHandle, delimiter=sFileDelimiter)
                oFile = []
                for oRow in oFileReader:
                    a1sRow = ', '.join(oRow)
                    oFile.append(a1sRow)
            return oFile

        elif 'w' in sFileMode:
            with open(sFileName, sFileMode) as oFileHandle:
                oFile = csv.writer(oFileHandle, quoting=csv.QUOTE_NONNUMERIC)
        return oFile

    except IOError as oError:
        Exc.getExc(' -----> ERROR: in open file (lib_data_io_csv)' + ' [' + str(oError) + ']', 1, 1)

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to close csv file
def closeFile(oFile):
    Exc.getExc(' -----> Warning: no close method defined (lib_data_io_csv)', 2, 1)
    pass
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to parse file in csv format
def parseFile(oFile, sDelimiter=',', iSkipRows=0):

    if iSkipRows > 0:
        iSkipRows = iSkipRows - 1

    iNL = None
    a2oFileTable = []
    for iRowID, oRowData in enumerate(oFile):

        if iRowID > iSkipRows - 1:
            a1oRowData = oRowData.split(sDelimiter)
            a2oFileTable.append(a1oRowData)

            # Arrange data in table format
            if iNL is None:
                iNL = a1oRowData.__len__()
                a2oDataTable = [[] for iL in range(iNL)]
            else:
                pass

            for iElemID, sElemVal in enumerate(a1oRowData):
                a2oDataTable[iElemID].append(sElemVal)
        else:
            pass

    return a2oDataTable, a2oFileTable
# --------------------------------------------------------------------------------
