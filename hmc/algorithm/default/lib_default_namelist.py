"""
Library Features:

Name:          lib_default_namelist
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

# -------------------------------------------------------------------------------------
# Namelist default
link_namelist_default = dict(

    HMC_Parameters={
        'dUc': {'algorithm': ['HMC_Info', 'hmc_parameters', 'ct']},
        'dUh': {'algorithm': ['HMC_Info', 'hmc_parameters', 'uh']},
        'dCt': {'algorithm': ['HMC_Info', 'hmc_parameters', 'ct']},
        'dCf': {'algorithm': ['HMC_Info', 'hmc_parameters', 'cf']},
        'dCPI': {'algorithm': ['HMC_Info', 'hmc_parameters', 'cpi']},
        'dCN': {'algorithm': ['HMC_Info', 'hmc_parameters', 'cn']},
        'dWS': {'algorithm': ['HMC_Info', 'hmc_parameters', 'ws']},
        'dFrac': {'algorithm': ['HMC_Info', 'hmc_parameters', 'fracturation']},
        'dWTableHbr': {'algorithm': ['HMC_Info', 'hmc_parameters', 'wtable_hbr']},
        'dKSatRatio': {'algorithm': ['HMC_Info', 'hmc_parameters', 'ksat_ratio']},
        'dSlopeMax': {'algorithm': ['HMC_Info', 'hmc_parameters', 'slope_max']},
        'sDomainName': {'algorithm': ['Run_Info', 'run_type', 'run_domain']},
    },

    HMC_Namelist={

        'iFlagDebugSet': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_debug_set']},
        'iFlagDebugLevel': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_debug_level']},

        'iFlagTypeData_Static': 1,
        'iFlagTypeData_Forcing_Gridded': 2,
        'iFlagTypeData_Forcing_Point': 1,
        'iFlagTypeData_Forcing_TimeSeries': 1,
        'iFlagTypeData_Updating_Gridded': 2,
        'iFlagTypeData_Output_Gridded': 2,
        'iFlagTypeData_Output_Point': 1,
        'iFlagTypeData_Output_TimeSeries': 1,
        'iFlagTypeData_State_Gridded': 2,
        'iFlagTypeData_State_Point': 1,
        'iFlagTypeData_Restart_Gridded': 2,
        'iFlagTypeData_Restart_Point': 1,

        'iFlagOs': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_model_os']},
        'iFlagFlowDeep': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_flow_deep']},
        'iFlagRestart': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_model_restart']},
        'iFlagVarDtPhysConv': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_convolution_dt']},
        'iFlagSnow': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_snow']},
        'iFlagSnowAssim': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_assimilation_snow']},
        'iFlagSMAssim': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_assimilation_soil_moisture']},
        'iFlagLAI': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_datasets_lai']},
        'iFlagAlbedo': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_datasets_albedo']},
        'iFlagCoeffRes': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_coeff_resolution']},
        'iFlagWS': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_water_sources']},
        'iFlagReleaseMass': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_release_mass']},
        'iFlagCType': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_convolution_type']},
        'iFlagFrac': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_fracturation']},
        'iFlagDynVeg': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_dynamic_vegetation']},
        'iFlagFlood': {'algorithm': ['HMC_Info', 'hmc_flags', 'flag_phys_flooding']},

        'a1dGeoForcing': [-9999.0, -9999.0],
        'a1dResForcing': [-9999.0, -9999.0],
        'a1iDimsForcing': [-9999, -9999],

        'iSimLength': {'time': ['time_run_length']},
        'iDtModel': {'algorithm': ['HMC_Info', 'hmc_dt', 'dt_model']},

        'iDtPhysMethod': 1,
        'iDtPhysConv': 50,
        'a1dDemStep': [1, 10, 100, 1000],
        'a1dIntStep': [1, 5, 25, 600],
        'a1dDtStep': [1, 6, 6, 60],
        'a1dDtRatioStep': [3, 3, 3, 2],

        'iDtData_Forcing': {'time': ['time_observed_delta']},
        'iDtData_Updating': {'time': ['time_observed_delta']},
        'iDtData_Output_Gridded': {'time': ['time_observed_delta']},
        'iDtData_Output_Point': {'time': ['time_observed_delta']},
        'iDtData_State_Gridded': {'time': ['time_observed_delta']},
        'iDtData_State_Point': {'time': ['time_observed_delta']},

        'iScaleFactor': 1,
        'iTcMax': {'time': ['time_tc']},
        'iTVeg': {'algorithm': ['Time_Info', 'time_vegetation_max']},

        'sTimeStart':  {'time': ['time_str_start']},
        'sTimeRestart':  {'time': ['time_str_restart']},

        'sPathData_Static_Gridded': {'datasets': ['DataGeo', 'Gridded', 'hmc_file_folder']},
        'sPathData_Static_Point': {'datasets': ['DataGeo', 'Point', 'hmc_file_folder']},
        'sPathData_Forcing_Gridded': {'datasets': ['DataForcing', 'Gridded', 'hmc_file_folder']},
        'sPathData_Forcing_Point': {'datasets': ['DataForcing', 'Point', 'hmc_file_folder']},
        'sPathData_Forcing_TimeSeries': {'datasets': ['DataForcing', 'TimeSeries', 'hmc_file_folder']},
        'sPathData_Updating_Gridded': {'datasets': ['DataUpdating', 'Gridded', 'hmc_file_folder']},
        'sPathData_Output_Gridded': {'datasets': ['DataOutcome', 'Gridded', 'hmc_file_folder']},
        'sPathData_Output_Point': {'datasets': ['DataOutcome', 'Point', 'hmc_file_folder']},
        'sPathData_Output_TimeSeries': {'datasets': ['DataOutcome', 'TimeSeries', 'hmc_file_folder']},
        'sPathData_State_Gridded':  {'datasets': ['DataState', 'Gridded', 'hmc_file_folder']},
        'sPathData_State_Point': {'datasets': ['DataState', 'Point', 'hmc_file_folder']},
        'sPathData_Restart_Gridded': {'datasets': ['DataRestart', 'Gridded', 'hmc_file_folder']},
        'sPathData_Restart_Point': {'datasets': ['DataRestart', 'Point', 'hmc_file_folder']},

        'iActiveData_Output_Generic': {'algorithm': ['HMC_Info', 'hmc_datasets', 'dset_output_generic']},
        'iActiveData_Output_Flooding': {'algorithm': ['HMC_Info', 'hmc_datasets', 'dset_output_flooding']},
        'iActiveData_Output_Snow': {'algorithm': ['HMC_Info', 'hmc_datasets', 'dset_output_snow']},
        'iAccumData_Output_Hour': {'algorithm': ['HMC_Info', 'hmc_datasets', 'dset_output_accumulated_hour_step']},

    },

    HMC_Snow={
        'a1dArctUp': [3.0, 4.5, 3.0, 4.0],
        'a1dExpRhoLow': [0.0333, 0.0222, 0.0250, 0.0333],
        'a1dExpRhoHigh': [0.0714, 0.0714, 0.0714, 0.0714],
        'a1dAltRange': [1500.0, 2000.0, 2500.0, 2500.0],
        'iGlacierValue': 2,
        'dRhoSnowFresh': 100,
        'dRhoSnowMax': 400,
        'dSnowQualityThr': 0.3,
        'dSnowTRef': 2,
        'dMeltingTRef': 1,
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
        'dLSTDeltaMax': {'algorithm': ['HMC_Info', 'hmc_phys_parametrization', 'phys_lst_maximum_integration_delta']},

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

        'dTV': {'algorithm': ['HMC_Info', 'hmc_phys_parametrization', 'phys_dam_initial_percentage_outflow']},
        'dDamSpillH': {'algorithm': ['HMC_Info', 'hmc_phys_parametrization', 'phys_dam_initial_delta_spill']},

        'dSMGain': 0.45,
    },

    HMC_Command={
        'sCommandZipFile': "gzip -f filenameunzip > LogZip.txt",
        'sCommandUnzipFile': "gunzip -c filenamezip > filenameunzip",
        'sCommandRemoveFile': "rm filename",
        'sCommandCreateFolder': "mkdir -p path",
    },

    HMC_Info={
        'sReleaseVersion': "3.1.3",
        'sAuthorNames': "Delogu F., Silvestro F., Gabellani S., Basso V., Libertino A., Ercolani G.",
        'sReleaseDate': "2020/10/28",
    },
)
# Namelist default
structure_namelist_default = dict(

    HMC_Parameters={
        'dUc': 20,
        'dUh': 1.5,
        'dCt': 0.5,
        'dCf': 0.02,
        'dCPI': 0.3,
        'dWTableHbr': 500,
        'dKSatRatio': 1,
        'dSlopeMax': 70,
        'sDomainName': "default",
    },

    HMC_Namelist={

        'iFlagDebugSet': 1,
        'iFlagDebugLevel': 3,

        'iFlagTypeData_Static': 1,
        'iFlagTypeData_Forcing_Gridded': 2,
        'iFlagTypeData_Forcing_Point': 1,
        'iFlagTypeData_Forcing_TimeSeries': 1,
        'iFlagTypeData_Updating_Gridded': 2,
        'iFlagTypeData_Output_Gridded': 2,
        'iFlagTypeData_Output_Point': 1,
        'iFlagTypeData_Output_TimeSeries': 1,
        'iFlagTypeData_State_Gridded': 2,
        'iFlagTypeData_State_Point': 1,
        'iFlagTypeData_Restart_Gridded': 2,
        'iFlagTypeData_Restart_Point': 1,

        'iFlagOs': 10,
        'iFlagFlowDeep': 1,
        'iFlagRestart': 0,
        'iFlagVarDtPhysConv': 1,
        'iFlagSnow': 0,
        'iFlagSnowAssim': 0,
        'iFlagSMAssim': 0,
        'iFlagLAI': 0,
        'iFlagAlbedo': 0,
        'iFlagCoeffRes': 0,
        'iFlagWS': 0,
        'iFlagReleaseMass': 1,
        'iFlagCType': 1,
        'iFlagFrac': 0,
        'iFlagDynVeg': 0,
        'iFlagFlood': 0,

        'a1dGeoForcing': [-9999.0, -9999.0],
        'a1dResForcing': [-9999.0, -9999.0],
        'a1iDimsForcing': [-9999, -9999],

        'iSimLength': 0,
        'iDtModel': 3600,

        'iDtPhysMethod': 1,
        'iDtPhysConv': 50,
        'a1dDemStep': [1, 10, 100, 1000],
        'a1dIntStep': [1, 5, 25, 600],
        'a1dDtStep': [1, 6, 6, 60],
        'a1dDtRatioStep': [3, 3, 3, 2],

        'iDtData_Forcing': 3600,
        'iDtData_Updating': 3600,
        'iDtData_Output_Gridded': 3600,
        'iDtData_Output_Point': 3600,
        'iDtData_State_Gridded': 3600,
        'iDtData_State_Point': 3600,

        'iScaleFactor': 10,
        'iTcMax': -9999,
        'iTVeg': 720,

        'sTimeStart': "197822051255",
        'sTimeRestart': "197822051255",

        'sPathData_Static_Gridded': "/static/gridded/",
        'sPathData_Static_Point': "/static/gridded/",
        'sPathData_Forcing_Gridded': "/forcing/gridded/",
        'sPathData_Forcing_Point': "/forcing/gridded/",
        'sPathData_Forcing_TimeSeries': "/forcing/timeseries/",
        'sPathData_Updating_Gridded': "/updating/gridded/",
        'sPathData_Output_Gridded': "/output/gridded/",
        'sPathData_Output_Point': "/output/gridded/",
        'sPathData_Output_TimeSeries': "/output/timeseries/",
        'sPathData_State_Gridded': "/state/gridded/",
        'sPathData_State_Point': "/state/gridded/",
        'sPathData_Restart_Gridded': "/restart/gridded/",
        'sPathData_Restart_Point': "/restart/gridded/",

        'iActiveData_Output_Generic': 2,
        'iActiveData_Output_Flooding': 0,
        'iActiveData_Output_Snow': 0,
        'iAccumData_Output_Hour': 23,

    },

    HMC_Snow={
        'a1dArctUp': [3.0, 4.5, 3.0, 4.0],
        'a1dExpRhoLow': [0.0333, 0.0222, 0.0250, 0.0333],
        'a1dExpRhoHigh': [0.0714, 0.0714, 0.0714, 0.0714],
        'a1dAltRange': [1500.0, 2000.0, 2500.0, 2500.0],
        'iGlacierValue': 2,
        'dRhoSnowFresh': 100,
        'dRhoSnowMax': 400,
        'dSnowQualityThr': 0.3,
        'dSnowTRef': 2,
        'dMeltingTRef': 1,
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
        'dLSTDeltaMax': 40,

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

        'dSMGain': 0.45,
    },

    HMC_Command={
        'sCommandZipFile': "gzip -f filenameunzip > LogZip.txt",
        'sCommandUnzipFile': "gunzip -c filenamezip > filenameunzip",
        'sCommandRemoveFile': "rm filename",
        'sCommandCreateFolder': "mkdir -p path",
    },

    HMC_Info={
        'sReleaseVersion': "3.1.3",
        'sAuthorNames': "Delogu F., Silvestro F., Gabellani S., Basso V., Libertino A., Ercolani G.",
        'sReleaseDate': "2020/10/28",
    },
)
# -------------------------------------------------------------------------------------
