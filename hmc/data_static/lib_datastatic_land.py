"""
Library Features:

Name:          lib_datastatic_land
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging

import numpy as np
from copy import deepcopy

from hmc.default.lib_default_args import sLoggerName
import hmc.data_static.Lib_HMC_DataLand_FlowDirections as oFDir
import hmc.data_static.Lib_HMC_DataLand_DrainageArea as oDArea
import hmc.data_static.Lib_HMC_DataLand_ChannelsNetwork as oCNet
import hmc.data_static.Lib_HMC_DataLand_WatertableSlopes as oWSlope
import hmc.data_static.Lib_HMC_DataLand_CoeffResolution as oCRes
import hmc.data_static.Lib_HMC_DataLand_CorrivationTime as oCTime

from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to compute mask domain
def computeMaskDomain(a2dVarDEM, dNoData):

    # Initialize mask array
    a2iVarMask = np.zeros([a2dVarDEM.shape[0], a2dVarDEM.shape[1]])
    a2iVarMask[:, :] = 1

    # Define undefined indexex
    a2bVarIdxUndef = np.where(a2dVarDEM == dNoData)
    a2iVarMask[a2bVarIdxUndef[0], a2bVarIdxUndef[1]] = 0

    return a2iVarMask

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute flow directions (using fortran external source)
def computeFlowDirections(a2dVarDEM):

    # Compiling fortran module using f2py library
    # f2py -c module_flow_directions.f90 -m Lib_HMC_DataLand_FlowDirections

    # Print information about Fortran module
    # print(oFDir.flow_directions.fdir.__doc__)
    # Call Fortran module
    a2iVarPNT = oFDir.flow_directions.fdir(a2dVarDEM)
    a2iVarPNT[a2iVarPNT == 0] = -9999
    a2iVarPNT = np.int32(a2iVarPNT)

    return a2iVarPNT

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute drainage area (using fortran external source)
def computeDrainageArea(a2dVarDEM, a2iVarPNT):

    # Compiling fortran module using f2py library
    # f2py -c module_drainage_area.f90 -m Lib_HMC_DataLand_DrainageArea

    # Print information about Fortran module
    # print(oDArea.drainage_area.darea.__doc__)
    # Call Fortran module
    a2iVarDArea = oDArea.drainage_area.darea(a2dVarDEM, a2iVarPNT)
    a2iVarDArea = np.int32(a2iVarDArea)

    return a2iVarDArea

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute channels network (using fortran external source)
def computeChannelsNetwork(a2dVarDEM, a2iVarPNT, a2iVarDArea, dVarAvgCAREA, dParCNET):

    # Compiling fortran module using f2py library
    # f2py -c module_channels_network.f90 -m Lib_HMC_DataLand_ChannelsNetwork

    # Parameter(s) cast to int for adapting with fortran source
    iParCNET = np.int32(dParCNET)
    iVarAvgCAREA = np.int32(dVarAvgCAREA)

    # Print information about Fortran module
    # print(oCNet.channels_network.cnet.__doc__)
    # Call Fortran module
    [a2iVarCNET, a2dVarPDIST] = oCNet.channels_network.cnet(a2dVarDEM, a2iVarPNT, a2iVarDArea, iParCNET, iVarAvgCAREA)

    return a2iVarCNET, a2dVarPDIST

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute watertable slopes (using fortran external source)
def computeWatertableSlopes(a2dVarDEM, a2iVarPNT, a2iVarCNET, a2dVarCAREA, dParWT):

    # Compiling fortran module using f2py library
    # f2py -c module_watertable_slopes.f90 -m Lib_HMC_DataLand_WatertableSlopes

    # Variable(s) cast to float64 for adapting with fortran source
    a2dVarDEM = np.float64(a2dVarDEM)
    a2dVarCAREA = np.float64(a2dVarCAREA)

    # Print information about Fortran module
    # print(oWSlope.watertable_slopes.wslope.__doc__)
    # Call Fortran module
    [a2dVarALPHA, a2dVarBETA] = oWSlope.watertable_slopes.wslope(a2dVarDEM, a2iVarPNT, a2iVarCNET, a2dVarCAREA, dParWT)

    return a2dVarALPHA, a2dVarBETA

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute corrivation time (using fortran external source)
def computeCorrivationTime(a2dVarDEM, a2iVarPNT, a2dVarPDIST, a2iVarCNET, a2dVarUH, a2dVarUC,
                           iSecJout, iSecIout, iSEC_HydID=1):

    # Compiling fortran module using f2py library
    # f2py -c module_corrivation_time.f90 -m Lib_HMC_DataLand_CorrivationTime

    # Parameter(s) cast to int for adapting with fortran source
    iSecJout = np.int32(iSecJout)
    iSecIout = np.int32(iSecIout)

    # Print information about Fortran module
    # print(oCTime.corrivation_time.ctime.__doc__)
    # Call Fortran module
    [a2dVarCTIME, a2iVarMASK, a2dVarDEMMASKED] = oCTime.corrivation_time.ctime(a2dVarDEM, a2iVarPNT,
                                                                               a2dVarPDIST, a2iVarCNET,
                                                                               a2dVarUH, a2dVarUC,
                                                                               iSecJout, iSecIout)
    # Set domain code (if defined in input)
    if iSEC_HydID >= 1:
        a2iVarMASK[a2iVarMASK == 1] = np.int32(iSEC_HydID)

    return a2dVarCTIME, a2iVarMASK, a2dVarDEMMASKED

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute coefficient resolution (using fortran external source)
def computeCoeffResolution(a2dVarDEM, a2iVarDAREA, a2iVarCNET, a2dVarCAREA, dParCR):

    # Compiling fortran module using f2py library
    # f2py -c module_coeff_resolution.f90 -m Lib_HMC_DataLand_CoeffResolution

    # Print information about Fortran module
    # print(oCRes.coeff_resolution.cres.__doc__)
    # Call Fortran module
    a2dVarCR = oCRes.coeff_resolution.cres(a2dVarDEM, a2iVarDAREA, a2iVarCNET, a2dVarCAREA, dParCR)

    return a2dVarCR

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute cell area taking care pixels latitude
def computeCellArea(a2dGeoY, dGeoXCellSize, dGeoYCellSize):

    # Method constant(s)
    dR = 6378388  # (Radius)
    dE = 0.00672267  # (Ellipsoid)

    # dx = (R * cos(lat)) / (sqrt(1 - e2 * sqr(sin(lat)))) * PI / 180
    a2dDX = (dR * np.cos(a2dGeoY * np.pi / 180)) \
            / (np.sqrt(1 - dE * np.sqrt(np.sin(a2dGeoY * np.pi / 180)))) * np.pi / 180
    # dy = (R * (1 - e2)) / pow((1 - e2 * sqr(sin(lat))),1.5) * PI / 180
    a2dDY = (dR * (1 - dE)) / np.power((1 - dE * np.sqrt(np.sin(a2dGeoY / 180))), 1.5) * np.pi / 180

    # Compute cell area in m^2
    a2dVarCAREA = ((a2dDX / (1 / dGeoXCellSize)) * (a2dDY / (1 / dGeoYCellSize)))  # [m^2]

    return a2dVarCAREA

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to set no data value on array boundaries
def setNoDataBound(a2dData, dNoData=-9999):

    # Set boundaries with no-data value
    a2dData[0, :] = dNoData     # First row
    a2dData[:, 0] = dNoData     # First column
    a2dData[-1, :] = dNoData    # Last row
    a2dData[:, -1] = dNoData    # Last column

    return a2dData
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute watermark nested
def computeWatermarkNested(a2iVarWTN_IN, a2iVarMASK, iVarWTN=0, iVarMASK=1):

    # Get MASK finite indexes
    a2bVarMASK_FINITE_ALL = np.where(a2iVarMASK > iVarMASK)
    a2bVarMASK_FINITE_PART = np.where((a2iVarMASK > iVarMASK) & (a2iVarWTN_IN == iVarWTN))
    # Get WATERMARK indexes in MASK finite indexes
    a1iVarWTN_SELECT = a2iVarWTN_IN[a2bVarMASK_FINITE_ALL[0], a2bVarMASK_FINITE_ALL[1]]
    # Define output array
    a2iVarWTN_OUT = deepcopy(a2iVarWTN_IN)

    # Check MASK FINITE
    if len(a2bVarMASK_FINITE_ALL[0]) == 0 and len(a2bVarMASK_FINITE_ALL[1]) == 0:
        bVarMASK_FINITE_ALL = False
    else:
        bVarMASK_FINITE_ALL = True

    # MASK FINITE condition
    if bVarMASK_FINITE_ALL:

        # Case 1: none domain is stored in watermark nested array
        if np.all(a1iVarWTN_SELECT == iVarWTN):
            a2iVarWTN_OUT[
                a2bVarMASK_FINITE_ALL[0], a2bVarMASK_FINITE_ALL[1]] = \
                a2iVarMASK[a2bVarMASK_FINITE_ALL[0], a2bVarMASK_FINITE_ALL[1]]
        # Case 2: other domain is stored completely in watermark nested array
        elif np.all(a1iVarWTN_SELECT != iVarWTN):
            a2iVarWTN_OUT[
                a2bVarMASK_FINITE_ALL[0], a2bVarMASK_FINITE_ALL[1]] = \
                a2iVarMASK[a2bVarMASK_FINITE_ALL[0], a2bVarMASK_FINITE_ALL[1]]
        # Case 3: other domain is stored partially in watermark nested array
        elif np.any(a1iVarWTN_SELECT == iVarWTN):
            a2iVarWTN_OUT[a2bVarMASK_FINITE_PART[0], a2bVarMASK_FINITE_PART[1]] = \
                a2iVarMASK[a2bVarMASK_FINITE_PART[0],a2bVarMASK_FINITE_PART[1]]
        else:
            pass
    else:
        pass

    #plt.figure(1)
    #plt.imshow(a2iVarWTN_OUT); plt.colorbar()
    #plt.show()

    return a2iVarWTN_OUT

# -------------------------------------------------------------------------------------
