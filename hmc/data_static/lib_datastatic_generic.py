"""
Library Features:

Name:          lib_datastatic_generic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging

from hmc.default.lib_default_args import sLoggerName

from hmc.io.lib_data_io_ascii import openFile, closeFile, getVar, readArcGrid
from hmc.utils.lib_utils_apps_geo import readGeoHeader, defineGeoCorner, \
    defineGeoGrid, defineGeoHeader, correctGeoHeader

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to get file static point
def getFileStaticPoint(sFileName):

    oFile = openFile(sFileName, 'r')
    a2dData = getVar(oFile)
    closeFile(oFile)

    return a2dData

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get file static gridded
def getFileStaticGridded(sFileName):

    oFile = openFile(sFileName, 'r')
    [a2dData, a1oVarHeader] = readArcGrid(oFile)
    closeFile(oFile)

    [iRows, iCols, dGeoXMin, dGeoYMin, dGeoXStep, dGeoYStep, dNoData] = readGeoHeader(a1oVarHeader)
    [dGeoXMin, dGeoXMax, dGeoYMin, dGeoYMax] = defineGeoCorner(dGeoXMin, dGeoYMin, dGeoXStep, dGeoYStep, iCols, iRows)

    [a2dGeoX, a2dGeoY, a1dGeoBox] = defineGeoGrid(dGeoYMin, dGeoXMin, dGeoYMax, dGeoXMax, dGeoYStep, dGeoXStep)
    a1oGeoHeader = defineGeoHeader(iRows, iCols, dGeoXMin, dGeoYMin, dGeoXStep, dGeoYStep, dNoData)

    # Correct GeoHeader key(s) --> lower characters
    a1oGeoHeader = correctGeoHeader(a1oGeoHeader)

    return a2dData, a2dGeoX, a2dGeoY, a1dGeoBox, dGeoXStep, dGeoYStep, a1oGeoHeader
# -------------------------------------------------------------------------------------
