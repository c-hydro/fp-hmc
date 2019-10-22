"""
Class Features

Name:          drv_manager_arguments
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20161114'
Version:       '2.0.6'
"""

#######################################################################################
# Library
import logging

from copy import deepcopy

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_args import oConfigArgs as oConfigArgs_Default
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.utils.lib_utils_op_dict import getDictValues, DictObj
from hmc.utils.lib_utils_op_string import defineString

from hmc.utils.lib_utils_apps_tags import setRunTags
from hmc.utils.lib_utils_file_args import checkFileSettings, getDataSettings

from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Dictionary to define file to be selected from settings
oAttributesTags = ['FileLog', 'FileData']
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class to configure algorithm
class HMC_Arguments:

    # -------------------------------------------------------------------------------------
    # Variable(s)
    oDataSettings = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method time info
    def __init__(self, sFileSetting=oConfigArgs_Default['FileSetting'], sTime=oConfigArgs_Default['Time']):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.sFileSetting = sFileSetting
        self.sTimeArg = sTime
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to import argument(s)
    def importArgs(self):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Import argument(s) ... ')

        # Method to check settings file
        checkFileSettings(self.sFileSetting, oSettings=oDataSettings_Default)

        # Method to get data settings
        oDataSettings = getDataSettings(self.sFileSetting, oSettings=oDataSettings_Default)[0]
        # Method to get data tags
        oDataTags = setRunTags(oTags=oConfigTags_Default, oSettings=oDataSettings, oSkipTags=[])

        # Method to fill tags using tags
        oDataTags = self.__fillTags(oDataTags)

        # Define data settings object
        oDataSettings = DictObj(oDataSettings)

        # Define data settings attribute(s)
        for sAttributeName in oAttributesTags:
            oAttributeData = deepcopy(getDictValues(oDataSettings, sAttributeName, value=[]))[0]
            if isinstance(oAttributeData, str):
                setattr(oDataSettings, sAttributeName, defineString(oAttributeData, oDataTags))
            else:
                setattr(oDataSettings, sAttributeName, oAttributeData)

        # Info end
        oLogStream.info(' ---> Import argument(s) ... OK')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Return variable(s)
        return oDataSettings
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to fill tags using tags
    @staticmethod
    def __fillTags(oDataTags):
        oDataTags_Parser = {}
        for sKeyTags, oKeyData in oDataTags.items():
            if isinstance(list(oKeyData.values())[0], str):
                oDataTags_Parser[sKeyTags] = {list(oKeyData.keys())[0]: defineString(list(oKeyData.values())[0], oDataTags)}
            else:
                oDataTags_Parser[sKeyTags] = oKeyData
        return oDataTags_Parser
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
