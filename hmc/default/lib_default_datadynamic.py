"""
Library Features:

Name:          lib_default_datadynamic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

# -------------------------------------------------------------------------------------
# Data input dynamic dictionary
oDataForcing = dict(
    Gridded=
    {'FileName': 'hmc.forcing-grid.$yyyy$mm$dd$HH$MM.nc',
     'FilePath': '/$RUN/forcing/$yyyy/$mm/$dd/',
     'FileType': 2,
     'FileTimeRes': 3600,
     'FileVars':
         {'OBS':
             {'VarResolution': 3600,
              'VarArrival': {'Day': 1, 'Hour': None},
              'VarOp': {'Merging': None, 'Splitting': None},
              'VarStep': 1,
              'VarDims': {'X': 'west_east', 'Y': 'south_north'},
              'VarName':
                 {'Rain':
                     {'FileName': 'ws.db.$yyyy$mm$dd$HH$MM.nc.gz',
                      'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                      'FileTag': 'Rain'},
                  'AirTemperature':
                      {'FileName': 'ws.db.$yyyy$mm$dd$HH$MM.nc.gz',
                       'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                       'FileTag': 'AirTemperature'},
                  'Wind':
                      {'FileName': 'ws.db.$yyyy$mm$dd$HH$MM.nc.gz',
                       'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                       'FileTag': 'Wind'},
                  'RelHumidity':
                      {'FileName': 'ws.db.$yyyy$mm$dd$HH$MM.nc.gz',
                       'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                       'FileTag': 'RelHumidity'},
                  'IncRadiation':
                      {'FileName': 'ws.db.$yyyy$mm$dd$HH$MM.nc.gz',
                       'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                       'FileTag': 'IncRadiation'},
                  'AirPressure':
                      {'FileName': 'ws.db.$yyyy$mm$dd$HH$MM.nc.gz',
                       'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                       'FileTag': 'AirPressure'},
                  },
              },
          'FOR':
              {'VarResolution': 3600,
               'VarArrival': {'Day': 1, 'Hour': ['00', '12'], },
               'VarOp': {'Merging': None, 'Splitting': None},
               'VarStep': 72,
               'VarDims': {'X': 'west_east', 'Y': 'south_north', 'time': 'time'},
               'VarName':
                   {'Rain':
                       {'FileName': 'nwp.lami.$yyyy$mm$dd0000.nc.gz',
                        'FilePath': '/data_for/$yyyy/$mm/$dd/',
                        'FileTag': 'Rain'},
                    'AirTemperature':
                        {'FileName': 'nwp.lami.$yyyy$mm$dd0000.nc.gz',
                         'FilePath': '/data_for/$yyyy/$mm/$dd/',
                         'FileTag': 'AirTemperature'},
                    'Wind':
                        {'FileName': 'nwp.lami.$yyyy$mm$dd0000.nc.gz',
                         'FilePath': '/data_for/$yyyy/$mm/$dd/',
                         'FileTag': 'Wind'},
                    'RelHumidity':
                        {'FileName': 'nwp.lami.$yyyy$mm$dd0000.nc.gz',
                         'FilePath': '/data_for/$yyyy/$mm/$dd/',
                         'FileTag': 'RelHumidity'},
                    'IncRadiation':
                        {'FileName': 'nwp.lami.$yyyy$mm$dd0000.nc.gz',
                         'FilePath': '/data_for/$yyyy/$mm/$dd/',
                         'FileTag': 'IncRadiation'},
                    'AirPressure':
                        {'FileName': 'nwp.lami.$yyyy$mm$dd0000.nc.gz',
                         'FilePath': '/data_for/$yyyy/$mm/$dd/',
                         'FileTag': 'AirPressure'},
                    },
               },
          },
     },

    Point={
        'FileName': 'hmc.forcing-point.$VAR.txt',
        'FilePath': '/$RUN/forcing/$yyyy/$mm/$dd/',
        'FileType': 1,
        'FileTimeRes': 3600,
        'FileVars':
            {'OBS':
                {'VarResolution': 3600,
                 'VarArrival': {'Day': 0, 'Hour': None},
                 'VarOp': {'Merging': None, 'Splitting': None},
                 'VarStep': 1,
                 'VarDims': {'T': 'time'},
                 'VarName':
                     {'DamV':
                          {'FileName': 'damv.db.$yyyy$mm$dd$HH$MM.txt',
                           'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                           'FileVar': 'damv'},
                      },
                 },
             'FOR': {},
             },
    },

    TimeSeries={
        'FileName': 'hmc.forcing-ts.plant_$NAME.txt',
        'FilePath': '/$RUN/forcing/$yyyy/$mm/$dd/',
        'FileType': 1,
        'FileTimeRes': None,
        'FileVars':
            {'OBS':
                 {'VarResolution': 3600,
                  'VarArrival': {'Day': 0, 'Hour': None},
                  'VarOp': {'Merging': None, 'Splitting': None},
                  'VarStep': 1,
                  'VarDims': {'T': 'time'},
                  'VarName':
                      {'DamQ':
                           {'FileName': 'hmc.forcing-ts.plant_$NAME.txt',
                            'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                            'FileVar': ''},
                       'IntakeQ':
                           {'FileName': 'hmc.forcing-ts.plant_$NAME.txt',
                            'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                            'FileVar': ''},
                       },
                  },
             'FOR': {},
             },
    },

)

# Data updating dynamic dictionary
oDataUpdating = dict(
    Gridded=
    {'FileName': 'hmc.forcing-grid.$yyyy$mm$dd$HH$MM.nc',
     'FilePath': '/$RUN/forcing/$yyyy/$mm/$dd/',
     'FileType': 2,
     'FileTimeRes': 3600,
     'FileVars':
         {'OBS':
              {'VarResolution': 3600,
               'VarArrival': {'Day': 1, 'Hour': None},
               'VarOp': {'Merging': None, 'Splitting': None},
               'VarStep': 1,
               'VarDims': {'X': 'west_east', 'Y': 'south_north'},
               'VarName':
                   {'SnowHeight':
                        {'FileName': 'ws.db.$yyyy$mm$dd$HH$MM.nc.gz',
                         'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                         'FileVar': 'SnowLevel'},
                    'SnowKernel':
                        {'FileName': 'ws.db.$yyyy$mm$dd$HH$MM.nc.gz',
                         'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                         'FileVar': 'SnowKernel'},
                    'SnowCoverArea':
                        {'FileName': 'MOD10A1.005_$DOMAIN_$yyyy$mm$dd$HH$MM.nc.gz',
                         'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                         'FileVar': 'snow_cover_daily'},
                    'SnowQualityArea':
                        {'FileName': 'MOD10A1.005_$DOMAIN_$yyyy$mm$dd$HH$MM.nc.gz',
                         'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                         'FileVar': 'snow_spatial_qa_filter'}
                    },
               },
          'FOR': {},
          },
     },
)

# Data output dynamic dictionary
oDataOutcome = dict(
    Gridded={
        'FileName': 'hmc.output-grid.$yyyy$mm$dd$HH$MM.nc.gz',
        'FilePath': '/$RUN/Data/outcome/$yyyy/$mm/$dd/$MODE/',
        'FileType': 2,
        'FileTimeRes': 3600,
        'FileVars':
            {'ARCHIVE':
                {'VarResolution': 3600,
                 'VarArrival': {'Day': 0, 'Hour': None},
                 'VarOp': {'Merging': None, 'Splitting': None},
                 'VarStep': 1,
                 'VarDims': {'X': 'west_east', 'Y': 'south_north'},
                 'VarName':
                     {'ALL':
                          {'FileName': 'hmc.output-grid.$yyyy$mm$dd$HH$MM.nc.gz',
                           'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/map/$MODE/',
                           'FileVar': 'ALL'},
                      },
                 },
             },
    },
    Point={
        'FileName': 'hmc.$VAR.$yyyy$mm$dd$HH$MM.txt',
        'FilePath': '/$RUN/Data/outcome/$yyyy/$mm/$dd/$MODE/',
        'FileType': 1,
        'FileTimeRes': 3600,
        'FileVars':
            {'ARCHIVE':
                {'VarResolution': 3600,
                 'VarArrival': {'Day': 0, 'Hour': None},
                 'VarOp': {'Merging': None, 'Splitting': None},
                 'VarStep': 1,
                 'VarDims': {'T': 'time'},
                 'VarName':
                     {'Discharge':
                          {'FileName': 'hmc.discharge.$yyyy$mm$dd$HH$MM.txt',
                           'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/point/$MODE/',
                           'FileVar': 'discharge'},
                      'DamV':
                          {'FileName': 'hmc.vdam.$yyyy$mm$dd$HH$MM.txt',
                           'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/point/$MODE/',
                           'FileVar': 'vdam'},
                      'DamL':
                          {'FileName': 'hmc.ldam.$yyyy$mm$dd$HH$MM.txt',
                           'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/point/$MODE/',
                           'FileVar': 'ldam'},
                      'VarAnalysis':
                          {'FileName': 'hmc.var-analysis.$yyyy$mm$dd$HH$MM.txt',
                           'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/point/$MODE/',
                           'FileVar': 'var-analysis'},
                      },
                 },
             },
        },
    TimeSeries={
         'FileName': 'hmc.$VAR.$yyyy$mm$dd$HH$MM.txt',
         'FilePath': '/$RUN/Data/outcome/$yyyy/$mm/$dd/$MODE/',
         'FileType': 1,
         'FileTimeRes': 3600,
         'FileVars': {
             'ARCHIVE': {
                 'VarResolution': 3600,
                 'VarArrival': {'Day': 0, 'Hour': None},
                 'VarOp': {'Merging': None, 'Splitting': None},
                 'VarStep': 1,
                 'VarDims': {'T': 'time'},
                 'VarName':
                     {'Discharge':
                         {'FileName': 'hmc.discharge.txt',
                          'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/timeseries/$MODE/',
                          'FileVar': 'discharge'},
                      'DamV':
                          {'FileName': 'hmc.vdam.txt',
                           'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/timeseries/$MODE/',
                           'FileVar': 'vdam'},
                      'DamL':
                          {'FileName': 'hmc.ldam.txt',
                           'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/timeseries/$MODE/',
                           'FileVar': 'ldam'},
                      'VarAnalysis':
                          {'FileName': 'hmc.var-analysis.txt',
                           'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/timeseries/$MODE/',
                           'FileVar': 'var-analysis'},
                 },
             },
             'DEWETRA': {
                'VarResolution': 3600,
                'VarArrival': {'Day': 0, 'Hour': None},
                'VarOp': {'Merging': None, 'Splitting': None},
                'VarStep': 1,
                'VarDims': {'T': 'time'},
                'VarName':
                    {'Discharge':
                         {'FileName': 'hydrograph_$SECTION_$DOMAIN_$yyyy$mm$dd$HH$MM.txt',
                          'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/timeseries/$MODE/',
                          'FileVar': 'hydrograph'},
                     },
             },
        },
    },
)

# Data state dynamic dictionary
oDataState = dict(
    Gridded={
        'FileName': 'hmc.state-grid.$yyyy$mm$dd$HH$MM.nc.gz',
        'FilePath': '/run/$RUN/Data/state/$yyyy/$mm/$dd/$MODE/',
        'FileType': 2,
        'FileTimeRes': 86400,
        'FileVars':
            {'ARCHIVE':
                {'VarResolution': 86400,
                 'VarArrival': {'Day': 0, 'Hour': None},
                 'VarOp': {'Merging': None, 'Splitting': None},
                 'VarStep': 1,
                 'VarDims': {'X': 'west_east', 'Y': 'south_north'},
                 'VarName':
                    {'ALL':
                        {'FileName': 'hmc.state-grid.$yyyy$mm$dd$HH$MM.nc.gz',
                         'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/state/$MODE/',
                         'FileVar': 'ALL'
                         },
                     },
                 },
             },
        },
    Point={
        'FileName': 'hmc.state-point.$yyyy$mm$dd$HH$MM.txt',
        'FilePath': '/run/$RUN/Data/state/$yyyy/$mm/$dd/$MODE/',
        'FileType': 1,
        'FileTimeRes': 86400,
        'FileVars':
            {'ARCHIVE':
                {'VarResolution': 86400,
                 'VarArrival': {'Day': 0, 'Hour': None},
                 'VarOp': {'Merging': None, 'Splitting': None},
                 'VarStep': 1,
                 'VarDims': {'T': 'time'},
                 'VarName':
                    {'ALL':
                        {'FileName': 'hmc.state-point.$yyyy$mm$dd$HH$MM.txt',
                         'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/state/$MODE/',
                         'FileVar': 'ALL',
                         },
                     },
                 },
             },
        },
)

# Data restart dynamic dictionary
oDataRestart = dict(
    Gridded={
        'FileName': 'hmc.state-grid.$yyyy$mm$dd$HH$MM.nc',
        'FilePath': '/run/$RUN/Data/restart/$yyyy/$mm/$dd/$MODE/',
        'FileType': 2,
        'FileTimeRes': 86400,
        'FileVars':
            {'ARCHIVE':
                {'VarResolution': 86400,
                 'VarArrival': {'Day': 0, 'Hour': ['00']},
                 'VarOp': {'Merging': None, 'Splitting': None},
                 'VarStep': 1,
                 'VarDims': {},
                 'VarName':
                    {'ALL':
                        {'FileName': 'hmc.state-grid.$yyyy$mm$dd$HH$MM.nc.gz',
                         'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/state/$MODE/',
                         'FileVar': 'ALL'
                         },
                     },
                 },
             },
    },
    Point={
        'FileName': 'hmc.state-point.$yyyy$mm$dd$HH$MM.txt',
        'FilePath': '/run/$RUN/Data/restart/$yyyy/$mm/$dd/$MODE/',
        'FileType': 1,
        'FileTimeRes': 86400,
        'FileVars':
            {'ARCHIVE':
                {'VarResolution': 86400,
                 'VarArrival': {'Day': 0, 'Hour': ['00']},
                 'VarOp': {'Merging': None, 'Splitting': None},
                 'VarStep': 1,
                 'VarDims': {'T': 'time'},
                 'VarName':
                    {'ALL':
                        {'FileName': 'hmc.state-point.$yyyy$mm$dd$HH$MM.txt',
                         'FilePath': '/archive/$RUN/$yyyy/$mm/$dd/$HH/state/$MODE/',
                         'FileVar': 'ALL',
                         },
                     },
                 },
             },
    },
)

oDataObs = dict(
    Point={
        'FileName': 'hmc.$VAR.$yyyy$mm$dd$HH$MM.txt',
        'FilePath': '/$RUN/forcing/$yyyy/$mm/$dd/',
        'FileType': 1,
        'FileTimeRes': 3600,
        'FileVars':
            {'ARCHIVE':
                 {'VarResolution': 3600,
                  'VarArrival': {'Day': 0, 'Hour': None},
                  'VarOp': {'Merging': None, 'Splitting': None},
                  'VarStep': 1,
                  'VarDims': {'T': 'time'},
                  'VarName':
                      {'Discharge':
                           {'FileName': 'rs.db.$yyyy$mm$dd$HH$MM.txt',
                            'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                            'FileVar': 'discharge'},
                       'DamV':
                           {'FileName': 'damv.db.$yyyy$mm$dd$HH$MM.txt',
                            'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                            'FileVar': 'damv'},
                       'DamL':
                           {'FileName': 'daml.db.$yyyy$mm$dd$HH$MM.txt',
                            'FilePath': '/data_obs/$yyyy/$mm/$dd/',
                            'FileVar': 'daml'},
                       },
                  },
             },
    },
)

oDataAllocate = dict(

    TimeSeries={
        'FileName': '',
        'FilePath': '',
        'FileVars':
            {'OBS':
                {'IntakeQ': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': 'Values'},
                 'DamQ': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': 'Values'},
                 },
             'ARCHIVE':
                 {'Discharge': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': 'Time Sections'},
                  'DamV': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': 'Time Dams'},
                  'DamL': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': 'Time Dams'},
                  'VarAnalysis': {'Data': None, 'FileName': '', 'VarName': '',
                                  'Attrs': 'Time '
                                           'Rain_Avg Rain_Max Rain_Min '
                                           'Ta_Avg Ta_Max Ta_Min '
                                           'K_Avg K_Max K_Min '
                                           'W_Avg W_Max W_Min '
                                           'RH_Avg RH_Max RH_Min '
                                           'Pa_Avg Pa_Max Pa_Min '
                                           'LAI_Avg LAI_Max LAI_Min '
                                           'Alb_Avg Alb_Max Alb_Min '
                                           'LST_Avg LST_Max LST_Min '
                                           'H_Avg H_Max H_Min '
                                           'LE_Avg LE_Max LE_Min '
                                           'ET_Avg ET_Max ET_Min '
                                           'INT_Avg INT_Max INT_Min '
                                           'VTot_Avg VTot_Max VTot_Min '
                                           'VRet_Avg VRet_Max VRet_Min '
                                           'VSub_Avg VSub_Max VSub_Min '
                                           'VLoss_Avg VLoss_Max VLoss_Min '
                                           'VExf_Avg VExf_Max VExf_Min '
                                           'FDeep_Avg FDeep_Max FDeep_Min '
                                           'WT_Avg WT_Max WT_Min'},
                  },
             },
        'FileType': 0,
        'FileTimeRes': 0,
    },

    Point={
        'FileName': '',
        'FilePath': '',
        'FileVars':
            {'OBS':
                 {'Discharge': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'DamV': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'DamL': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  },
             },
        'FileType': 0,
        'FileTimeRes': 0.
    },

    Gridded={
        'FileName': '',
        'FilePath': '',
        'FileVars':
            {'OBS':
                 {'Rain': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'AirTemperature': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'Wind': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'RelHumidity': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'IncRadiation': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'AirPressure': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'SnowHeight': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'SnowKernel': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'SnowCoverArea': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'SnowQualityArea': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'Terrain': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'Longitude': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'Latitude': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'Info': {'GeoBox': None, 'GeoHeader': None}
                  },
             'FOR':
                 {'Rain': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'AirTemperature': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'Wind': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'RelHumidity': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'IncRadiation': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'AirPressure': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'Terrain': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'Longitude': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'Latitude': {'Data': None, 'FileName': '', 'VarName': '', 'Attrs': None},
                  'Info': {'GeoBox': None, 'GeoHeader': None}
                  },
             },
        'FileType': 0,
        'FileTimeRes': 0,
    },
)

oDataAnalysis = dict(

    Gridded={'ForcingDataThr': 0.0},
    Point={'ForcingDataThr': 0.0},
)

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Resume dictionary
oDataDynamic = dict(DataForcing=oDataForcing, DataUpdating=oDataUpdating,
                    DataOutcome=oDataOutcome,
                    DataRestart=oDataRestart, DataState=oDataState,
                    DataObs=oDataObs,
                    DataAllocate=oDataAllocate, DataAnalysis=oDataAnalysis)
# -------------------------------------------------------------------------------------
