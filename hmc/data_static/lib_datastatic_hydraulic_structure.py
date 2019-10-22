"""
Library Features:

Name:          lib_datastatic_hydraulic_structure
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging

from hmc.default.lib_default_args import sLoggerName

from hmc.io.lib_data_io_ascii import openFile, closeFile, getVar, getLines

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

class DictCustom(dict):
    pass

def parseLineContent(oLine, sLineDelimiter='#'):

    sLine = oLine.split(sLineDelimiter)[0]

    # Check delimiter character (in intake file info there are both '#' and '%')
    if ('#' not in oLine) and ('%' in sLine):
        sLine = oLine.split('%')[0]

    sLine = sLine.strip()

    return sLine

# -------------------------------------------------------------------------------------
# Method to get file static point dam
def getFileStaticPointDam(sFileName, sLineDelimiter='#'):

    oFile = openFile(sFileName, 'r')
    oContent = getLines(oFile)
    closeFile(oFile)

    iRows_Count = 0
    iNDam = int(oContent[iRows_Count].split(sLineDelimiter)[0])
    iRows_Count += 1
    iNPlant = int(oContent[iRows_Count].split(sLineDelimiter)[0])

    oDamDict = DictCustom()
    oConnectionDict = DictCustom()
    oDamList = []
    oPlantList = []
    oDamPlantList = []
    for iDam in range(0, iNDam):
        iRows_Count += 1
        sCommentLine = parseLineContent(oContent[iRows_Count], sLineDelimiter)
        iRows_Count += 1
        sDamName = parseLineContent(oContent[iRows_Count], sLineDelimiter)
        iRows_Count += 1
        a1iDamIJ = list(map(int, parseLineContent(oContent[iRows_Count], sLineDelimiter).split()))
        iRows_Count += 1
        iDamPlantN = int(parseLineContent(oContent[iRows_Count], sLineDelimiter))
        iRows_Count += 1
        iDamCellLakeCode = int(parseLineContent(oContent[iRows_Count], sLineDelimiter))
        iRows_Count += 1
        dDamVMax = float(parseLineContent(oContent[iRows_Count], sLineDelimiter))
        iRows_Count += 1
        dDamVInit = float(parseLineContent(oContent[iRows_Count], sLineDelimiter))
        iRows_Count += 1
        dDamQMax = float(parseLineContent(oContent[iRows_Count], sLineDelimiter))
        iRows_Count += 1
        dDamLMax = float(parseLineContent(oContent[iRows_Count], sLineDelimiter))
        iRows_Count += 1
        dDamHMax = float(parseLineContent(oContent[iRows_Count], sLineDelimiter))
        iRows_Count += 1
        dDamLinCoeff = float(parseLineContent(oContent[iRows_Count], sLineDelimiter))
        iRows_Count += 1
        sDamCurveName = parseLineContent(oContent[iRows_Count], sLineDelimiter)

        # Store data
        sDamKey = 'Dam_{:}'.format(sDamName)
        oDamDict[sDamKey] = {}
        oDamDict[sDamKey]['Dam_Name'] = sDamName
        oDamDict[sDamKey]['Dam_IJ'] = a1iDamIJ
        oDamDict[sDamKey]['Dam_PlantN'] = iDamPlantN
        oDamDict[sDamKey]['Dam_LakeCode'] = iDamCellLakeCode
        oDamDict[sDamKey]['Dam_VMax'] = dDamVMax
        oDamDict[sDamKey]['Dam_VInit'] = dDamVInit
        oDamDict[sDamKey]['Dam_QMax'] = dDamQMax
        oDamDict[sDamKey]['Dam_LMax'] = dDamLMax
        oDamDict[sDamKey]['Dam_HMax'] = dDamHMax
        oDamDict[sDamKey]['Dam_LinCoeff'] = dDamLinCoeff
        oDamDict[sDamKey]['Dam_StorageCurve'] = sDamCurveName

        oDamList.append(sDamName)
        oDamPlantList.append(sDamName)
        oConnectionDict[sDamName] = {}

        oDamPlantConnection = []
        for iPlant in range(0, int(iDamPlantN)):
            iRows_Count += 1
            sPlantName = parseLineContent(oContent[iRows_Count], sLineDelimiter)
            iRows_Count += 1
            a1iPlantIJ = list(map(int, parseLineContent(oContent[iRows_Count], sLineDelimiter).split()))
            iRows_Count += 1
            iPlantTc = int(parseLineContent(oContent[iRows_Count], sLineDelimiter))
            iRows_Count += 1
            dPlantQMax = float(parseLineContent(oContent[iRows_Count], sLineDelimiter))
            iRows_Count += 1
            iPlantQFlag = int(parseLineContent(oContent[iRows_Count], sLineDelimiter))

            # Store data
            sPlantKey = 'Plant_{:}'.format(sPlantName)
            oDamDict[sDamKey][sPlantKey] = {}
            oDamDict[sDamKey][sPlantKey]['Plant_Name'] = sPlantName
            oDamDict[sDamKey][sPlantKey]['Plant_IJ'] = a1iPlantIJ
            oDamDict[sDamKey][sPlantKey]['Plant_Tc'] = iPlantTc
            oDamDict[sDamKey][sPlantKey]['Plant_QMax'] = dPlantQMax
            oDamDict[sDamKey][sPlantKey]['Plant_QFlag'] = iPlantQFlag

            oPlantList.append(sPlantName)
            oDamPlantConnection.append(sPlantName)

        oDamPlantList.append(oDamPlantConnection)
        oConnectionDict[sDamName] = oDamPlantConnection

    oDamDict.dam_suffix = 'Dam_{:}'
    oDamDict.plant_suffix = 'Plant_{:}'
    oDamDict.dam_list = oDamList
    oDamDict.plant_list = oPlantList
    oDamDict.connections = oConnectionDict

    return oDamDict

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get file static point intake
def getFileStaticPointIntake(sFileName, sLineDelimiter='#'):

    oFile = openFile(sFileName, 'r')
    oContent = getLines(oFile)
    closeFile(oFile)

    iRows_Count = 0
    iNCatch = int(oContent[iRows_Count].split(sLineDelimiter)[0])
    iRows_Count += 1
    iNRelease = int(oContent[iRows_Count].split(sLineDelimiter)[0])

    oIntakeDict = DictCustom()
    oConnectionDict = DictCustom()
    oReleaseList = []
    oCatchList = []
    oReleaseCatchList = []
    for iRelease in range(0, iNRelease):
        iRows_Count += 1
        sReleaseName = parseLineContent(oContent[iRows_Count], sLineDelimiter)
        iRows_Count += 1
        a1iReleaseIJ = list(map(int, parseLineContent(oContent[iRows_Count], sLineDelimiter).split()))
        iRows_Count += 1
        iReleaseCatchN = int(parseLineContent(oContent[iRows_Count], sLineDelimiter))

        # Store data
        sReleaseKey = 'Release_{:}'.format(sReleaseName)
        oIntakeDict[sReleaseKey] = {}
        oIntakeDict[sReleaseKey]['Release_Name'] = sReleaseName
        oIntakeDict[sReleaseKey]['Release_IJ'] = a1iReleaseIJ
        oIntakeDict[sReleaseKey]['Release_CatchN'] = iReleaseCatchN

        oReleaseList.append(sReleaseName)
        oReleaseCatchList.append(sReleaseName)
        oConnectionDict[sReleaseName] = {}

        oReleaseCatchConnection = []
        for iCatch in range(0, int(iReleaseCatchN)):
            iRows_Count += 1
            sCatchName = parseLineContent(oContent[iRows_Count], sLineDelimiter)
            iRows_Count += 1
            iCatchTc = int(parseLineContent(oContent[iRows_Count], sLineDelimiter))
            iRows_Count += 1
            a1iCatchIJ = list(map(int, parseLineContent(oContent[iRows_Count], sLineDelimiter).split()))
            iRows_Count += 1
            dCatchQMax = float(parseLineContent(oContent[iRows_Count], sLineDelimiter))
            iRows_Count += 1
            dCatchQMin = float(parseLineContent(oContent[iRows_Count], sLineDelimiter))
            iRows_Count += 1
            dCatchQWeight = float(parseLineContent(oContent[iRows_Count], sLineDelimiter))

            # Store data
            sCatchKey = 'Catch_{:}'.format(sCatchName)
            oIntakeDict[sReleaseKey][sCatchKey] = {}
            oIntakeDict[sReleaseKey][sCatchKey]['Catch_Name'] = sCatchName
            oIntakeDict[sReleaseKey][sCatchKey]['Catch_IJ'] = a1iCatchIJ
            oIntakeDict[sReleaseKey][sCatchKey]['Catch_Tc'] = iCatchTc
            oIntakeDict[sReleaseKey][sCatchKey]['Catch_QMax'] = dCatchQMax
            oIntakeDict[sReleaseKey][sCatchKey]['Catch_QMin'] = dCatchQMin
            oIntakeDict[sReleaseKey][sCatchKey]['Catch_QWeight'] = dCatchQWeight

            oCatchList.append(sCatchName)
            oReleaseCatchConnection.append(sCatchName)

        oReleaseCatchList.append(oReleaseCatchConnection)
        oConnectionDict[sReleaseName] = oReleaseCatchConnection

    oIntakeDict.release_suffix = 'Release_{:}'
    oIntakeDict.catch_suffix = 'Catch_{:}'
    oIntakeDict.release_list = oReleaseList
    oIntakeDict.catch_list = oCatchList
    oIntakeDict.connections = oConnectionDict

    return oIntakeDict

# -------------------------------------------------------------------------------------
