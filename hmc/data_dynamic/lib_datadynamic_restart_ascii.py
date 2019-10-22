"""
Class Features

Name:          lib_datadynamic_restart_ascii
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""
#######################################################################################
# Library
import logging
import time

from copy import deepcopy
from os.path import join, exists, split

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_tags import oDynamicTags as oDynamicTags_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default

from hmc.time.lib_time import computeTimeArrival

from hmc.utils.lib_utils_apps_tags import updateRunTags, mergeRunTags
from hmc.utils.lib_utils_apps_file import handleFileData
from hmc.utils.lib_utils_op_string import defineString
from hmc.utils.lib_utils_op_system import createFolder, copyFile

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to get restart point Data (in ASCII format)
def getRestartPoint_ASCII(sDataTime, sRunMode='Deterministic', sDataFlag='ARCHIVE', sRefTime=None, iWaitTime=10,
                          oDataTags=oConfigTags_Default,
                          oDataGridded=oDataDynamic_Default['DataRestart']['Gridded'],
                          sPathTemp='/temp'):

    # -------------------------------------------------------------------------------------
    # Get global information
    oFileDyn = oDataGridded['FileVars'][sDataFlag]
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Cycle(s) over variable(s)
    oDataCheck_OUT = {}
    for sVarKey, oVarData in iter(oFileDyn['VarName'].items()):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... ')
        oDataCheck_OUT[sVarKey] = False
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute time arrival (used for nwp model selection)
        if sRefTime:
            a1sArrTime = computeTimeArrival(sRefTime,
                                            oFileDyn['VarArrival']['Day'], oFileDyn['VarArrival']['Hour'])
        else:
            a1sArrTime = computeTimeArrival(sDataTime,
                                            oFileDyn['VarArrival']['Day'], oFileDyn['VarArrival']['Hour'])
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Define filename and search file(s)
        a1sFileNotFound = []
        for sArrTime in sorted(a1sArrTime, reverse=True):

            # -------------------------------------------------------------------------------------
            # Define state file
            sFileName_State = join(oVarData['FilePath'], oVarData['FileName'])
            sVarName_State = oVarData['FileVar']

            oStateTags = updateRunTags({'Year': sArrTime[0:4],
                                          'Month': sArrTime[4:6], 'Day': sArrTime[6:8],
                                          'Hour': sArrTime[8:10], 'Minute': sArrTime[10:12],
                                          'RunMode': sRunMode, 'VarName': sVarName_State},
                                          deepcopy(oDynamicTags_Default))
            oStateTagsUpd = mergeRunTags(oStateTags, oDataTags)
            sFileName_State = defineString(sFileName_State, oStateTagsUpd)
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Define restart file
            sFileName_Restart = join(oDataGridded['FilePath'], oDataGridded['FileName'])

            oRestartTags = updateRunTags({'Year': sArrTime[0:4],
                                          'Month': sArrTime[4:6], 'Day': sArrTime[6:8],
                                          'Hour': sArrTime[8:10], 'Minute': sArrTime[10:12],
                                          'RunMode': sRunMode, 'VarName': sVarName_State},
                                          deepcopy(oDynamicTags_Default))
            oRestartTagsUpd = mergeRunTags(oRestartTags, oDataTags)
            sFileName_Restart = defineString(sFileName_Restart, oRestartTagsUpd)
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Search selected file
            if sFileName_State != '':
                if exists(sFileName_State):
                    bFileFound = True
                    break
                else:
                    a1sFileNotFound.append(sFileName_State)
                    bFileFound = False
            else:
                a1sFileNotFound.append(sVarKey + '_' + sArrTime)
                bFileFound = False
            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Check file zipped availability
        if bFileFound is True:

            # -------------------------------------------------------------------------------------
            # Unzip, open file (with waiting time to avoid issue(s) with parallel runs)
            bFileOpen = False
            iTimeOut = time.time() + iWaitTime
            while bFileOpen is False:

                # -------------------------------------------------------------------------------------
                # Handle Data file
                [oFileHandle, oFileDriver, bFileOpen] = handleFileData(sFileName_State, sPathTemp)
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # TimeOut
                if time.time() > iTimeOut:
                    Exc.getExc(' =====> WARNING: unable to open file ' + sFileName_State + '!', 2, 1)
                elif bFileOpen is False:
                    oLogStream.info(
                        ' ---> Waiting to open file: ' + sFileName_State + ' ... '
                        'probably different processes attempt to access the same file!')
                else:
                    pass
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Check file opening
            if bFileOpen:

                # -------------------------------------------------------------------------------------
                # Create restart folder (if not available)
                createFolder(split(sFileName_Restart)[0])
                # Copy restart file from source to destination folder
                copyFile(sFileName_State, sFileName_Restart)
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Info end
                oLogStream.info(' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... OK')
                oDataCheck_OUT[sVarKey] = True
                # -------------------------------------------------------------------------------------

            else:

                # -------------------------------------------------------------------------------------
                # Exit for issues in opening file
                oLogStream.info(' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... SKIP! '
                                'File not correctly open!')
                Exc.getExc(' =====> WARNING: file not correctly open!', 2, 1)
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

        else:

            # -------------------------------------------------------------------------------------
            # Condition file not found
            oLogStream.info(
                ' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... FAILED! File(s) not found!')
            Exc.getExc(' =====> WARNING: file(s) ' + str(a1sFileNotFound) + ' are not found!', 2, 1)
            # -------------------------------------------------------------------------------------

    # End variable(s) cycle(s)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Return value
    return oDataCheck_OUT
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
