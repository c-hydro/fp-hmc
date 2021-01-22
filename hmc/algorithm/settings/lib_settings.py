"""
Library Features:

Name:          lib_settings
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
import numpy as np
import decimal
import collections

from hmc.algorithm.default.lib_default_args import sLoggerName
from hmc.algorithm.default import oConfigTags as oConfigTags_Default
from hmc.algorithm.default.lib_default_settings import oDataSettings as oDataSettings_Default

from hmc.algorithm.utils import updateDictValue

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# --------------------------------------------------------------------------------
# Method to define run mode
def setRunMode(bEnsMode=False, sVarName='run', iVarMin=0, iVarMax=0, oVarStep=0):

    oRunDict = {}
    if bEnsMode:

        iVarEnsN = (iVarMax - iVarMin + oVarStep)/oVarStep
        a1iVarEns = np.linspace(iVarMin, iVarMax, endpoint=True, num=iVarEnsN)

        sVarEnsFormat = None
        if isinstance(oVarStep, int):
            sVarEnsFormat = '{:03d}'
        elif isinstance(oVarStep, float):
            oVarDecimal = decimal.Decimal(str(oVarStep))
            iVarDigitsAD = abs(oVarDecimal.as_tuple().exponent)
            iVarDigitsBD = len(oVarDecimal.as_tuple().digits) - iVarDigitsAD
            sVarEnsFormat = "{:" + str(iVarDigitsBD) + "." + str(iVarDigitsAD) + "f}"

        for iVarEnsID, oVarEnsN in enumerate(a1iVarEns):
            # Variable name
            if isinstance(oVarStep, int):
                sVarEnsN = sVarEnsFormat.format(int(oVarEnsN))
            else:
                sVarEnsN = sVarEnsFormat.format(oVarEnsN)
            # Run name
            sRunType = 'ensemble_' + sVarName.lower() + '_' + sVarEnsN
            # Run List definition
            oRunDict[sRunType] = [sVarName, sVarEnsN, str(iVarEnsID + 1)]

    else:
        # Run name
        sVarName = None
        sVarEnsN = None
        iVarEnsID = 1
        sRunType = 'deterministic'
        # Run List definition
        oRunDict[sRunType] = [sVarName, sVarEnsN, str(iVarEnsID)]

    # Dictionary sorting
    oRunMode = collections.OrderedDict(sorted(oRunDict.items()))

    return oRunMode
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# Method to set running settings
def setRunSettings(oTags=oConfigTags_Default, oSettings=oDataSettings_Default):

    for oTagKey, oTagValue in iter(oTags.items()):
        sTag = list(oTagValue.keys())[0]
        oValue = list(oTagValue.values())[0]
        if oValue:
            updateDictValue(oSettings, sTag, oValue)
        else:
            pass

    return oSettings
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# Method to update running settings
def updateRunSettings(oTags=oConfigTags_Default, oSettings=oDataSettings_Default):

    for oTagKey, oTagValue in iter(oTags.items()):

        if oTagValue is not None:
            sTag = list(oTagValue.keys())[0]
            oValue = list(oTagValue.values())[0]
            if oValue:
                updateDictValue(oSettings, sTag, oValue)
            else:
                pass
        else:
            pass

    return oSettings
# --------------------------------------------------------------------------------
