"""
Library Features:

Name:          lib_time
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging

import numpy as np
import datetime
from copy import deepcopy

from hmc.default.lib_default_args import sLoggerName, sTimeFormat

from hmc.utils.lib_utils_apps_time import getTimeNow

from hmc.driver.manager.drv_manager_debug import Exc

# Logging
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# --------------------------------------------------------------------------------
# Method to update Data time workspace
def updateTimeData(oData, oDictUpd={}):

    for sDictKey, oDictValue in iter(oDictUpd.items()):

        if sDictKey in oData.keys():
            oData[sDictKey] = oDictValue
        else:
            pass
    return oData

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to compute arrival time (reference to a given hour)
def computeTimeArrival(sTime, iArrDay=1, a1oArrHour=['00', '12']):

    # Check list Data
    if a1oArrHour:

        oTime = datetime.datetime.strptime(sTime, sTimeFormat)

        oTimeRaw_TO = deepcopy(oTime)
        oTimeRaw_FROM = oTimeRaw_TO + datetime.timedelta(seconds=86400 * -iArrDay)

        oTimeRaw = oTimeRaw_FROM
        oTimeDelta = datetime.timedelta(seconds=86400)

        a1oTimeRaw = []
        while oTimeRaw <= oTimeRaw_TO:
            a1oTimeRaw.append(oTimeRaw.strftime(sTimeFormat))
            oTimeRaw += oTimeDelta

        a1oTimeArr_All = []
        for sTimeRaw in a1oTimeRaw:
            for sHourArr in a1oArrHour:
                oTimeRaw = datetime.datetime.strptime(sTimeRaw, sTimeFormat)
                oTimeArr = oTimeRaw.replace(hour=int(sHourArr), minute=0, second=0, microsecond=0)
                a1oTimeArr_All.append(oTimeArr.strftime(sTimeFormat))

        a1oTimeArr = []
        for sTimeArr in a1oTimeArr_All:
            oTimeArr = datetime.datetime.strptime(sTimeArr, sTimeFormat)

            if oTimeArr <= oTimeRaw_TO:
                a1oTimeArr.append(oTimeArr.strftime(sTimeFormat))
            else:
                pass

        a1oTimeArr = sorted(a1oTimeArr)

    else:
        a1oTimeArr = [sTime]

    return a1oTimeArr

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to put value in time summary
def putTimeSummary(sDataTime, oDataSummary, oDataUpd=False, sDataFlag='DataType'):

    a1oDataTime = oDataSummary['TimeStep']
    a1oDataFlag = oDataSummary[sDataFlag]

    iIndexTime = a1oDataTime.index(sDataTime)
    a1oDataFlag[iIndexTime] = oDataUpd

    oDataSummary[sDataFlag] = a1oDataFlag

    return oDataSummary
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to define summary time steps (OBS, FOR, CHECK and CORR)
def defineTimeSummary(sTimeRun,
                      a1oTimeSummary, a1oTimeStep,
                      a1oTimeCheck, a1oTimeCorr):

    # Simulation length
    iTimeStep = len(a1oTimeStep)

    # Summary time definition(s)
    a1oTimeSummaryType = iTimeStep * [None]             # Summary slots for data type (OBS/FOR)
    a1oTimeSummaryCheck = iTimeStep * [False]           # Summary slots for data checking
    a1oTimeSummaryCorr = iTimeStep * [False]            # Summary slots for data type extra (CORR)
    a1oTimeSummaryTag_FG = iTimeStep * [False]          # Summary slots for forcing data gridded
    a1oTimeSummaryTag_FP = iTimeStep * [False]          # Summary slots for forcing data point
    a1oTimeSummaryTag_FTS = iTimeStep * [False]         # Summary slots for forcing data timeseries
    a1oTimeSummaryTag_UG = iTimeStep * [False]          # Summary slots for updating data gridded
    a1oTimeSummaryTag_UP = iTimeStep * [False]          # Summary slots for updating data point
    a1oTimeSummaryTag_RG = iTimeStep * [False]          # Summary slots for restart data gridded
    a1oTimeSummaryTag_RP = iTimeStep * [False]          # Summary slots for restart data point

    # Time index definition
    iIndexStepRun = a1oTimeStep.index(sTimeRun)
    iIndexStepFrom = a1oTimeStep.index(a1oTimeStep[0])
    iIndexStepTo = a1oTimeStep.index(a1oTimeStep[-1])

    iIndexCheckFrom = a1oTimeStep.index(a1oTimeCheck[0])
    iIndexCheckTo = a1oTimeStep.index(a1oTimeCheck[-1])

    iIndexCorrFrom = a1oTimeStep.index(a1oTimeCorr[0])
    iIndexCorrTo = a1oTimeStep.index(a1oTimeCorr[-1])

    iIndexStepFrom_OBS = iIndexStepFrom
    iIndexStepTo_OBS = iIndexStepRun
    iIndexStepFrom_FOR = iIndexStepRun + 1
    iIndexStepTo_FOR = iIndexStepTo

    iIndexStepFrom_CHECK = iIndexCheckFrom
    iIndexStepTo_CHECK = iIndexCheckTo
    iIndexStepFrom_CORR = iIndexCorrFrom
    iIndexStepTo_CORR = iIndexCorrTo

    iIndexStep_TOT_OBS = iIndexStepTo_OBS - iIndexStepFrom_OBS + 1
    iIndexStep_TOT_FOR = iIndexStepTo_FOR - iIndexStepFrom_FOR + 1
    iIndexCheck_TOT = iIndexStepTo_CHECK - iIndexStepFrom_CHECK + 1
    iIndexCorr_TOT = iIndexStepTo_CORR - iIndexStepFrom_CORR + 1

    # Summary tags definition
    a1oTimeSummaryType[iIndexStepFrom_OBS : iIndexStepTo_OBS + 1] = ['OBS'] * iIndexStep_TOT_OBS
    a1oTimeSummaryType[iIndexStepFrom_FOR :iIndexStepTo_FOR + 1] = ['FOR'] * iIndexStep_TOT_FOR
    a1oTimeSummaryType[iIndexStepFrom_CORR:iIndexStepTo_CORR + 1] = ['CORR'] * iIndexCorr_TOT

    a1oTimeSummaryCheck[iIndexStepFrom_CHECK:iIndexStepTo_CHECK + 1] = [True] * iIndexCheck_TOT
    a1oTimeSummaryCorr[iIndexStepFrom_CORR:iIndexStepTo_CORR + 1] = [True] * iIndexCorr_TOT

    # Define time summary
    a1oTimeSummary['TimeStep'] = a1oTimeStep
    a1oTimeSummary['DataType'] = a1oTimeSummaryType
    a1oTimeSummary['DataCheck'] = a1oTimeSummaryCheck
    a1oTimeSummary['DataExtra'] = a1oTimeSummaryCorr
    a1oTimeSummary['DataForcingGridded'] = a1oTimeSummaryTag_FG
    a1oTimeSummary['DataForcingPoint'] = a1oTimeSummaryTag_FP
    a1oTimeSummary['DataForcingTimeSeries'] = a1oTimeSummaryTag_FTS
    a1oTimeSummary['DataUpdatingGridded'] = a1oTimeSummaryTag_UG
    a1oTimeSummary['DataUpdatingPoint'] = a1oTimeSummaryTag_UP
    a1oTimeSummary['DataRestartGridded'] = a1oTimeSummaryTag_RG
    a1oTimeSummary['DataRestartPoint'] = a1oTimeSummaryTag_RP

    # Return variable(s)
    return a1oTimeSummary

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to get running time
def getTimeRun(sTimeNow='', sTimeArg='', sTimeType='GMT'):

    if not sTimeNow == '':
        [sTimeNow, sTimeNowFormat] = getTimeNow(sTimeNow, sTimeType)
        oTimeNow = datetime.datetime.strptime(sTimeNow, sTimeNowFormat)
    else:
        oTimeNow = None
    if not sTimeArg == '':
        [sTimeArg, sTimeArgFormat] = getTimeNow(sTimeArg, sTimeType)
        oTimeArg = datetime.datetime.strptime(sTimeArg, sTimeArgFormat)
    else:
        oTimeArg = None

    if oTimeArg:
        sTimeRun = oTimeArg.strftime(sTimeArgFormat)
    else:
        sTimeRun = oTimeNow.strftime(sTimeNowFormat)

    return sTimeRun
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to get restart time
def computeTimeRestart(sTime, sTimeRestartHH='00', iTimeStep=3600, iTimePeriod=0):

    # Compute time restart
    # sTimeFormat = defineTimeFormat(sTime)
    oTime = datetime.datetime.strptime(sTime, sTimeFormat)

    oTimeRaw = oTime - datetime.timedelta(seconds=int(iTimePeriod * iTimeStep))
    oTimeStep = datetime.timedelta(seconds=iTimeStep)

    while oTimeRaw.hour != int(sTimeRestartHH):
        oTimeRaw -= oTimeStep

    sTimeRestart = oTimeRaw.strftime(sTimeFormat)

    return sTimeRestart

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to define corrivation time
def computeTimeCorrivation(a2dGeoZ, a2dGeoX, a2dGeoY, dGeoXCSize, dGeoYCSize, dGeoNoData=np.nan):

    # -------------------------------------------------------------------------------------
    # Dynamic values
    dR = 6378388  # (Radius)
    dE = 0.00672267  # (Ellipsoid)

    # dx = (R * cos(lat)) / (sqrt(1 - e2 * sqr(sin(lat)))) * PI / 180
    a2dDX = (dR * np.cos(a2dGeoY * np.pi / 180)) / (np.sqrt(1 - dE * np.sqrt(np.sin(a2dGeoY * np.pi / 180)))) * np.pi / 180
    # dy = (R * (1 - e2)) / pow((1 - e2 * sqr(sin(lat))),1.5) * PI / 180
    a2dDY = (dR * (1 - dE)) / np.power((1 - dE * np.sqrt(np.sin(a2dGeoY / 180))), 1.5) * np.pi / 180

    #a2dGeoAreaKm = ((a2dDX / (1 / dGeoXCSize)) * (a2dDY / (1 / dGeoYCSize))) / 1000000  # [km^2]
    a2dGeoAreaM = ((a2dDX / (1 / dGeoXCSize)) * (a2dDY / (1 / dGeoYCSize)))  # [m^2]

    # Area, Mean Dx and Dy values (meters)
    dGeoDxMean = np.sqrt(np.nanmean(a2dGeoAreaM))
    dGeoDyMean = np.sqrt(np.nanmean(a2dGeoAreaM))

    # Compute domain pixels and area
    iGeoPixels = np.sum(np.isfinite(a2dGeoZ))
    dGeoArea = float(iGeoPixels) * dGeoDxMean * dGeoDyMean / 1000000

    # Debug
    #plt.figure(1)
    #plt.imshow(a2dGeoZ); plt.colorbar()
    #plt.show()

    # Concentration time [hour]
    iGeoTc = np.int(0.27 * np.sqrt(0.6 * dGeoArea) + 0.25)

    return iGeoTc

    # -------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
