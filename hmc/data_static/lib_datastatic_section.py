"""
Library Features:

Name:          lib_datastatic_section
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
# Method to get file point section
def getFileStaticPointSection(sFileName):
    oFile = openFile(sFileName, 'r')

    oList = []
    for sFileLine in oFile.readlines():
        sFileLine = sFileLine.strip()
        sLineCols = sFileLine.split()
        oList.append(sLineCols)
    return oList

# -------------------------------------------------------------------------------------
