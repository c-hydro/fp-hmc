# Copyright (c) 2018, CIMA Research Foundation, Hydrology and Hydraulics Department
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of TU Wien, Department of Geodesy and Geoinformation
#      nor the names of its contributors may be used to endorse or promote
#      products derived from this software without specific prior written
#      permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL TU WIEN DEPARTMENT OF GEODESY AND
# GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Description:    Library to manage CSV data

Name:           lib_data_io_ascii
Author(s):      Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:           '20180516'
Version:        '2.0.1'
"""

import numpy as np

from hmc.io.lib_data_io_csv import openFile, parseFile
from hmc.utils.lib_generic_op_dataframe import castDF, convertDict2DF

class io_reader_csv:

    """
    Class that provides access to weather stations data stored in CSV format.

    Parameters
    ----------
    sFileName : string
        File name of weather stations data
    sFileDelimiter : string
        Delimiter used to separate columns of the file
    oFileFieldsName : list, optional
        Names of the columns
    oFileFieldsType : list, optional
        Type of the columns [numeric, datetime, string, object]

    Attributes
    ----------
    sFileName : string
        File name of weather stations data
    sFileDelimiter : string
        Delimiter used to separate columns of the file
    oFileFieldsName : list, optional
        Names of the columns
    oFileFieldsType : list, optional
        Type of the columns [numeric, datetime, string, object]

    Methods
    -------
    readData()
        Read data
    filterData(oDF, sFieldName, dFieldMin, dFieldMax)
        Filter data using physical min and max limits
    """

    def __init__(self, sFileName, sFileDelimiter=',', oFileFieldsName=None, oFileFieldsType=None):

        self.sFileName = sFileName
        self.sFileDelimiter = sFileDelimiter
        self.oFileFieldsName = oFileFieldsName
        self.oFileFieldsType = oFileFieldsType

    def readData(self):

        """
        Read data from a CSV file

        Returns
        -------
        oFileDF : dataframe
        """

        oFileData = openFile(self.sFileName, 'r')
        oFileTable = parseFile(oFileData, self.sFileDelimiter)[0]

        oFileDict = {}
        for sFileField, oFileField in zip(self.oFileFieldsName, oFileTable):
            oFileDict[sFileField] = oFileField
        oFileDF = convertDict2DF(oFileDict)

        for sFileFieldsName, sFileFieldsType in zip(self.oFileFieldsName, self.oFileFieldsType):
            oFileDF = castDF(oFileDF, sFileFieldsName, sFileFieldsType)

        return oFileDF

    @staticmethod
    def filterData(oDF, sFieldName, dFieldMin=np.nan, dFieldMax=np.nan):

        """
        Filter data using physical min and max limits

        Parameters
        ----------
        oDF : dataframe
            Data
        sFieldName : string
            Name of the filtering data field
        dFieldMin: float
            Minimal accepted value of data
        dFieldMax : float
            Maximum accepted value of data
        Returns
        -------
        oDF : dataframe
        """

        oDF.loc[(oDF[sFieldName] < dFieldMin), sFieldName] = np.nan
        oDF.loc[(oDF[sFieldName] > dFieldMax), sFieldName] = np.nan
        return oDF
