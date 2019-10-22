"""
Library Features:

Name:          lib_utils_apps_tag
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
from __future__ import print_function
import logging

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default

from hmc.utils.lib_utils_op_dict import getDictDeep

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# --------------------------------------------------------------------------------
# Method to set running tags
def setRunTags(oTags=oConfigTags_Default, oSettings=oDataSettings_Default, oSkipTags=None):

    if oSkipTags is None:
        oSkipTags = []

    for sTagKey, oTagValue in iter(oTags.items()):

        if sTagKey not in oSkipTags:

            oSetValue = getDictDeep(oSettings, sTagKey)
            sSetKey = list(oTagValue.keys())[0]
            oTagValueUpd = {sSetKey: oSetValue}
            oTags[sTagKey] = oTagValueUpd

        else:
            pass

    return oTags
# # --------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to merge run tags
def mergeRunTags(oTags1, oTags2):

    oTagsComplete = {}
    for sKey1, oValue1 in iter(oTags1.items()):
        oTagsComplete[sKey1] = oValue1
    for sKey2, oValue2 in iter(oTags2.items()):
        if sKey2 in oTagsComplete:
            if oTagsComplete[sKey2] is None:
                if oValue2:
                    oTagsComplete[sKey2] = oValue2
                else:
                    pass
            else:
                pass
        else:
            oTagsComplete[sKey2] = oValue2

    return oTagsComplete
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to update run tags
def updateRunTags(oDict, oTags):

    for sDictKey, oDictValue in iter(oDict.items()):

        if sDictKey in oTags.keys():
            oValue = oTags[sDictKey]
            oGetTag = list(oValue.keys())[0]
            oTagUpd = {oGetTag: oDictValue}

            oTags[sDictKey] = oTagUpd

        else:

            if not sDictKey.startswith('$'):
                sDictTag = '$' + sDictKey
            else:
                sDictTag = sDictKey
            oTags[sDictKey] = {sDictTag: oDictValue}

    return oTags
# -------------------------------------------------------------------------------------
