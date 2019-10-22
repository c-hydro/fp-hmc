"""
Class Features:

Name:          drv_data_io_type
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#################################################################################
# Library
import logging

from os.path import join
from os.path import split
from os.path import exists

from hmc.default.lib_default_args import sLoggerName
from hmc.utils.lib_utils_op_system import defineFileExt

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)
#################################################################################

#################################################################################
# Check file binary
def checkBinaryFile(filename):
    """Return true if the given filename is binary.
    @raise EnvironmentError: if the file does not exist or cannot be accessed.
    @attention: found @ http://bytes.com/topic/python/answers/21222-determine-file-type-binary-text on 6/08/2010
    @author: Trent Mick <TrentM@ActiveState.com>
    @author: Jorge Orpinel <jorge@orpinel.com>"""

    if exists(filename):
        fin = open(filename, 'rb')
        try:
            CHUNKSIZE = 1024
            while 1:
                chunk = fin.read(CHUNKSIZE)
                if b'\0' in chunk: # found null byte
                    return True
                if len(chunk) < CHUNKSIZE:
                    break # done
        finally:
            fin.close()

    return False
#################################################################################

#################################################################################
# Class to manage IO files
class Drv_Data_IO:
    
    # --------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFileName, sFileMode=None, sFileType=None):

        # Check binary file format
        bFileBinary = checkBinaryFile(sFileName)

        # Define file path, name and extension
        sFilePath = split(sFileName)[0]
        sFileName = split(sFileName)[1]
        sFileExt = defineFileExt(sFileName)

        # Define FileType and FileWorkspace
        if sFileName.endswith('txt') or sFileName.endswith('asc'):
            
            sFileType = 'ascii'
            self.oFileWorkspace = FileAscii(sFilePath, sFileName, sFileType, sFileMode)

        elif sFileName.endswith('nc'):
            
            sFileType = 'netCDF'
            self.oFileWorkspace = FileNetCDF(sFilePath, sFileName, sFileType, sFileMode)

        elif sFileName.endswith('bin') or (sFileExt is '' and bFileBinary is True):
            
            sFileType = 'binary'
            self.oFileWorkspace = FileBinary(sFilePath, sFileName, sFileType, sFileMode)

        else:
            sFileType = 'unknown'
            self.oFileWorkspace = FileUnknown(sFilePath, sFileName, sFileType, sFileMode)

    # --------------------------------------------------------------------------------
    
#################################################################################

#################################################################################

# --------------------------------------------------------------------------------
# Class to manage unknown files
class FileUnknown:

    # --------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode

        # Print file unknown information
        self.printInfo()

    # --------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------
    # Method to print information about unknown file
    def printInfo(self):
        Exc.getExc(' =====> WARNING: file ' + join(self.sFilePath, self.sFileName) +
                   ' has unknown extension! Please check library or file format!', 2, 1)
        Exc.getExc(' =====> ERROR: file format unknown!', 1, 1)
    # --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Class to manage Binary files
class FileBinary:

    # --------------------------------------------------------------------------------
    # Class variable(s)
    oFileLibrary = None
    # --------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode

        # Set library IO
        self.setFileLibIO()
    
    # --------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------
    # Method to set library I/O function(s)
    def setFileLibIO(self):

        import hmc.io.lib_data_io_binary as oFileLibrary
        self.oFileLibrary = oFileLibrary

    # --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Class to manage ASCII files
class FileAscii:

    # --------------------------------------------------------------------------------
    # Class variable(s)
    oFileLibrary = None
    # --------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode

        # Set library IO
        self.setFileLibIO()

    # --------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------
    # Method to set library I/O function(s)
    def setFileLibIO(self):

        import hmc.io.lib_data_io_ascii as oFileLibrary
        self.oFileLibrary = oFileLibrary
        
    # --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Class to manage NetCDF grid files
class FileNetCDF:

    # --------------------------------------------------------------------------------
    # Class variables
    oFileLibrary = None
    # --------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        # Common variable(s)
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode

        # Set library IO
        self.setFileLibIO()

    # --------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------
    # Method to set library I/O function(s)
    def setFileLibIO(self):
        
        import hmc.io.lib_data_io_netcdf as oFileLibrary
        self.oFileLibrary = oFileLibrary
        
    # --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------

#################################################################################
