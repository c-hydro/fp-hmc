"""
Library Features:

Name:          lib_utils_apps_file
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging
import json
from os.path import exists, split, join

from hmc.utils.lib_utils_apps_zip import getExtZip, addExtZip, removeExtZip

from hmc.default.lib_default_args import sLoggerName

from hmc.utils.lib_utils_op_system import createFolder, deleteFolder, copyFile, deleteFileName, createTemp

from hmc.driver.data.drv_data_io_type import Drv_Data_IO
from hmc.driver.data.drv_data_io_zip import Drv_Data_Zip
from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to import file in dictionary format
def importFileDict(sFileName):

    if exists(sFileName):
        try:
            # Read configuration file in json format
            with open(sFileName, 'r') as oFile:
                oFileData = json.load(oFile)

            oFileDict = {}
            for sFileKey, oFileData in oFileData.items():
                if not sFileKey.startswith('__'):
                    oFileDict[sFileKey] = oFileData
                else:
                    pass

            bFileData = True
        except BaseException:
            Exc.getExc(' =====> WARNING: read file ' + sFileName + ' FAILED!', 2, 1)
            oFileDict = None
            bFileData = False
    else:
        Exc.getExc(' =====> WARNING: file ' + sFileName + ' NOT FOUND!', 2, 1)
        oFileDict = None
        bFileData = False

    return oFileDict, bFileData
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Select file driver according with file status (existent, zipped or unzipped)
def selectFileDriver(sFileName, sZipExt=None):

    # -------------------------------------------------------------------------------------
    # Check zip extension of filename
    bZipExt = getExtZip(sFileName)[1]

    if bZipExt is False:
        sFileZip = addExtZip(sFileName, sZipExt)[0]
        sFileUnzip = sFileName
    else:
        sFileZip = sFileName
        sFileUnzip = removeExtZip(sFileName, sZipExt)[0]
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Check file availability on disk
    oFileDriver = None
    if (not exists(sFileUnzip)) and (not exists(sFileZip)):

        # -------------------------------------------------------------------------------------
        # Open non existent file
        try:
            # Open file in write mode
            oFileDriver = Drv_Data_IO(sFileUnzip, 'w').oFileWorkspace

        except BaseException:
            # Exception
            Exc.getExc(' =====> ERROR: driver selection to open file ' +
                       sFileName + ' FAILED! Errors in opening file in write mode!', 1, 1)
        # -------------------------------------------------------------------------------------

    elif exists(sFileZip):

        # -------------------------------------------------------------------------------------
        # Unzip and open existent file
        try:
            # Get source file path and name
            sFile_Source = sFileZip

            # Get destination file path and name
            sPathName_Destination = createTemp(None)
            sFileName_Destination = sFileZip
            sFile_Destination = join(sPathName_Destination, sFileName_Destination)

            # Copy file in temporary folder (to manage multiprocess file request)
            copyFile(sFile_Source, sFile_Destination)

            # Open zip driver
            oZipDriver = Drv_Data_Zip(sFile_Destination, 'u', None, sZipExt).oFileWorkspace
            [oFile_ZIP, oFile_UNZIP] = oZipDriver.oFileLibrary.openZip(oZipDriver.sFileName_IN,
                                                                       oZipDriver.sFileName_OUT,
                                                                       oZipDriver.sZipMode)
            oZipDriver.oFileLibrary.unzipFile(oFile_ZIP, oFile_UNZIP)
            oZipDriver.oFileLibrary.closeZip(oFile_ZIP, oFile_UNZIP)

            # Open unzipped file in append mode
            oFileDriver = Drv_Data_IO(oZipDriver.sFileName_OUT, 'a').oFileWorkspace

        except BaseException:
            # Exception
            Exc.getExc(' =====> ERROR: driver selection to unzip or open file ' +
                       sFileZip + ' FAILED! Errors in unzipping or opening file in append mode!', 1, 1)
        # -------------------------------------------------------------------------------------

    elif exists(sFileUnzip):

        # -------------------------------------------------------------------------------------
        # Open existent file
        try:
            # Open unzipped file in append mode
            oFileDriver = Drv_Data_IO(sFileUnzip, 'a').oFileWorkspace
        except BaseException:
            # Exception
            Exc.getExc(' =====> ERROR: driver selection open file ' +
                       sFileUnzip + ' FAILED! Errors in opening file in append mode!', 1, 1)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Return file handling
    return oFileDriver
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to handle file Data (in netCDF, binary and ASCII formats)
def handleFileData(sFileName, sPathTemp=None):

    # -------------------------------------------------------------------------------------
    # Check file availability on disk
    if exists(sFileName):

        # -------------------------------------------------------------------------------------
        # Create temporary folder to copy file from source (to manage multiprocess request)
        sFolderTemp = createTemp(sPathTemp)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get source file path and name
        [sPathName_Source, sFileName_Source] = split(sFileName)
        sFile_Source = join(sPathName_Source, sFileName_Source)

        # Get destination file path and name
        sPathName_Destination = join(sPathTemp, sFolderTemp)
        sFileName_Destination = sFileName_Source

        sFile_Destination = join(sPathName_Destination, sFileName_Destination)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Create destination folder (if needed)
        createFolder(sPathName_Destination)
        # Copy file in temporary folder (to manage multiprocess file request)
        copyFile(sFile_Source, sFile_Destination)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get zip extension (if exists)
        [sZipType_Destination, bZipType_Destination] = getExtZip(sFile_Destination)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Check file is compressed or not
        if bZipType_Destination is True:

            # -------------------------------------------------------------------------------------
            # Check script for zipped file
            try:

                # -------------------------------------------------------------------------------------
                # Unzip file
                oZipDriver = Drv_Data_Zip(sFile_Destination, 'u', None, sZipType_Destination).oFileWorkspace
                [oFile_ZIP, oFile_UNZIP] = oZipDriver.oFileLibrary.openZip(oZipDriver.sFileName_IN,
                                                                           oZipDriver.sFileName_OUT,
                                                                           oZipDriver.sZipMode)
                oZipDriver.oFileLibrary.unzipFile(oFile_ZIP, oFile_UNZIP)
                oZipDriver.oFileLibrary.closeZip(oFile_ZIP, oFile_UNZIP)

                # Open unzipped file
                oFileDriver = Drv_Data_IO(oZipDriver.sFileName_OUT).oFileWorkspace
                oFileHandle = oFileDriver.oFileLibrary.openFile(oZipDriver.sFileName_OUT, 'r')
                bFileOpen = True

                # Delete unzipped file
                deleteFileName(oZipDriver.sFileName_OUT)

                # Delete zipped temporary file
                deleteFileName(sFile_Destination)
                # Delete temporary folder
                deleteFolder(sPathName_Destination)
                # -------------------------------------------------------------------------------------

            except BaseException:

                # -------------------------------------------------------------------------------------
                # Exit for errors in unzip or open file
                Exc.getExc(' =====> WARNING: handle file ' + sFileName + ' FAILED! '
                           'Errors in unzipping or opening file!', 2, 1)
                oFileDriver = None
                oFileHandle = None
                bFileOpen = False
                # -------------------------------------------------------------------------------------

        else:

            # -------------------------------------------------------------------------------------
            # Check script for normal file
            try:

                # -------------------------------------------------------------------------------------
                # Open file
                oFileDriver = Drv_Data_IO(sFile_Destination).oFileWorkspace
                oFileHandle = oFileDriver.oFileLibrary.openFile(sFile_Destination, 'r')
                bFileOpen = True

                # Delete zipped temporary file
                deleteFileName(sFile_Destination)
                # Delete temporary folder
                deleteFolder(sPathName_Destination)
                # -------------------------------------------------------------------------------------

            except BaseException:

                # -------------------------------------------------------------------------------------
                # Exit for errors in read file
                Exc.getExc(' =====> WARNING: handle file ' + sFileName + ' FAILED! '
                           'Errors in opening file!', 2, 1)
                oFileDriver = None
                oFileHandle = None
                bFileOpen = False
                # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------

    else:

        # -------------------------------------------------------------------------------------
        # Exit for errors in finding file
        Exc.getExc(' =====> WARNING: handle file ' + sFileName + ' FAILED! File not found!', 2, 1)
        oFileDriver = None
        oFileHandle = None
        bFileOpen = False
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Return variable(s)
    return oFileHandle, oFileDriver, bFileOpen
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
