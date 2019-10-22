"""
Library Features:

Name:          lib_default_namelist
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

# -------------------------------------------------------------------------------------
# Generic namelist file
sFileNamelist = '/run/hmc.namelist.txt'
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Generic namelist dictionary
oDataNamelist = dict(

    HMC_Parameters={
        'dUc': 20,  # new in 2.0.7
        'dUh': 1.5,  # new in 2.0.7
        'dCt': 0.5,  # new in 2.0.7
        'dCf': 0.02,  # new in 2.0.7
        'dCPI': 0.3,  # new in 2.0.7
        'dWTableHbr': 500,  # new in 2.0.7
        'dKSatRatio': 1,  # new in 2.0.7
        'dSlopeMax': 70,  # new in 2.0.7
        'sDomainName': "default",  # new in 2.0.7
    },

    HMC_Namelist={

        'iFlagDebugSet': 1,
        'iFlagDebugLevel': 3,

        'iFlagTypeData_Static': 1,
        'iFlagTypeData_Forcing_Gridded': 2,
        'iFlagTypeData_Forcing_Point': 1,
        'iFlagTypeData_Forcing_TimeSeries': 1,  # new in 2.0.7
        'iFlagTypeData_Updating_Gridded': 2,    # new in 2.0.7
        'iFlagTypeData_Output_Gridded': 2,
        'iFlagTypeData_Output_Point': 1,
        'iFlagTypeData_Output_TimeSeries': 1,   # new in 2.0.7
        'iFlagTypeData_State_Gridded': 2,
        'iFlagTypeData_State_Point': 1,
        'iFlagTypeData_Restart_Gridded': 2,
        'iFlagTypeData_Restart_Point': 1,

        'iFlagOs': 10,
        'iFlagFlowDeep': 1,
        'iFlagRestart': 0,
        # 'a1iFlagS': [0, 0, 0],            # obsolete field
        # 'a1iFlagO': [0, 0, 0],            # obsolete field
        # 'iFlagVarUc': 1,                  # obsolete field
        'iFlagVarDtPhysConv': 1,
        'iFlagSnow': 0,
        'iFlagSnowAssim': 0,
        'iFlagSMAssim': 0,                  # new in 2.0.7
        'iFlagLAI': 0,
        'iFlagAlbedo': 0,
        'iFlagCoeffRes': 0,                 # new in 2.0.7
        'iFlagWS': 0,                       # new in 2.0.7
        'iFlagReleaseMass': 1,              # new in 2.0.7

        'a1dGeoForcing': [-9999.0, -9999.0],
        'a1dResForcing': [-9999.0, -9999.0],
        'a1iDimsForcing': [-9999, -9999],

        'iSimLength': 0,
        'iDtModel': 3600,

        'iDtPhysMethod': 1,                 # new in 2.0.7
        'iDtPhysConv': 50,
        'a1dDemStep': [1, 10, 100, 1000],   # new in 2.0.7
        'a1dIntStep': [1, 5, 25, 600],      # new in 2.0.7
        'a1dDtStep': [1, 6, 6, 60],         # new in 2.0.7
        'a1dDtRatioStep': [3, 3, 3, 2],     # new in 2.0.7

        'iDtData_Forcing': 3600,
        'iDtData_Updating': 3600,           # new in 2.0.7
        'iDtData_Output_Gridded': 3600,
        'iDtData_Output_Point': 3600,
        'iDtData_State_Gridded': 3600,
        'iDtData_State_Point': 3600,

        'iScaleFactor': 10,
        'iTcMax': -9999,

        'sTimeStart': "197822051255",
        # 'sTimeStatus': "197822051255",    # obsolete field
        'sTimeRestart': "197822051255",

        'sPathData_Static_Gridded': "/static/gridded/",
        'sPathData_Static_Point': "/static/gridded/",
        'sPathData_Forcing_Gridded': "/forcing/gridded/",
        'sPathData_Forcing_Point': "/forcing/gridded/",
        'sPathData_Forcing_TimeSeries': "/forcing/timeseries/",         # new in 2.0.7
        'sPathData_Updating_Gridded': "/updating/gridded/",             # new in 2.0.7
        'sPathData_Output_Gridded': "/output/gridded/",
        'sPathData_Output_Point': "/output/gridded/",
        'sPathData_Output_TimeSeries': "/output/timeseries/",           # new in 2.0.7
        'sPathData_State_Gridded': "/state/gridded/",
        'sPathData_State_Point': "/state/gridded/",
        'sPathData_Restart_Gridded': "/restart/gridded/",
        'sPathData_Restart_Point': "/restart/gridded/",

    },

    HMC_Snow={
        'a1dArctUp': [3.0, 4.5, 3.0, 4.0],
        'a1dExpRhoLow': [0.0333, 0.0222, 0.0250, 0.0333],
        'a1dExpRhoHigh': [0.0714, 0.0714, 0.0714, 0.0714],
        'a1dAltRange': [1500.0, 2000.0, 2500.0, 2500.0],
        'iGlacierValue': 2,
        'dRhoSnowFresh': 100,                               # new in 2.0.7
        'dRhoSnowMax': 400,
        'dSnowQualityThr': 0.3,
        'dSnowTRef': 2,                                     # new in 2.0.7
        'dMeltingTRef': 1,                                  # new in 2.0.7
    },

    HMC_Constants={
        'a1dAlbedoMonthly': [0.18,  0.17, 0.16,  0.15,  0.15,  0.15,  0.15,  0.16,  0.16,  0.17,  0.17,  0.18],
        'a1dLAIMonthly': [4.00,  4.00, 4.00,  4.00,  4.00,  4.00,  4.00,  4.00,  4.00,  4.00,  4.00,  4.00],

        'dWTableHMin': 10.0,
        'dWTableHUSoil': 100.0,
        'dWTableHUChannel': 5.0,
        'dWTableSlopeBM': 0.08,
        'dWTableHOBedRock': 25.0,

        'dRateMin': 0.01,
        'dBc': 0.5,

        'dTRef': 273.15,
        'iTdeepShift': 2,
        'a1dCHMonthly': [-7.3, -7.3, -5.8, -5.8, -5.8, -4.8, -4.8, -4.8, -4.8, -5.9, -5.9, -7.3],
        'dEpsS': 0.96,
        'dSigma': 0.00000005576,
        'dBFMin': 0.1,
        'dBFMax': 0.9,

        'dZRef': 3.0,
        'dG': 9.81,
        'dCp': 1004.0,
        'dRd': 287.0,

        'dRhoS': 2700,
        'dRhoW': 1000,
        'dCpS': 733,
        'dCpW': 4186,
        'dKq': 7.7,
        'dKw': 0.57,
        'dKo': 4,
        'dPorS': 0.4,
        'dFqS': 0.5,

        'dTV': 0.95,
        'dDamSpillH': 0.4,

        'dSMGain': 0.45,                                         # new in 2.0.7
    },

    HMC_Command={
        'sCommandZipFile': "gzip -f filenameunzip > LogZip.txt",
        'sCommandUnzipFile': "gunzip -c filenamezip > filenameunzip",
        'sCommandRemoveFile': "rm filename",
        'sCommandCreateFolder': "mkdir -p path",
    },

    HMC_Info={
        'sReleaseVersion': "2.0.7",
        'sAuthorNames': "Delogu F., Silvestro F., Gabellani S.",
        'sReleaseDate': "2018/01/19",
    },
)
# -------------------------------------------------------------------------------------
