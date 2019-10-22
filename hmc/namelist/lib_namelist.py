"""
Library Features:

Name:          lib_namelist
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
from __future__ import print_function
from os.path import join
from numpy import asarray
import logging

from hmc.default.lib_default_args import sLoggerName
from hmc.default.lib_default_tags import oConfigTags as oConfigTags_Default

from hmc.default.lib_default_settings import oDataSettings as oDataSettings_Default

from hmc.default.lib_default_datastatic import oDataStatic as oDataStatic_Default
from hmc.default.lib_default_datadynamic import oDataDynamic as oDataDynamic_Default

from hmc.default.lib_default_namelist import oDataNamelist as oDataNamelist_Default

from hmc.default.lib_default_time import oDataTime as oDataTime_Default

from hmc.utils.lib_utils_op_dict import getDictValues
from hmc.utils.lib_utils_op_string import defineString
from hmc.utils.lib_utils_op_list import convertList2Str
from hmc.utils.lib_utils_op_var import printVarFormat

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to update namelist using settings Data
def updateData_NML(oDataSettings=oDataSettings_Default,
                   oDataTags=oConfigTags_Default,
                   oDataStatic=oDataStatic_Default,
                   oDataDynamic=oDataDynamic_Default,
                   oDataTime=oDataTime_Default,
                   oDataNamelist=oDataNamelist_Default):

    # Parameter(s) information --> average values
    oDataNamelist['HMC_Parameters']['dUc'] = oDataSettings['ParamsInfo']['HMC_Params']['Uc']
    oDataNamelist['HMC_Parameters']['dUh'] = oDataSettings['ParamsInfo']['HMC_Params']['Uh']
    oDataNamelist['HMC_Parameters']['dCt'] = oDataSettings['ParamsInfo']['HMC_Params']['Ct']
    oDataNamelist['HMC_Parameters']['dCf'] = oDataSettings['ParamsInfo']['HMC_Params']['Cf']
    oDataNamelist['HMC_Parameters']['dCPI'] = oDataSettings['ParamsInfo']['HMC_Params']['CPI']
    oDataNamelist['HMC_Parameters']['dKSatRatio'] = oDataSettings['ParamsInfo']['HMC_Params']['KSatRatio']
    oDataNamelist['HMC_Parameters']['dSlopeMax'] = oDataSettings['ParamsInfo']['HMC_Params']['SlopeMax']
    oDataNamelist['HMC_Parameters']['dWTableHbr'] = oDataSettings['ParamsInfo']['HMC_Params']['WTableHbr']
    oDataNamelist['HMC_Parameters']['sDomainName'] = oDataSettings['ParamsInfo']['Run_Params']['RunDomain']

    # Flag(s) information
    oDataNamelist['HMC_Namelist']['iFlagOs'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_OS']
    oDataNamelist['HMC_Namelist']['iFlagRestart'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_Restart']
    oDataNamelist['HMC_Namelist']['iFlagAlbedo'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_Albedo']
    oDataNamelist['HMC_Namelist']['iFlagDebugLevel'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_DebugLevel']
    oDataNamelist['HMC_Namelist']['iFlagDebugSet'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_DebugSet']
    oDataNamelist['HMC_Namelist']['iFlagVarDtPhysConv'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_DtPhysConv']
    oDataNamelist['HMC_Namelist']['iFlagFlowDeep'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_FlowDeep']
    oDataNamelist['HMC_Namelist']['iFlagLAI'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_LAI']
    oDataNamelist['HMC_Namelist']['iFlagSnow'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_Snow']
    oDataNamelist['HMC_Namelist']['iFlagSnowAssim'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_Snow_Assim']
    oDataNamelist['HMC_Namelist']['iFlagSMAssim'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_SM_Assim']
    oDataNamelist['HMC_Namelist']['iFlagCoeffRes'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_CoeffRes']
    oDataNamelist['HMC_Namelist']['iFlagWS'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_WS']
    oDataNamelist['HMC_Namelist']['iFlagReleaseMass'] = oDataSettings['ParamsInfo']['HMC_Flag']['Flag_ReleaseMass']

    # Dt information
    oDataNamelist['HMC_Namelist']['iDtModel'] = oDataSettings['ParamsInfo']['HMC_Dt']['Dt_Model']
    oDataNamelist['HMC_Namelist']['iDtPhysConv'] = oDataSettings['ParamsInfo']['HMC_Dt']['Dt_PhysConv']
    oDataNamelist['HMC_Namelist']['iScaleFactor'] = oDataSettings['ParamsInfo']['HMC_Data']['ForcingScaleFactor']
    oDataNamelist['HMC_Namelist']['iTcMax'] = oDataSettings['ParamsInfo']['Time_Params']['TimeTcMax']

    # DataStatic Information
    oDataNamelist['HMC_Namelist']['sPathData_Static_Point'] = oDataStatic['DataLand']['Point']['FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_Static'] = oDataStatic['DataLand']['Point']['FileType']
    oDataNamelist['HMC_Namelist']['sPathData_Static_Gridded'] = oDataStatic['DataLand']['Gridded']['FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_Static'] = oDataStatic['DataLand']['Gridded']['FileType']

    # DataDynamic Information
    oDataNamelist['HMC_Namelist']['sPathData_Forcing_Gridded'] = oDataDynamic['DataForcing']['Gridded']['FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_Forcing_Gridded'] = oDataDynamic['DataForcing']['Gridded']['FileType']
    oDataNamelist['HMC_Namelist']['sPathData_Forcing_Point'] = oDataDynamic['DataForcing']['Point']['FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_Forcing_Point'] = oDataDynamic['DataForcing']['Point']['FileType']
    oDataNamelist['HMC_Namelist']['sPathData_Forcing_TimeSeries'] = oDataDynamic['DataForcing']['TimeSeries'][
        'FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_Forcing_TimeSeries'] = oDataDynamic['DataForcing']['TimeSeries'][
        'FileType']

    oDataNamelist['HMC_Namelist']['sPathData_Updating_Gridded'] = oDataDynamic['DataUpdating']['Gridded'][
        'FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_Updating_Gridded'] = oDataDynamic['DataUpdating']['Gridded'][
        'FileType']

    oDataNamelist['HMC_Namelist']['sPathData_Output_Gridded'] = oDataDynamic['DataOutcome']['Gridded']['FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_Output_Gridded'] = oDataDynamic['DataOutcome']['Gridded']['FileType']
    oDataNamelist['HMC_Namelist']['sPathData_Output_Point'] = oDataDynamic['DataOutcome']['Point']['FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_Output_Point'] = oDataDynamic['DataOutcome']['Point']['FileType']
    oDataNamelist['HMC_Namelist']['sPathData_Output_TimeSeries'] = oDataDynamic['DataOutcome']['TimeSeries']['FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_Output_TimeSeries'] = oDataDynamic['DataOutcome']['TimeSeries'][
        'FileType']

    oDataNamelist['HMC_Namelist']['sPathData_Restart_Gridded'] = oDataDynamic['DataRestart']['Gridded']['FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_Restart_Gridded'] = oDataDynamic['DataRestart']['Gridded']['FileType']
    oDataNamelist['HMC_Namelist']['sPathData_Restart_Point'] = oDataDynamic['DataRestart']['Point']['FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_Restart_Point'] = oDataDynamic['DataRestart']['Point']['FileType']

    oDataNamelist['HMC_Namelist']['sPathData_State_Gridded'] = oDataDynamic['DataState']['Gridded']['FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_State_Gridded'] = oDataDynamic['DataState']['Gridded']['FileType']
    oDataNamelist['HMC_Namelist']['sPathData_State_Point'] = oDataDynamic['DataState']['Point']['FilePath']
    oDataNamelist['HMC_Namelist']['iFlagTypeData_State_Point'] = oDataDynamic['DataState']['Point']['FileType']

    # DataTime information
    oDataNamelist['HMC_Namelist']['sTimeRestart'] = oDataTime['DataTime']['TimeRestart']
    oDataNamelist['HMC_Namelist']['sTimeStart'] = oDataTime['DataTime']['TimeRun']
    oDataNamelist['HMC_Namelist']['iSimLength'] = oDataTime['DataTime']['SimLength']

    # Other information
    oDataNamelist['HMC_Namelist']['a1dGeoForcing'] = getDictValues(oDataStatic, 'LLCorner', [])[0]
    oDataNamelist['HMC_Namelist']['a1dResForcing'] = getDictValues(oDataStatic, 'Resolution', [])[0]
    oDataNamelist['HMC_Namelist']['a1iDimsForcing'] = getDictValues(oDataStatic, 'Dims', [])[0]

    return oDataNamelist

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to define namelist filename
def defineFile_NML(sFileName=join(oDataSettings_Default['ParamsInfo']['Run_Path']['PathExec'],
                                  oDataSettings_Default['ParamsInfo']['Run_VarExec']['RunModelNamelist']),
                   oDataTags=oConfigTags_Default):
    # Update filename using run tags
    sFileName_Tags = defineString(sFileName, oDataTags)
    return sFileName_Tags
# -------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to write namelist file
def writeFile_NML(sFileNML, oDataNML, sLineIndent=4 * ' '):

    # Write namelist file
    oFileNML = open(sFileNML, 'w')
    try:
        for oGrpName, oGrpVars in oDataNML.items():
            if isinstance(oGrpVars, list):
                for oVars in oGrpVars:
                    __writeGroup_NML(oFileNML, oGrpName, oVars, sLineIndent)
            else:
                __writeGroup_NML(oFileNML, oGrpName, oGrpVars, sLineIndent)
    finally:
        oFileNML.close()
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to write group namelist
def __writeGroup_NML(oFileNML, oGrpName, oVars, sLineIndent):

    # Write group in namelist file
    print('&{0}'.format(oGrpName), file=oFileNML)

    # Cycle(s) over variable(s) and value(s)
    for oVName, oVValue in sorted(oVars.items()):

        if isinstance(oVValue, list):
            # Reduce number precision (if needed)
            a1oValue = printVarFormat(asarray(oVValue))
            sLine = __writeLine_NML(oVName, a1oValue)
            sLine = sLineIndent + sLine
            print('{0}'.format(sLine), file=oFileNML)
        elif isinstance(oVValue, str):
            sLine = __writeLine_NML(oVName, oVValue)
            sLine = sLineIndent + sLine
            print('{0}'.format(sLine), file=oFileNML)
        else:
            sLine = __writeLine_NML(oVName, oVValue)
            sLine = sLineIndent + sLine
            print('{0}'.format(sLine), file=oFileNML)

    print('/', file=oFileNML)

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to write line namelist
def __writeLine_NML(oVName, oVValue):

    # Check variable value type
    if isinstance(oVValue, str):
        sVValue = oVValue
        sVValue = '"' + sVValue + '"'
    elif isinstance(oVValue, int):
        sVValue = str(int(oVValue))
    elif isinstance(oVValue, float):
        sVValue = str(float(oVValue))
    elif isinstance(oVValue, list):
        sVValue = convertList2Str(oVValue, ',')
    else:
        sVValue = str(oVValue)

    # Line definition in Fortran style
    sLine = str(oVName) + ' = ' + sVValue
    return sLine

# --------------------------------------------------------------------------------
