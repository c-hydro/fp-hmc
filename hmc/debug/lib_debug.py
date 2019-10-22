"""
Library Features:

Name:          lib_debug
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""
#######################################################################################
# Library
from __future__ import print_function

import logging
import shelve
import pickle
import scipy.io as sio

from os import remove
from os.path import join, exists
from tempfile import mkdtemp

from hmc.default.lib_default_args import sLoggerName
from hmc.utils.lib_utils_op_string import randomString

from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to set filename of debug workspace(s)
def setFileName(sFolderTemp=None, sFileTemp=None, sFileExt='.workspace'):

    # Define debug filename
    if not sFolderTemp:
        sFolderTemp = mkdtemp()
    if not sFileTemp:
        sFileTemp = randomString() + sFileExt
    sFilePath = join(sFolderTemp, sFileTemp)

    return sFilePath
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to save variable(s) workspace
def saveWorkspace(sFileName, **kwargs):
    # Remove old workspace
    if exists(sFileName):
        remove(sFileName)
    # Save new workspace
    oShelf = shelve.open(sFileName, 'n')
    for oKey, oValue in iter(kwargs.items()):
        try:
            oShelf[oKey] = oValue
        except TypeError:
            Exc.getExc(' =====> ERROR saving: {0}'.format(oKey), 1, 1)
    oShelf.close()
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to restore variable(s) workspace
def restoreWorkspace(sFileName):
    # Restore saved workspace
    oShelf = shelve.open(sFileName)
    oDictArgs = {}
    for oKey in oShelf:
        try:
            oDictArgs[oKey] = oShelf[oKey]
        except TypeError:
            Exc.getExc(' =====> ERROR restoring: {0}'.format(oKey), 1, 1)
    oShelf.close()
    return oDictArgs
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to save pickle file
def savePickle(sFileName, oVarData):
    oFile = open(sFileName, 'wb')
    pickle.dump(oVarData, oFile, protocol=pickle.HIGHEST_PROTOCOL)
    oFile.close()
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to restore pickle file
def restorePickle(sFileName):
    oFile = open(sFileName, 'rb')
    oVarData = pickle.load(oFile)
    oFile.close()
    return oVarData
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to save mat file
def saveMat(sFileName, oVarData, sVarName):
    oData = {sVarName: oVarData}
    sio.savemat(sFileName, oData)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to restore mat file
def restoreMat(sFileName):
    return sio.loadmat(sFileName)
# -------------------------------------------------------------------------------------
