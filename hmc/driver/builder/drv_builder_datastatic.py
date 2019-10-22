"""
Class Features

Name:          drv_builder_datastatic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
import numpy as np
from os.path import join, isfile

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_tags import oStaticTags as oStaticTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default

from hmc.utils.lib_utils_apps_tags import updateRunTags, mergeRunTags

from hmc.data_static.lib_datastatic_generic import getFileStaticPoint, getFileStaticGridded
from hmc.data_static.lib_datastatic_section import getFileStaticPointSection
from hmc.data_static.lib_datastatic_hydraulic_structure import getFileStaticPointDam, getFileStaticPointIntake

from hmc.utils.lib_utils_op_string import defineString

from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class Builder DataStatic
class HMC_Builder_DataStatic:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}

    oDataVarStatic = {}
    oDataForcingGridded_Info = {}

    oDataStaticGridded_INIT = {}
    oDataStaticPoint_INIT = {}

    oDataStaticGridded_RUN = {}
    oDataStaticPoint_RUN = {}
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, oDataSettings=oDataSettings_Default,
                 oDataTags=oConfigTags_Default, oDataVarStatic=oDataStatic_Default):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = oDataSettings
        self.oDataTags = oDataTags
        self.oDataVarStatic = oDataVarStatic

        self.oDataForcingGridded_Info = oDataSettings['ParamsInfo']['HMC_Data']

        self.oDataStaticGridded_INIT = oDataVarStatic['DataLand']['Gridded']
        self.oDataStaticPoint_INIT = oDataVarStatic['DataLand']['Point']

        self.oDataStaticGridded_RUN = oDataStatic_Default['DataAllocate']['Gridded']
        self.oDataStaticPoint_RUN = oDataStatic_Default['DataAllocate']['Point']
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get static file(s)
    def getFile(self):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Get static data ... ')

        # Method to get static point file(s)
        self.__getFileStaticPoint()
        # Method to get static gridded file(s)
        self.__getFileStaticGridded()

        # Method to set file static in structured workspace
        self.__setFileStatic()

        # Info end
        oLogStream.info(' ---> Get static data ... OK')

        return self.oDataVarStatic
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set static variable(s) to structured workspace
    def __setFileStatic(self):

        self.oDataVarStatic['DataAllocate']['Gridded'] = self.oDataStaticGridded_RUN
        self.oDataVarStatic['DataAllocate']['Point'] = self.oDataStaticPoint_RUN

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get file static point
    def __getFileStaticPoint(self):

        sFileName = self.oDataStaticPoint_INIT['FileName']
        sFilePath = self.oDataStaticPoint_INIT['FilePath']
        iFileType = self.oDataStaticPoint_INIT['FileType']
        oFileVars_IN = self.oDataStaticPoint_INIT['FileVars']
        oFileVars_OUT = self.oDataStaticPoint_INIT['FileVars']

        # Cycle(s) over variable(s)
        for sVarKey, oVarFeat in iter(oFileVars_IN.items()):

            sFileNameVar = join(sFilePath, sFileName)

            sVarName = oVarFeat['Name']
            bVarCheck = oVarFeat['AlgCheck']
            bVarReq = oVarFeat['AlgReq']

            oStaticTags = updateRunTags({'VarName': sVarName}, oStaticTags_Default)
            oTagsUpd = mergeRunTags(oStaticTags, self.oDataTags)
            sFileNameVar = defineString(sFileNameVar, oTagsUpd)

            if bVarCheck:
                if not isfile(sFileNameVar):
                    Exc.getExc(' =====> WARNING: fileName (' + sFileNameVar + ') '
                               'with flag algorithm check does not exist!', 2, 1)
            else:
                pass

            if bVarReq:

                if sVarKey == 'Dam':
                    oData = getFileStaticPointDam(sFileNameVar)
                elif sVarKey == 'Intake':
                    oData = getFileStaticPointIntake(sFileNameVar)
                else:
                    oData = getFileStaticPointSection(sFileNameVar)

                if sVarKey in oFileVars_OUT:
                    oDataVar_OUT = {}
                    try:
                        oDataVar_OUT['Data'] = oData
                        oDataVar_OUT['FileName'] = sFileNameVar

                        self.oDataStaticPoint_RUN['FileVars'][sVarKey] = oDataVar_OUT
                    except RuntimeError:
                        Exc.getExc(
                            ' =====> ERROR: variable (' + sVarKey + ') is not correctly loaded!', 1, 1)
                else:
                    Exc.getExc(' =====> WARNING: variable (' + sVarKey + ') does not exist in workspace!', 2, 1)
            else:
                pass

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get file static gridded
    def __getFileStaticGridded(self):

        # Get information
        sFileName = self.oDataStaticGridded_INIT['FileName']
        sFilePath = self.oDataStaticGridded_INIT['FilePath']
        iFileType = self.oDataStaticGridded_INIT['FileType']
        oFileVars_IN = self.oDataStaticGridded_INIT['FileVars']
        oFileVars_OUT = self.oDataStaticGridded_INIT['FileVars']

        oDataForcing_Info = self.oDataForcingGridded_Info

        # Cycle(s) over variable(s)
        for sVarKey, oVarFeat in iter(oFileVars_IN.items()):

            sFileNameVar = join(sFilePath, sFileName)

            sVarName = oVarFeat['Name']
            bVarCheck = oVarFeat['AlgCheck']
            bVarReq = oVarFeat['AlgReq']

            oStaticTags = updateRunTags({'VarName': sVarName}, oStaticTags_Default)
            oTagsUpd = mergeRunTags(oStaticTags, self.oDataTags)
            sFileNameVar = defineString(sFileNameVar, oTagsUpd)

            if bVarCheck:
                if not isfile(sFileNameVar):
                    Exc.getExc(' =====> WARNING: fileName (' + sFileNameVar + ') '
                               'with flag algorithm check does not exist!', 2, 1)
            else:
                pass

            if bVarReq:
                [a2dData, a2dGeoX, a2dGeoY, a1dGeoBox,
                 dGeoXStep, dGeoYStep, a1oGeoHeader] = getFileStaticGridded(sFileNameVar)
                if sVarKey in oFileVars_OUT:
                    oDataVar_OUT = {}
                    try:
                        oDataVar_OUT['Data'] = a2dData
                        oDataVar_OUT['FileName'] = sFileNameVar

                        self.oDataStaticGridded_RUN['FileVars'][sVarKey] = oDataVar_OUT

                        # Longitude
                        if (self.oDataStaticGridded_RUN['FileVars']['Longitude']['Data']) is None:
                            self.oDataStaticGridded_RUN['FileVars']['Longitude']['Data'] = a2dGeoX
                        else:
                            pass
                        # Latitude
                        if (self.oDataStaticGridded_RUN['FileVars']['Latitude']['Data']) is None:
                            self.oDataStaticGridded_RUN['FileVars']['Latitude']['Data'] = a2dGeoY
                        else:
                            pass
                        # Geographical box
                        if (self.oDataStaticGridded_RUN['FileVars']['Info']['GeoBox']) is None:
                            self.oDataStaticGridded_RUN['FileVars']['Info']['GeoBox'] = a1dGeoBox
                        else:
                            pass
                        # Geographical header
                        if (self.oDataStaticGridded_RUN['FileVars']['Info']['GeoHeader']) is None:
                            self.oDataStaticGridded_RUN['FileVars']['Info']['GeoHeader'] = a1oGeoHeader
                        else:
                            pass

                        # Extra values about forcing Data (using geographical header)
                        # Forcing Geo(example: a1dGeoForcing = 42.5206, 12.0418)
                        if (self.oDataStaticGridded_RUN['FileVars']['Info']['Forcing']['LLCorner']) is None:
                            # Get information (corner XllCorner, YllCorner)
                            if oDataForcing_Info['ForcingGridSwitch'] == 1:
                                if oDataForcing_Info['ForcingGeo'][0] > 0 and oDataForcing_Info['ForcingGeo'][1] > 0:
                                    a1dGeoForcing = np.array([oDataForcing_Info['ForcingGeo'][0],
                                                             oDataForcing_Info['ForcingGeo'][1]],
                                                             dtype=np.float32)
                                else:
                                    Exc.getExc(' =====> WARNING: grid switch selected '
                                               'but forcing geographical corner not defined!', 2, 1)
                                    a1dGeoForcing = np.array([-9999.0, -9999, 0], dtype=np.float32)

                            else:
                                a1dGeoForcing = np.array([a1oGeoHeader['yllcorner'],
                                                          a1oGeoHeader['xllcorner']],
                                                          dtype=np.float32)
                            # Set information
                            self.oDataStaticGridded_RUN['FileVars']['Info']['Forcing']['LLCorner'] = a1dGeoForcing
                        else:
                            pass

                        # Forcing Res (example: a1dResForcing = 0.003003, 0.003003)
                        if (self.oDataStaticGridded_RUN['FileVars']['Info']['Forcing']['Resolution']) is None:
                            # Get information (XRes, YRes)

                            if oDataForcing_Info['ForcingGridSwitch'] == 1:
                                if oDataForcing_Info['ForcingRes'][0] > 0 and oDataForcing_Info['ForcingRes'][1] > 0:
                                    a1dResForcing = np.array([oDataForcing_Info['ForcingRes'][0],
                                                             oDataForcing_Info['ForcingRes'][1]],
                                                             dtype=np.float32)
                                else:
                                    Exc.getExc(' =====> WARNING: grid switch selected'
                                               'but forcing resolutions not defined!', 2, 1)
                                    a1dResForcing = np.array([-9999.0, -9999, 0], dtype=np.float32)

                            else:
                                a1dResForcing = np.array([a1oGeoHeader['cellsize'],
                                                          a1oGeoHeader['cellsize']],
                                                          dtype=np.float32)
                            # Set information
                            self.oDataStaticGridded_RUN['FileVars']['Info']['Forcing']['Resolution'] = a1dResForcing
                        else:
                            pass

                        # Forcing Dims (example: a1iDimsForcing = 534, 643)
                        if (self.oDataStaticGridded_RUN['FileVars']['Info']['Forcing']['Dims']) is None:
                            # Get information (XDims, YDims)
                            if oDataForcing_Info['ForcingGridSwitch'] == 1:
                                if oDataForcing_Info['ForcingDims'][0] > 0 and oDataForcing_Info['ForcingDims'][1] > 0:
                                    a1iDimsForcing = np.array([oDataForcing_Info['ForcingDims'][0],
                                                               oDataForcing_Info['ForcingDims'][1]],
                                                               dtype=np.int32)
                                else:
                                    Exc.getExc(' =====> WARNING: grid switch selected'
                                               'but forcing dimensions not defined!', 2, 1)
                                    a1iDimsForcing = np.array([-9999, -9999], dtype=np.int32)

                            else:
                                a1iDimsForcing = np.array([a1oGeoHeader['nrows'],
                                                           a1oGeoHeader['ncols']],
                                                           dtype=np.int32)
                            # Set information
                            self.oDataStaticGridded_RUN['FileVars']['Info']['Forcing']['Dims'] = a1iDimsForcing
                        else:
                            pass

                        # Forcing ScaleFactor (example: iScaleFactor = 10)
                        if (self.oDataStaticGridded_RUN['FileVars']['Info']['Forcing']['ScaleFactor']) is None:
                            # Get information (XDims, YDims)
                            if oDataForcing_Info['ForcingGridSwitch'] == 1:
                                if oDataForcing_Info['ForcingScaleFactor'] > 0:
                                    iScaleFactorForcing = oDataForcing_Info['ForcingScaleFactor']
                                else:
                                    Exc.getExc(' =====> WARNING: grid switch selected'
                                               'but forcing scale factor not defined!', 2, 1)
                                    iScaleFactorForcing = -9999.0
                            else:
                                iScaleFactorForcing = 1
                            # Set information
                            self.oDataStaticGridded_RUN['FileVars']['Info']['Forcing']['ScaleFactor'] = iScaleFactorForcing

                        else:
                            pass

                    except RuntimeError:
                        Exc.getExc(
                            ' =====> ERROR: variable (' + sVarKey + ') is not correctly loaded!', 1, 1)
                else:
                    Exc.getExc(' =====> WARNING: variable (' + sVarKey + ') does not exist in workspace!', 2, 1)
            else:
                pass

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
