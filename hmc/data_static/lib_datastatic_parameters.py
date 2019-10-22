"""
Library Features:

Name:          Lib_HMC_DataParameters
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170715'
Version:       '2.0.0'
"""

#######################################################################################

# ===============================================================================
# Library
import logging
import numpy as np

from Lib_HMC_Struct_Args import sLoggerFormat
from Drv_HMC_Exception import Exc

# Log
oLogStream = logging.getLogger(sLoggerFormat)
# ================================================================================

# -------------------------------------------------------------------------------------
# Method to define default parameter map
def defineParamsMapDefault(a2dVarIN, dVarConst):
    a2dVarOUT = np.zeros([a2dVarIN.shape[0], a2dVarIN.shape[1]])
    a2dVarOUT[:, :] = np.float32(dVarConst)
    return a2dVarOUT
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute constant parameter maps
def computeParamsMapConstant(a2dVarPAR, a2bVarNaN=None, dVarND=-9999):
    if a2bVarNaN is not None:
        a2dVarPAR[a2bVarNaN] = dVarND
    return a2dVarPAR
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute distributed parameter maps
def computeParamsMapDistributed(a2dVarPAR, a2iVarWM, a2dVarLink, a2bVarNaN=None, dVarND=-9999):

    # Interating over values
    for iIndex in range(a2dVarLink.shape[0]):
        # Get parameter(s) and code(s)
        dVarPAR = np.float32(a2dVarLink[iIndex, 0])
        iVarWM = np.int32(a2dVarLink[iIndex, 1])
        # Create distributed parameter(s) map
        a2bVarIndex = np.where(a2iVarWM == np.int32(iVarWM))
        a2dVarPAR[a2bVarIndex[0], a2bVarIndex[1]] = np.float32(dVarPAR)

    if a2bVarNaN is not None:
        a2dVarPAR[a2bVarNaN] = dVarND

    return a2dVarPAR
# -------------------------------------------------------------------------------------
