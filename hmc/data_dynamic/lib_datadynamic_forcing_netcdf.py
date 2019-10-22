"""
Class Features

Name:          lib_datadynamic_forcing_netcdf
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""
#######################################################################################
# Library
import logging
import time
import numpy as np
from copy import deepcopy
from os.path import join, exists, split

from hmc.default.lib_default_args import sLoggerName, sZipExt
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_tags import oDynamicTags as oDynamicTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default

from hmc.utils.lib_utils_apps_tags import updateRunTags, mergeRunTags
from hmc.utils.lib_utils_apps_file import handleFileData
from hmc.time.lib_time import computeTimeArrival

from hmc.utils.lib_utils_apps_file import selectFileDriver
from hmc.utils.lib_utils_apps_time import getTimeSteps
from hmc.utils.lib_utils_apps_zip import deleteFileUnzip, addExtZip, getExtZip
from hmc.utils.lib_utils_op_string import defineString
from hmc.utils.lib_utils_op_system import createFolder, deleteFileName, copyFile
from hmc.utils.lib_utils_op_dict import mergeDict, removeDictKey
from hmc.utils.lib_utils_op_list import reduceListUnique

from hmc.driver.data.drv_data_io_zip import Drv_Data_Zip
from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to get gridded data forecast
def getForcingGridded_For_NC(sDataTime, sRunMode='Deterministic', sDataFlag='FOR', sRefTime=None, iWaitTime=10,
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

    # Get variable(s) operation(s)
    if 'VarOp' in oFileVars_IN:
        oDataOp_OUT = np.any(list(oFileVars_IN['VarOp'].values()))
    else:
        oDataOp_OUT = True
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Cycle(s) over variable(s)
    oDataCheck_OUT = {}
    oFileCheck_OUT = {}
    for sVarKey, oVarData in iter(oFileVars_IN['VarName'].items()):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... ')
        oDataCheck_OUT[sVarKey] = False
        oFileCheck_OUT[sVarKey] = None
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
        bFileFound = False
        sFileNameDyn = None
        sVarNameDyn = None
        sArrTime = None
        for sArrTime in sorted(a1sArrTime, reverse=True):

            # Check file and variable definition(s)
            if oVarData['FilePath'] and oVarData['FileName'] and oVarData['FileVar']:

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
                        oLogStream.info(' ----> File selected: ' + sFileNameDyn)
                        bFileFound = True
                        oFileCheck_OUT[sVarKey] = sFileNameDyn
                        break
                    else:
                        a1sFileNotFound.append(sFileNameDyn)
                        Exc.getExc(' =====> WARNING: file selected ' + sFileNameDyn + ' NOT FOUND! '
                                   'Try to use an older file!', 2, 1)
                        bFileFound = False
                        oFileCheck_OUT[sVarKey] = None
                else:
                    a1sFileNotFound.append(sVarKey + '_' + sArrTime)
                    Exc.getExc(' =====> WARNING: impossible to select a file! Try to use an older file!', 2, 1)
                    bFileFound = False
                    oFileCheck_OUT[sVarKey] = None

            else:
                Exc.getExc(' =====> WARNING: impossible to select a file! File or variable definition are null!', 2, 1)
                a1sFileNotFound.append(sVarKey + '_' + sArrTime)
                bFileFound = False
                oFileCheck_OUT[sVarKey] = None

        # Info about file dynamic initialized as null
        if sFileNameDyn is None:
            Exc.getExc(' =====> WARNING: impossible to select a file! Time arrival is null!', 2, 1)
            bFileFound = False
            oFileCheck_OUT[sVarKey] = None
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Check data merging condition
        if oDataOp_OUT:

            # -------------------------------------------------------------------------------------
            # Check file zipped availability
            if bFileFound is True:

                # Unzip, open file (with waiting time to avoid issue(s) with parallel runs)
                bFileOpen = False
                oFileDriver = None
                oFileHandle = None
                iTimeOut = time.time() + iWaitTime
                while bFileOpen is False:

                    # -------------------------------------------------------------------------------------
                    # Handle Data file
                    [oFileHandle, oFileDriver, bFileOpen] = handleFileData(sFileNameDyn, sPathTemp)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # TimeOut
                    if (time.time() > iTimeOut) and (bFileOpen is False):
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
                # Check variable availability
                if oFileDriver.oFileLibrary.checkVarName(oFileHandle, sVarNameDyn):

                    # -------------------------------------------------------------------------------------
                    # Get variable information
                    [_, _, iVarDim, _] = oFileDriver.oFileLibrary.getVarInfo(oFileHandle, sVarNameDyn)
                    # Get variable attributes
                    oVarAttrs = oFileDriver.oFileLibrary.getVarAttrs(oFileHandle, sVarNameDyn)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check current time step related with file time period
                    a1oTimeCheck = getTimeSteps(sTimeFrom=sArrTime, sTimeTo=sDataTime,
                                                iTimeDelta=oFileVars_IN['VarResolution'])
                    iTimeCheckLen = len(a1oTimeCheck[1:])
                    iTimeDataLen = oFileVars_IN['VarStep']
                    if iTimeCheckLen > iTimeDataLen:
                        bTimeCheck = False
                    else:
                        bTimeCheck = True
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Get time index to identify var slice)
                    a1oTime = oFileDriver.oFileLibrary.getTime(oFileHandle)
                    if bTimeCheck is True:
                        if a1oTime:     # Time correctly defined in netCDF file
                            try:
                                iIndexTime = a1oTime.index(sDataTime)
                            except RuntimeWarning:
                                Exc.getExc(
                                    ' =====> WARNING: time step is not in file time period! Index time is null!', 2, 1)
                                iIndexTime = None

                        else:           # Time not defined in netCDF file
                            Exc.getExc(' =====> WARNING: time period is not defined in input file! '
                                       'Index time is computed in default mode! Check for errors!', 2, 1)
                            a1oTimePeriod = getTimeSteps(sTimeFrom=sArrTime,
                                                         iTimeDelta=oFileVars_IN['VarResolution'],
                                                         iTimeStep=oFileVars_IN['VarStep'])
                            iIndexTime = a1oTimePeriod[1:-1].index(sDataTime)
                    else:
                        iIndexTime = None
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check index time definition
                    if iIndexTime is not None:

                        # -------------------------------------------------------------------------------------
                        # Get 2d or 3d variable Data
                        if iVarDim == 2:
                            oData = oFileDriver.oFileLibrary.get2DVar(oFileHandle, sVarNameDyn,
                                                                      bSetAutoMask=False)
                        elif iVarDim == 3:
                            oData = oFileDriver.oFileLibrary.get3DVar(oFileHandle, sVarNameDyn,
                                                                      iIndexTime, bSetAutoMask=False)
                        else:
                            Exc.getExc(
                                ' =====> WARNING: variable dimension(s) are not allowed. Check your data!', 2, 1)
                            oData = None
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
                                # Store attributes information (if available)
                                if oVarAttrs:
                                    oDataVar_OUT['Attrs'] = oVarAttrs
                                else:
                                    pass
                                # Store variable information
                                oDataGridded_OUT['FileVars'][sDataFlag][sVarKey] = oDataVar_OUT
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Store Terrain information
                                if (oDataGridded_OUT['FileVars'][sDataFlag]['Terrain']['Data']) is None:
                                    try:
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Terrain']['Data'] = \
                                            oFileStatic['Terrain']['Data']
                                    except RuntimeWarning:
                                        Exc.getExc(
                                            ' =====> WARNING: variable Terrain does not save in workspace!', 2, 1)
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Terrain']['Data'] = None
                                else:
                                    pass
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Store Longitude information
                                if (oDataGridded_OUT['FileVars'][sDataFlag]['Longitude']['Data']) is None:
                                    try:
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Longitude']['Data'] = \
                                            oFileStatic['Longitude']['Data']
                                    except RuntimeWarning:
                                        Exc.getExc(
                                            ' =====> WARNING: variable Longitude does not save in workspace!', 2, 1)
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Longitude']['Data'] = None
                                else:
                                    pass
                                # Store Latitude information
                                if (oDataGridded_OUT['FileVars'][sDataFlag]['Latitude']['Data']) is None:
                                    try:
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Latitude']['Data'] = \
                                            oFileStatic['Latitude']['Data']
                                    except RuntimeWarning:
                                        Exc.getExc(
                                            ' =====> WARNING: variable Latitude does not save in workspace!', 2, 1)
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Latitude']['Data'] = None
                                else:
                                    pass
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Store GeoBox information
                                if (oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoBox']) is None:
                                    try:
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoBox'] = \
                                            oFileStatic['Info']['GeoBox']
                                    except RuntimeWarning:
                                        Exc.getExc(
                                            ' =====> WARNING: variable GeoBox does not save in workspace!', 2, 1)
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoBox'] = None
                                else:
                                    pass

                                # Store GeoHeader information
                                if (oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoHeader']) is None:
                                    try:
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoHeader'] = \
                                            oFileStatic['Info']['GeoHeader']
                                    except RuntimeWarning:
                                        Exc.getExc(
                                            ' =====> WARNING: variable GeoHeader does not save in workspace!', 2, 1)
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoHeader'] = None
                                else:
                                    pass
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Info end
                                oLogStream.info(' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... OK')
                                oDataCheck_OUT[sVarKey] = True
                                # -------------------------------------------------------------------------------------

                            except RuntimeError:

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
                        # Check time definition
                        if bTimeCheck is True:

                            # -------------------------------------------------------------------------------------
                            # Variable is not defined in output workspace
                            oLogStream.info(
                                ' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... FAILED! '
                                'Variable not found in output workspace!')
                            Exc.getExc(
                                ' =====> WARNING: variable ' + sVarKey + ' index time is not correctly defined!', 2, 1)
                            # -------------------------------------------------------------------------------------

                        else:
                            # -------------------------------------------------------------------------------------
                            # Exit in get variable
                            oLogStream.info(
                                ' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... SKIP! '
                                'Variable is not available because time step is greater than time period!')
                            # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------

                else:

                    # -------------------------------------------------------------------------------------
                    # Condition variable is not found in input file
                    oLogStream.info(
                        ' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... FAILED! '
                        'Variable not found in input file!')
                    Exc.getExc(' =====> WARNING: variable ' + sVarKey + ' does not exist in input file!', 2, 1)
                    # -------------------------------------------------------------------------------------

            else:

                # -------------------------------------------------------------------------------------
                # Condition file not found
                oLogStream.info(
                    ' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... FAILED! File(s) not found!')
                Exc.getExc(' =====> WARNING: file(s) ' + str(a1sFileNotFound) + ' are not found!', 2, 1)
                # -------------------------------------------------------------------------------------

        else:
            # -------------------------------------------------------------------------------------
            # Condition with merging data not activated
            oDataGridded_OUT[sVarKey] = None
            oDataCheck_OUT[sVarKey] = True
            # -------------------------------------------------------------------------------------

    # End variable(s) cycle(s)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Return value
    return oDataGridded_OUT, oDataCheck_OUT, oFileCheck_OUT, oDataOp_OUT
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get gridded data observed
def getForcingGridded_Obs_NC(sDataTime, sRunMode='Deterministic', sDataFlag='OBS', sRefTime=None, iWaitTime=10,
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

    # Get variable(s) operation(s)
    if 'VarOp' in oFileVars_IN:
        oDataOp_OUT = np.any(list(oFileVars_IN['VarOp'].values()))
    else:
        oDataOp_OUT = True
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Cycle(s) over variable(s)
    oDataCheck_OUT = {}
    oFileCheck_OUT = {}
    for sVarKey, oVarData in iter(oFileVars_IN['VarName'].items()):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... ')
        oDataCheck_OUT[sVarKey] = False
        oFileCheck_OUT[sVarKey] = None
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
        bFileFound = False
        sFileNameDyn = None
        sVarNameDyn = None
        sArrTime = None
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
                    oLogStream.info(' ----> File selected: ' + sFileNameDyn)
                    bFileFound = True
                    oFileCheck_OUT[sVarKey] = sFileNameDyn
                    break
                else:

                    Exc.getExc(' =====> WARNING: file selected ' + sFileNameDyn + ' NOT FOUND! '
                               'Try to use an older file!', 2, 1)
                    a1sFileNotFound.append(sFileNameDyn)
                    bFileFound = False
                    oFileCheck_OUT[sVarKey] = None
            else:
                a1sFileNotFound.append(sVarKey + '_' + sArrTime)
                Exc.getExc(' =====> WARNING: impossible to select a file! Try to use an older file!', 2, 1)
                bFileFound = False
                oFileCheck_OUT[sVarKey] = None

        # Info about file dynamic initialized as null
        if sFileNameDyn is None:
            Exc.getExc(' =====> WARNING: impossible to select a file! Time arrival is null!', 2, 1)
            bFileFound = False
            oFileCheck_OUT[sVarKey] = None
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Check data merging condition
        if oDataOp_OUT:

            # -------------------------------------------------------------------------------------
            # Check file zipped availability
            if bFileFound:

                # -------------------------------------------------------------------------------------
                # Unzip, open file (with waiting time to avoid issue(s) with parallel runs)
                bFileOpen = False
                oFileDriver = None
                oFileHandle = None
                iTimeOut = time.time() + iWaitTime
                while bFileOpen is False:

                    # -------------------------------------------------------------------------------------
                    # Handle Data file
                    [oFileHandle, oFileDriver, bFileOpen] = handleFileData(sFileNameDyn, sPathTemp)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # TimeOut
                    if (time.time() > iTimeOut) and (bFileOpen is False):
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
                # Check variable availability
                if oFileDriver.oFileLibrary.checkVarName(oFileHandle, sVarNameDyn):

                    # -------------------------------------------------------------------------------------
                    # Get variable information
                    [_, _, iVarDim, _] = oFileDriver.oFileLibrary.getVarInfo(oFileHandle, sVarNameDyn)
                    # Get variable attributes
                    oVarAttrs = oFileDriver.oFileLibrary.getVarAttrs(oFileHandle, sVarNameDyn)
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check current time step related with file time period
                    a1oTimeCheck = getTimeSteps(sTimeFrom=sArrTime, sTimeTo=sDataTime,
                                                iTimeDelta=oFileVars_IN['VarResolution'])
                    iTimeCheckLen = len(a1oTimeCheck[1:])
                    iTimeDataLen = oFileVars_IN['VarStep']
                    if iTimeCheckLen > iTimeDataLen:
                        bTimeCheck = False
                    else:
                        bTimeCheck = True
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Get time index to identify var slice)
                    a1oTime = oFileDriver.oFileLibrary.getTime(oFileHandle)
                    if bTimeCheck is True:
                        if a1oTime:     # Time correctly defined in netCDF file
                            try:
                                iIndexTime = a1oTime.index(sDataTime)
                            except BaseException:
                                Exc.getExc(
                                    ' =====> WARNING: time step is not in file time period! Index time is null!', 2, 1)
                                iIndexTime = None

                        else:           # Time not defined in netCDF file
                            Exc.getExc(' =====> WARNING: time period is not defined in input file! '
                                       'Index time is computed in default mode! Check for errors!', 2, 1)
                            a1oTimePeriod = getTimeSteps(sTimeFrom=sArrTime,
                                                         iTimeDelta=oFileVars_IN['VarResolution'],
                                                         iTimeStep=oFileVars_IN['VarStep'])
                            iIndexTime = a1oTimePeriod[1:-1].index(sDataTime)
                    else:
                        iIndexTime = None
                    # -------------------------------------------------------------------------------------

                    # -------------------------------------------------------------------------------------
                    # Check index time definition
                    if iIndexTime is not None:

                        # Get 2d or 3d variable Data
                        if iVarDim == 2:
                            oData = oFileDriver.oFileLibrary.get2DVar(oFileHandle, sVarNameDyn,
                                                                      bSetAutoMask=False)
                        elif iVarDim == 3:
                            oData = oFileDriver.oFileLibrary.get3DVar(oFileHandle, sVarNameDyn,
                                                                      iIndexTime, bSetAutoMask=False)
                        else:
                            Exc.getExc(
                                ' =====> WARNING: variable dimension(s) are not allowed. Check your data!', 2, 1)
                            oData = None
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
                                # Store attributes information (if available)
                                if oVarAttrs:
                                    oDataVar_OUT['Attrs'] = oVarAttrs
                                else:
                                    pass
                                # Store variable information
                                oDataGridded_OUT['FileVars'][sDataFlag][sVarKey] = oDataVar_OUT
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Store Terrain information
                                if (oDataGridded_OUT['FileVars'][sDataFlag]['Terrain']['Data']) is None:
                                    try:
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Terrain']['Data'] = \
                                            oFileStatic['Terrain']['Data']
                                    except BaseException:
                                        Exc.getExc(
                                            ' =====> WARNING: variable Terrain does not save in workspace!', 2, 1)
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Terrain']['Data'] = None
                                else:
                                    pass
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Store Longitude information
                                if (oDataGridded_OUT['FileVars'][sDataFlag]['Longitude']['Data']) is None:
                                    try:
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Longitude']['Data'] = \
                                            oFileStatic['Longitude']['Data']
                                    except BaseException:
                                        Exc.getExc(
                                            ' =====> WARNING: variable Longitude does not save in workspace!', 2, 1)
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Longitude']['Data'] = None
                                else:
                                    pass
                                # Store Latitude information
                                if (oDataGridded_OUT['FileVars'][sDataFlag]['Latitude']['Data']) is None:
                                    try:
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Latitude']['Data'] = \
                                            oFileStatic['Latitude']['Data']
                                    except BaseException:
                                        Exc.getExc(
                                            ' =====> WARNING: variable Latitude does not save in workspace!', 2, 1)
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Latitude']['Data'] = None
                                else:
                                    pass
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Store GeoBox information
                                if (oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoBox']) is None:
                                    try:
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoBox'] = \
                                            oFileStatic['Info']['GeoBox']
                                    except BaseException:
                                        Exc.getExc(
                                            ' =====> WARNING: variable GeoBox does not save in workspace!', 2, 1)
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoBox'] = None
                                else:
                                    pass

                                # Store GeoHeader information
                                if (oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoHeader']) is None:
                                    try:
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoHeader'] = \
                                            oFileStatic['Info']['GeoHeader']
                                    except BaseException:
                                        Exc.getExc(
                                            ' =====> WARNING: variable GeoHeader does not save in workspace!', 2, 1)
                                        oDataGridded_OUT['FileVars'][sDataFlag]['Info']['GeoHeader'] = None
                                else:
                                    pass
                                # -------------------------------------------------------------------------------------

                                # -------------------------------------------------------------------------------------
                                # Info end
                                oLogStream.info(' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... OK')
                                oDataCheck_OUT[sVarKey] = True
                                # -------------------------------------------------------------------------------------

                            except BaseException:

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
                            Exc.getExc(
                                ' =====> WARNING: variable ' + sVarKey + ' does not define in output workspace!', 2, 1)
                            # -------------------------------------------------------------------------------------

                    else:
                        # -------------------------------------------------------------------------------------
                        # Check time definition
                        if bTimeCheck is True:

                            # -------------------------------------------------------------------------------------
                            # Variable is not defined in output workspace
                            oLogStream.info(
                                ' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... FAILED! '
                                'Variable not found in output workspace!')
                            Exc.getExc(
                                ' =====> WARNING: variable ' + sVarKey + ' index time is not correctly defined!', 2, 1)
                            # -------------------------------------------------------------------------------------

                        else:
                            # -------------------------------------------------------------------------------------
                            # Exit in get variable
                            oLogStream.info(
                                ' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... SKIP! '
                                'Variable is not available because time step is greater than time period!')
                            # -------------------------------------------------------------------------------------

                        # -------------------------------------------------------------------------------------
                else:

                    # -------------------------------------------------------------------------------------
                    # Condition variable is not found in input file
                    oLogStream.info(
                        ' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... FAILED! '
                        'Variable not found in input file!')
                    Exc.getExc(' =====> WARNING: variable ' + sVarKey + ' does not exist in input file!', 2, 1)
                    # -------------------------------------------------------------------------------------

            else:
                # -------------------------------------------------------------------------------------
                # Condition file not found
                oLogStream.info(
                    ' ---> Get Variable [' + sDataFlag + ']: ' + sVarKey + ' ... FAILED! File(s) not found!')
                Exc.getExc(' =====> WARNING: file(s) ' + str(a1sFileNotFound) + ' are not found!', 2, 1)
                # -------------------------------------------------------------------------------------

        else:
            # -------------------------------------------------------------------------------------
            # Condition with merging data not activated
            oDataGridded_OUT[sVarKey] = None
            oDataCheck_OUT[sVarKey] = True
            # -------------------------------------------------------------------------------------

    # End variable(s) cycle(s)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Return value
    return oDataGridded_OUT, oDataCheck_OUT, oFileCheck_OUT, oDataOp_OUT
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to copy gridded data
def copyForcingGridded_NC(sDataTime, sFileName_OUT,
                          oFileName_IN,
                          sRunMode='Deterministic', sRunType='OBS',
                          oDataSettings=oDataSettings_Default,
                          oDataTags=oConfigTags_Default):

    # -------------------------------------------------------------------------------------
    # Define filename IN
    oFileName_IN_LIST = []
    for sVarName, sVarFile in oFileName_IN.items():
        oFileName_IN_LIST.append(sVarFile)

    oFileName_IN_VAR = reduceListUnique(oFileName_IN_LIST)

    if oFileName_IN_VAR.__len__() == 1:
        sFileName_IN_VAR = oFileName_IN_VAR[0]
        [sZipType_IN_VAR, bZipType_IN_VAR] = getExtZip(sFileName_IN_VAR)
    else:
        sZipType_IN_VAR = None
        bZipType_IN_VAR = None
        sFileName_IN_VAR = None
        Exc.getExc(' =====> ERROR: variable(s) merging not activated, two or more file(s) declared in settings.', 1, 1)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Define filename OUT
    oDynamicTags = updateRunTags({'Year': sDataTime[0:4],
                                  'Month': sDataTime[4:6], 'Day': sDataTime[6:8],
                                  'Hour': sDataTime[8:10], 'Minute': sDataTime[10:12],
                                  'RunMode': sRunMode},
                                 deepcopy(oDynamicTags_Default))
    oTagsUpd = mergeRunTags(oDynamicTags, oDataTags)

    # Update filename
    sFileName_OUT_VAR = defineString(sFileName_OUT, oTagsUpd)
    [_, bZipType_OUT_VAR] = getExtZip(sFileName_OUT_VAR)

    if bZipType_IN_VAR and not bZipType_OUT_VAR:
        sFileName_OUT_VAR = addExtZip(sFileName_OUT_VAR, sZipType_IN_VAR)[0]

    # Create destination folder (if not available)
    createFolder(split(sFileName_OUT_VAR)[0])
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Copy file from source to outcome folder (from data to run folder)
    try:
        copyFile(sFileName_IN_VAR, sFileName_OUT_VAR)
        return True
    except BaseException:
        return False
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to save gridded Data
def saveForcingGridded_NC(sDataTime, sFileName,
                          sRunMode='Deterministic', sRunType='OBS',
                          oDataSettings=oDataSettings_Default,
                          oDataTags=oConfigTags_Default,
                          oDataGridded=oDataDynamic_Default['DataAllocate']['Gridded']):

    # -------------------------------------------------------------------------------------
    # Get global information
    oFileVars = oDataGridded['FileVars'][sRunType]
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Define filename
    oDynamicTags = updateRunTags({'Year': sDataTime[0:4],
                                  'Month': sDataTime[4:6], 'Day': sDataTime[6:8],
                                  'Hour': sDataTime[8:10], 'Minute': sDataTime[10:12],
                                  'RunMode': sRunMode},
                                 deepcopy(oDynamicTags_Default))
    oTagsUpd = mergeRunTags(oDynamicTags, oDataTags)
    # Update filename
    sFileNameVar = defineString(sFileName, oTagsUpd)

    # Create destination folder (if not available)
    createFolder(split(sFileNameVar)[0])
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Time information
    a1oDataTime = [sDataTime]
    iLenTime = 1
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Open netCDF file in write/append mode according with availability of selected file
    oDrv_IO = selectFileDriver(sFileNameVar, sZipExt)
    oFile = oDrv_IO.oFileLibrary.openFile(join(oDrv_IO.sFilePath, oDrv_IO.sFileName), oDrv_IO.sFileMode)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Declare variable dimensions
    # Dimension X
    sVarX = 'X'
    if oDrv_IO.oFileLibrary.checkDimName(oFile, sVarX) is False:
        oDrv_IO.oFileData = oDrv_IO.oFileLibrary.writeDims(oFile,
                                                           sVarX, np.int32(oFileVars['Info']['GeoHeader']['ncols']))
    # Dimension Y
    sVarY = 'Y'
    if oDrv_IO.oFileLibrary.checkDimName(oFile, sVarY) is False:
        oDrv_IO.oFileData = oDrv_IO.oFileLibrary.writeDims(oFile,
                                                           sVarY, np.int32(oFileVars['Info']['GeoHeader']['nrows']))
    # Dimension Time
    sVarT = 'time'
    if oDrv_IO.oFileLibrary.checkDimName(oFile, sVarT) is False:
        oDrv_IO.oFileData = oDrv_IO.oFileLibrary.writeDims(oFile, sVarT, iLenTime)
    # Dimension N simulations
    sVarNSim = 'nsim'
    if oDrv_IO.oFileLibrary.checkDimName(oFile, sVarNSim) is False:
        oDrv_IO.oFileData = oDrv_IO.oFileLibrary.writeDims(oFile, sVarNSim, 1)
    # Dimension N times
    sVarNTime = 'ntime'
    if oDrv_IO.oFileLibrary.checkDimName(oFile, sVarNTime) is False:
        oDrv_IO.oFileData = oDrv_IO.oFileLibrary.writeDims(oFile, sVarNTime, 2)
    # Dimension N ensembles
    sVarNEns = 'nens'
    if oDrv_IO.oFileLibrary.checkDimName(oFile, sVarNEns) is False:
        oDrv_IO.oFileData = oDrv_IO.oFileLibrary.writeDims(oFile, sVarNEns, 1)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Write time information
    if oDrv_IO.oFileLibrary.checkVarName(oFile, sVarT) is False:
        oDrv_IO.oFileData = oDrv_IO.oFileLibrary.writeTime(oFile, a1oDataTime, 'f8', 'time', iLenTime / iLenTime)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Write GeneralInfo attributes
    if 'GeneralInfo' in oDataSettings:
        # Define extra fields to add in saving procedure
        oDataExtra = mergeDict(oFileVars['Info']['GeoHeader'], {'FileName': split(sFileNameVar)[1]})
        # Define general info with extra field(s)
        oGeneralInfo = mergeDict(oDataSettings['GeneralInfo'], oDataExtra)
        # Check general info attribute(s)
        if not np.all(oDrv_IO.oFileLibrary.checkAttrName(oFile, oGeneralInfo)) is True:
            # Save general info attribute(s)
            oDrv_IO.oFileData = oDrv_IO.oFileLibrary.writeFileAttrs(oFile, oGeneralInfo)
    else:
        pass

    # Write GeoSystemInfo attributes
    if 'GeoSystemInfo' in oDataSettings:
        # Define bounding box in a suitable format
        a1oGeoBox = oFileVars['Info']['GeoBox'].tolist()
        # Define geosystem info with extra field(s)
        oGeoSystemInfo = mergeDict(oDataSettings['GeoSystemInfo'], {'bounding_box': a1oGeoBox})
        # Check general info attribute(s)
        if not np.all(oDrv_IO.oFileLibrary.checkAttrName(oFile, oGeoSystemInfo)) is True:
            # Save geographical system attribute(s)
            oDrv_IO.oFileData = oDrv_IO.oFileLibrary.writeGeoSystem(oFile, oGeoSystemInfo)
    else:
        pass
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Cycle(s) over variable(s)
    oFileVars = removeDictKey(oFileVars, ['Info'])
    for sVarName, oVarValue in iter(oFileVars.items()):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Save Variable [' + sRunType + ']: ' + sVarName + ' ... ')

        # Check Data availability
        if oVarValue['Data'] is not None:

            # -------------------------------------------------------------------------------------
            # Check variable existence in nc file
            if oDrv_IO.oFileLibrary.checkVarName(oFile, sVarName) is False:

                # -------------------------------------------------------------------------------------
                # Save Variable(s)
                oDrv_IO.oFileData = oDrv_IO.oFileLibrary.write2DVar(oFile,
                                                                    sVarName, oVarValue['Data'],
                                                                    oVarValue['Attrs'], 'f4', sVarY, sVarX)

                # Info exit (ok)
                oLogStream.info(' ---> Save Variable [' + sRunType + ']: ' + sVarName + ' ... OK')
                # -------------------------------------------------------------------------------------
            else:
                # -------------------------------------------------------------------------------------
                # Info exit (ok)
                oLogStream.info(' ---> Save Variable [' + sRunType + ']: ' +
                                sVarName + ' ... SKIP. VARIABLE ALREADY SET IN FILE!')
                # -------------------------------------------------------------------------------------
        else:
            # -------------------------------------------------------------------------------------
            # Info exit (skip)
            oLogStream.info(' ---> Save Variable [' + sRunType + ']: ' +
                            sVarName + ' ... SKIP. VARIABLE IS NULL!')
            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Close netCDF file
    oDrv_IO.oFileLibrary.closeFile(oFile)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Check zipped file previously generated
    if exists(addExtZip(sFileNameVar, sZipExt)[0]) is True:
        deleteFileName(addExtZip(sFileNameVar, sZipExt)[0])
    # Zip file
    oDrv_ZIP = Drv_Data_Zip(sFileNameVar, 'z', None, sZipExt).oFileWorkspace
    [oFile_ZIP, oFile_UNZIP] = oDrv_ZIP.oFileLibrary.openZip(oDrv_ZIP.sFileName_IN,
                                                             oDrv_ZIP.sFileName_OUT,
                                                             oDrv_ZIP.sZipMode)
    oDrv_ZIP.oFileLibrary.zipFile(oFile_ZIP, oFile_UNZIP)
    oDrv_ZIP.oFileLibrary.closeZip(oFile_ZIP, oFile_UNZIP)

    # Delete uncompressed file
    deleteFileUnzip(oDrv_ZIP.sFileName_IN, True)
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
