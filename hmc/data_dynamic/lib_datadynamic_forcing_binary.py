"""
Class Features

Name:          lib_datadynamic_forcing_binary
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
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default

from hmc.time.lib_time import computeTimeArrival

from hmc.utils.lib_utils_apps_tags import updateRunTags, mergeRunTags
from hmc.utils.lib_utils_apps_file import handleFileData
from hmc.utils.lib_utils_op_string import defineString
from hmc.utils.lib_utils_op_system import createFolder, copyFile
from hmc.utils.lib_utils_op_dict import removeDictKey

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to get gridded Data in binary format
def getForcingGridded_Binary(sDataTime, sRunMode='Deterministic', sDataFlag='OBS', sRefTime=None, iWaitTime=10,
                             oDataTags=oConfigTags_Default,
                             oDataStatic=oDataStatic_Default['DataAllocate']['Gridded'],
                             oDataGridded_IN=oDataDynamic_Default['DataForcing']['Gridded'],
                             oDataGridded_OUT=oDataDynamic_Default['DataAllocate']['Gridded'],
                             sPathTemp='/temp'):

    # -------------------------------------------------------------------------------------
    # Get global information
    oFileVars_IN = oDataGridded_IN['FileVars'][sDataFlag]
    oFileVars_OUT = oDataGridded_OUT['FileVars'][sDataFlag]

    oFileStatic = oDataStatic['FileVars']
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Cycle(s) over variable(s)
    oDataCheck_OUT = {}
    for sVarKey, oVarData in oFileVars_IN['VarName'].items():

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... ')
        oDataCheck_OUT[sVarKey] = False
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute time arrival (used for nwp model selection)
        if sRefTime:
            a1sArrTime = computeTimeArrival(sRefTime,
                                            oFileVars_IN['VarArrival']['Day'], oFileVars_IN['VarArrival']['Hour'])
        else:
            a1sArrTime = computeTimeArrival(sDataTime,
                                            oFileVars_IN['VarArrival']['Day'], oFileVars_IN['VarArrival']['Hour'])
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Define filename and search file(s)
        a1sFileNotFound = []
        for sArrTime in sorted(a1sArrTime, reverse=True):

            sFileNameDyn = join(oVarData['FilePath'], oVarData['FileName'])
            sVarNameDyn = oVarData['FileVar']

            oDynamicTags = updateRunTags({'Year': sArrTime[0:4],
                                          'Month': sArrTime[4:6], 'Day': sArrTime[6:8],
                                          'Hour': sArrTime[8:10], 'Minute': sArrTime[10:12],
                                          'RunMode': sRunMode},
                                          deepcopy(oDynamicTags_Default))
            oTagsUpd = mergeRunTags(oDynamicTags, oDataTags)

            sFileNameDyn = defineString(sFileNameDyn, oTagsUpd)

            # Search selected file
            if sFileNameDyn != '':
                if exists(sFileNameDyn):
                    bFileFound = True
                    break
                else:
                    a1sFileNotFound.append(sFileNameDyn)
                    bFileFound = False
            else:
                a1sFileNotFound.append(sVarKey + '_' + sArrTime)
                bFileFound = False
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Check file zipped availability
        if bFileFound is True:

            # Unzip, open file (with waiting time to avoid issue(s) with parallel runs)
            bFileOpen = False
            iTimeOut = time.time() + iWaitTime
            while bFileOpen is False:

                # -------------------------------------------------------------------------------------
                # Handle Data file
                [oFileHandle, oFileDriver, bFileOpen] = handleFileData(sFileNameDyn, sPathTemp)
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # TimeOut
                if time.time() > iTimeOut:
                    Exc.getExc(' =====> WARNING: unable to open file ' + sFileNameDyn + '!', 2, 1)
                elif bFileOpen is False:
                    oLogStream.info(
                        ' ---> Waiting to open file: ' + sFileNameDyn + ' ... '
                        'probably different processes attempt to access the same file!')
                else:
                    pass
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # Check file opening
            if bFileOpen:

                # -------------------------------------------------------------------------------------
                # Get 2d variable Data
                a1iDataDims = oFileStatic['Info']['Forcing']['Dims']
                iScaleFactor = oFileStatic['Info']['Forcing']['ScaleFactor']
                oData = oFileDriver.oFileLibrary.get2DVar(oFileHandle, a1iDataDims[0], a1iDataDims[1], iScaleFactor)
                # -------------------------------------------------------------------------------------

                # -------------------------------------------------------------------------------------
                # Check variable selection in output workspace
                if sVarKey in oFileVars_OUT:

                    # -------------------------------------------------------------------------------------
                    # Initialize store workspace
                    oDataVar_OUT = {}
                    try:

                        # -------------------------------------------------------------------------------------
                        # Store variable information
                        oDataVar_OUT['Data'] = oData
                        # Store filename information
                        oDataVar_OUT['FileName'] = sFileNameDyn
                        # Store variable name information
                        oDataVar_OUT['VarName'] = sVarNameDyn
                        # Store variable information
                        oDataGridded_OUT['FileVars'][sDataFlag][sVarKey] = oDataVar_OUT
                        # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                        # Info end
                        oLogStream.info(' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... OK')
                        oDataCheck_OUT[sVarKey] = True
                        # -------------------------------------------------------------------------------------

                    except:

                        # -------------------------------------------------------------------------------------
                        # Error in get variable
                        oLogStream.info(
                            ' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... FAILED! '
                                                                                   'Variable is not correctly loaded!')
                        Exc.getExc(' =====> ERROR: variable ' + sVarKey + ' is not correctly loaded!', 1, 1)
                        # -------------------------------------------------------------------------------------

                else:

                    # -------------------------------------------------------------------------------------
                    # Variable is not defined in output workspace
                    oLogStream.info(
                        ' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... FAILED! '
                                                                               'Variable not found in output workspace!')
                    Exc.getExc(' =====> WARNING: variable ' + sVarKey + ' '
                                                                        'does not define in output workspace!', 2, 1)
                    # -------------------------------------------------------------------------------------

            else:

                # -------------------------------------------------------------------------------------
                # Exit for issues in opening file
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
    return oDataGridded_OUT, oDataCheck_OUT
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to save gridded Data in binary format
def saveForcingGridded_Binary(sDataTime, sFileName,
                                  sRunMode='Deterministic', sRunType='OBS',
                                  oDataSettings=oDataSettings_Default,
                                  oDataTags=oConfigTags_Default,
                                  oDataGridded=oDataDynamic_Default['DataAllocate']['Gridded']):

    # -------------------------------------------------------------------------------------
    # Get global information
    oFileVars = oDataGridded['FileVars'][sRunType]
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Define filename using time and run information
    oDynamicTags = updateRunTags({'Year': sDataTime[0:4],
                                  'Month': sDataTime[4:6], 'Day': sDataTime[6:8],
                                  'Hour': sDataTime[8:10], 'Minute': sDataTime[10:12],
                                  'RunMode': sRunMode},
                                  deepcopy(oDynamicTags_Default))
    oTags = mergeRunTags(oDynamicTags, oDataTags)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Cycle(s) over variable(s)
    oFileVars = removeDictKey(oFileVars, ['Info'])
    for sVarName, oVarValue in oFileVars.iteritems():

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Save Variable [' + sRunType + ']: ' + sVarName + ' ... ')

        # Check Data availability
        if oVarValue['Data'] is not None:

            # -------------------------------------------------------------------------------------
            # Define filename using variable information
            oTagsVar = updateRunTags({'VarName': oVarValue['VarName']}, deepcopy(oTags))

            # Get filename source
            sFileNameDyn_Source = oVarValue['FileName']
            # Get filename destination
            sFileNameDyn_Dest = defineString(sFileName, oTagsVar)

            # Create destination folder (if not available)
            createFolder(split(sFileNameDyn_Dest)[0])
            # Copy forcing file from source to destination folder
            copyFile(sFileNameDyn_Source, sFileNameDyn_Dest)

            # Info exit (ok)
            oLogStream.info(' ---> Save Variable [' + sRunType + ']: ' + sVarName + ' ... OK')
            # -------------------------------------------------------------------------------------

        else:

            # -------------------------------------------------------------------------------------
            # Info exit (skip)
            oLogStream.info(' ---> Save Variable [' + sRunType + ']: ' + sVarName + ' ... SKIP. VARIABLE IS NULL!')
            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
