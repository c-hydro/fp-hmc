"""
Library Features:

Name:          lib_utils_file_args
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Logging
import logging
from datetime import datetime

from hmc.utils.lib_utils_apps_time import getTimeNow
from hmc.utils.lib_utils_op_dict import getDictValues, DictObj
from hmc.utils.lib_utils_apps_file import importFileDict

from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_args import sLoggerName

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# --------------------------------------------------------------------------------
# Method to get time arg
def getDataTime(sTimeArg):
    [sTimeArg, sTimeFormat] = getTimeNow(sTimeArg)
    oTimeArg = datetime.strptime(sTimeArg, sTimeFormat)
    return oTimeArg
# --------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to init settings data
def setDataSettings():
    oDataSettings = DictObj()
    return oDataSettings
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get data settings
def getDataSettings(sFileName, oSettings=oDataSettings_Default):

    [oFileData, bFileData] = importFileDict(sFileName)

    if bFileData:
        oDictUpd = {}
        for sArgKey, oArgDict in oSettings.items():
            oDictUpd[sArgKey] = {}
            for sDictKey, oDictValue in oArgDict.items():

                oFileKey = oFileData[sArgKey][sDictKey]

                oSettings[sArgKey][sDictKey] = {}
                oSettings[sArgKey][sDictKey] = oFileKey

    else:
        Exc.getExc(' =====> ERROR: settings file ' + sFileName + ' NOT FOUND!', 1, 1)

    return oFileData, oSettings

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to check settings file
def checkFileSettings(sFileName, oSettings=oDataSettings_Default):

    [oFileData, bFileData] = importFileDict(sFileName)

    bDictCheck = False
    if bFileData:
        for sArgKey, oArgDict in oSettings.items():

            if sArgKey in oFileData:

                oFileDict = oFileData[sArgKey]

                if not set(list(oFileDict.keys())) == set(list(oArgDict.keys())):
                    Exc.getExc(' =====> ERROR: check dictionary ' +
                               sArgKey + ' of configuration file ' + sFileName + ' FAILED', 1, 1)
                    bDictCheck = False
                else:
                    bDictCheck = True

            else:
                Exc.getExc(' =====> ERROR: check dictionary ' +
                           sArgKey + ' of configuration file ' + sFileName + ' FAILED', 1, 1)
                bDictCheck = False
    else:
        Exc.getExc(' =====> ERROR: check dictionary FAILED! File does not exist!', 1, 1)
        bDictCheck = False

    return bDictCheck

# -------------------------------------------------------------------------------------


