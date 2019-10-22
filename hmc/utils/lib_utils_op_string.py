"""
Library Features:

Name:          lib_utils_op_string
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging

from hmc.default.lib_default_args import sLoggerName
from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to create a random string
def randomString(sStringRoot='temporary', sStringSeparator='_', iMinRandom=0, iMaxRandom=1000):

    # Generate random number
    sRandomNumber = str(randint(iMinRandom, iMaxRandom))
    # Generate time now
    sTimeNow = datetime.now().strftime('%Y%m%d-%H%M%S_%f')

    # Concatenate string(s) with defined separator
    sRandomString = sStringSeparator.join([sStringRoot, sTimeNow, sRandomNumber])

    return sRandomString
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to define string
def defineString(sString='', oDictTags=None):

    if sString != '':
        if not oDictTags:
            pass
        elif oDictTags:
            for sKey, oValue in iter(oDictTags.items()):

                if isinstance(oValue, list):            # list values
                    sVarKey = oValue[0]
                    oVarValue = oValue[1]
                elif isinstance(oValue, dict):          # dict values
                    sVarKey = list(oValue.keys())[0]
                    oVarValue = list(oValue.values())[0]
                else:                                   # scalar value
                    sVarKey = sKey
                    oVarValue = oValue

                if isinstance(oVarValue, str):
                    sString = sString.replace(sVarKey, oVarValue)
                elif isinstance(oVarValue, int):
                    sString = sString.replace(sVarKey, str(int(oVarValue)))
                elif isinstance(oVarValue, float):
                    sString = sString.replace(sVarKey, str(float(oVarValue)))
                else:
                    sString = sString.replace(sVarKey, str(oVarValue))
    else:
        pass

    return sString
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to convert UNICODE to ASCII
def convertUnicode2ASCII(sStringUnicode, convert_option='ignore'):
    # convert_option "ignore" or "replace"
    sStringASCII = sStringUnicode.encode('ascii', convert_option)
    return sStringASCII
# -------------------------------------------------------------------------------------
