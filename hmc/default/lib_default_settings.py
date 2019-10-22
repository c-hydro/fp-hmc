"""
Library Features:

Name:          lib_default_settings
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
# Nothing to do here
#######################################################################################

# -------------------------------------------------------------------------------------
# Settings general info
oGeneralInfo = dict(
    Conventions='CF-1.7',
    title='HMC Run Manager',
    institution='CIMA Research Foundation - www.cimafoundation.org',
    website='http://continuum.cimafoundation.org',
    source='',
    history='Python settings algorithm for running hydrological model Continuum (HMC)',
    references='http://cf-pcmdi.llnl.gov/ ; http://cf-pcmdi.llnl.gov/documents/cf-standard-names/ecmwf-grib-mapping',
    authors='Fabio Delogu',
    email='fabio.delogu@cimafoundation.org',
    project='FloodProofs - Hydrological Model Continuum',
    version="2.0.7",
    date="20180521"
)

# Settings parameters info
oParamsInfo = dict(
    Run_Params={
        'RunDomain': '$DOMAIN',
        'RunName': '$RUN',
        'RunMode': {'EnsMode': False,
                    'EnsVar':
                        {'VarName': '',
                         'VarMin': 0,
                         'VarMax': 0,
                         'VarStep': 0},
                    },
    },

    Run_VarExec={
        'RunModelExec': 'HMC_Model_V2_$RUN.x',
        'RunModelNamelist': '$DOMAIN.info.txt',
        'RunModelCLine': '$UC $UH $CT $CF $DOMAIN $CPI $RF $VMAX $SLOPEMAX',
    },

    Run_ConfigFile={
        'FileData': 'hmc_configuration_variables_default.json',
        'FileLog': 'hmc_logging_default.txt',
    },

    Run_Path={
        'PathTemp': '/Temp',
        'PathCache': '/Cache',
        'PathExec': '/Exec',
        'PathLibrary': '/Library',
    },

    Time_Params={
        'TimeNow': '197805221255',
        'TimeDelta': 0,
        'TimeStepObs': 0,
        'TimeStepFor': 0,
        'TimeStepCheck': 0,
        'TimeRestart': {'RestartStep': 0, 'RestartHH': '00'},
        'TimeWorldRef': {'RefType': 'gmt', 'RefLoad': 0, 'RefSave': 0},
        'TimeTcMax': -9999,
    },

    HMC_Params={
        'Ct': -9999,
        'Cf': -9999,
        'Uc': -9999,
        'Uh': -9999,
        'CPI': -9999,
        'Rf': -9999,
        'VMax': -9999,
        'SlopeMax': -9999,
    },

    HMC_Flag={
        'Flag_OS': -9999,
        'Flag_Restart': -9999,
        'Flag_FlowDeep': -9999,
        'Flag_Uc': -9999,
        'Flag_DtPhysConv': -9999,
        'Flag_Snow': -9999,
        'Flag_Snow_Assim': -9999,
        'Flag_DebugSet': -9999,
        'Flag_DebugLevel': -9999,
        'Flag_LAI': -9999,
        'Flag_Albedo': -9999,
    },

    HMC_Dt={
        'Dt_Model': -9999,
        'Dt_PhysConv': -9999,
    },

    HMC_Data={
        'ForcingGridSwitch': -9999,
        'ForcingScaleFactor': -9999,
        'ForcingGeo': [-9999.0, -9999.0],
        'ForcingRes': [-9999.0, -9999.0],
        'ForcingDims': [-9999, -9999],
        'ForcingDataThr': 90,
    },

)

# Settings geographical info
oGeoSystemInfo = dict(
    epsg_code=4326,
    grid_mapping_name='latitude_longitude',
    longitude_of_prime_meridian=0.0,
    semi_major_axis=6378137.0,
    inverse_flattening=298.257223563,
)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Resume dictionary
oDataSettings = dict(GeneralInfo=oGeneralInfo, ParamsInfo=oParamsInfo, GeoSystemInfo=oGeoSystemInfo)
# -------------------------------------------------------------------------------------
