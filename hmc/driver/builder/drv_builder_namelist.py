"""
Class Features

Name:          drv_builder_namelist
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
from os.path import join

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default
from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default
from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default
from hmc.default.lib_default_time import oDataTime as oDataTime_Default
from hmc.default.lib_default_namelist import oDataNamelist as oDataNamelist_Default
from hmc.default.lib_default_namelist import sFileNamelist as sFileNamelist_Default

from hmc.namelist.lib_namelist import updateData_NML, defineFile_NML, writeFile_NML

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Class Builder Namelist
class HMC_Builder_Namelist:

    # -------------------------------------------------------------------------------------
    # Classes variable(s)
    oDataSettings = {}
    oDataTags = {}
    oDataVarStatic = {}
    oDataVarDynamic = {}
    oDataTime = {}

    oDataNML = {}
    sFileNML = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method ClassInit
    def __init__(self, oDataSettings=oDataSettings_Default,
                 oDataTags=oConfigTags_Default,
                 oDataVarStatic=oDataStatic_Default,
                 oDataVarDynamic=oDataDynamic_Default,
                 oDataTime=oDataTime_Default,
                 oDataNamelist=oDataNamelist_Default,
                 sFileNamelist=sFileNamelist_Default):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.oDataSettings = oDataSettings
        self.oDataTags = oDataTags
        self.oDataVarStatic = oDataVarStatic
        self.oDataVarDynamic = oDataVarDynamic
        self.oDataTime = oDataTime

        self.oDataNML = oDataNamelist
        self.sFileNML = sFileNamelist

        # Format
        self.__LineIndent = 4 * ' '
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to write namelist file
    def writeNML(self, sRunMode, oRunArgs):

        # -------------------------------------------------------------------------------------
        # Info start
        oLogStream.info(' ---> Write namelist file ... ')

        # Method to update namelist values
        self.oDataNML = updateData_NML(self.oDataSettings, self.oDataTags,
                                        self.oDataVarStatic, self.oDataVarDynamic,
                                        self.oDataTime,
                                        self.oDataNML)

        # Method to define namelist filename
        self.sFileNML = defineFile_NML(join(self.oDataSettings['ParamsInfo']['Run_Path']['PathExec'],
                                            self.oDataSettings['ParamsInfo']['Run_VarExec']['RunModelNamelist']),
                                       self.oDataTags)

        # Method to write namelist file
        writeFile_NML(self.sFileNML, self.oDataNML, self.__LineIndent)

        # Info end
        oLogStream.info(' ---> Write namelist file ... OK')

        # Return variable to global workspace
        return self.sFileNML, self.oDataNML
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
