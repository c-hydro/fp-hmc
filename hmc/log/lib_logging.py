"""
Library Features:

Name:          lib_logging
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
import logging.config

from os.path import exists
from os import remove

from hmc.default.lib_default_args import sLoggerName as sLoggerName_Default
from hmc.default.lib_default_args import sLoggerFile as sLoggerFile_Default
from hmc.default.lib_default_args import sLoggerHandle as sLoggerHandle_Default
from hmc.default.lib_default_args import sLoggerFormatter as sLoggerFormatter_Default

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to set logging file
def setLoggingFile(sLoggerFile=sLoggerFile_Default, sLoggerName=sLoggerName_Default,
                   sLoggerHandle=sLoggerHandle_Default, sLoggerFormatter=sLoggerFormatter_Default):

    # Remove old logging file
    if exists(sLoggerFile):
        remove(sLoggerFile)

    # Open logger
    oLoggerStream = logging.getLogger(sLoggerName)
    oLoggerStream.setLevel(logging.DEBUG)

    # Set logger handle
    if sLoggerHandle == 'file':
        oLogHandle_1 = logging.FileHandler(sLoggerFile, 'w')
        oLogHandle_2 = logging.StreamHandler()

        # Set logger level
        oLogHandle_1.setLevel(logging.DEBUG)
        oLogHandle_2.setLevel(logging.DEBUG)

        # Set logger formatter
        oLogFormatter = logging.Formatter(sLoggerFormatter)
        oLogHandle_1.setFormatter(oLogFormatter)
        oLogHandle_2.setFormatter(oLogFormatter)

        # Add handle to logger
        oLoggerStream.addHandler(oLogHandle_1)
        oLoggerStream.addHandler(oLogHandle_2)

    elif sLoggerHandle == 'stream':
        oLogHandle = logging.StreamHandler()

        # Set logger level
        oLogHandle.setLevel(logging.DEBUG)

        # Set logger formatter
        oLogFormatter = logging.Formatter(sLoggerFormatter)
        oLogHandle.setFormatter(oLogFormatter)

        # Add handle to logger
        oLoggerStream.addHandler(oLogHandle)

    else:
        oLogHandle = logging.NullHandler()
        # Add handle to logger
        oLoggerStream.addHandler(oLogHandle)

    # Return logger stream
    return oLoggerStream

# -------------------------------------------------------------------------------------
