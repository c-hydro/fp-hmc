"""
Library Features:

Name:          lib_default_datastatic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

# -------------------------------------------------------------------------------------
# Data land dictionary
oDataLand = dict(

    Gridded={
        'FileName': '$DOMAIN.$VAR.txt',
        'FilePath': '/land',
        'FileVar': {'Alpha': {'Name': 'alpha', 'AlgCheck': True, 'AlgReq': False},
                    'Beta': {'Name': 'beta', 'AlgCheck': True, 'AlgReq': False},
                    'Cf': {'Name': 'cf', 'AlgCheck': True, 'AlgReq': False},
                    'Ct': {'Name': 'ct', 'AlgCheck': True, 'AlgReq': False},
                    'Uh': {'Name': 'uh', 'AlgCheck': True, 'AlgReq': False},
                    'Uc': {'Name': 'uc', 'AlgCheck': True, 'AlgReq': False},
                    'Drainage_Area': {'Name': 'area', 'AlgCheck': True, 'AlgReq': False},
                    'Channels_Distinction': {'Name': 'choice', 'AlgCheck': True, 'AlgReq': False},
                    'Cell_Area': {'Name': 'areacell', 'AlgCheck': True, 'AlgReq': False},
                    'Coeff_Resolution': {'Name': 'coeffres', 'AlgCheck': True, 'AlgReq': False},
                    'Flow_Directions': {'Name': 'pnt', 'AlgCheck': True, 'AlgReq': False},
                    'Partial_Distance': {'Name': 'partial_distance', 'AlgCheck': True, 'AlgReq': False},
                    'Vegetation_IA': {'Name': 'ia', 'AlgCheck': True, 'AlgReq': False},
                    'Vegetation_Type': {'Name': 'cn', 'AlgCheck': True, 'AlgReq': True},
                    'Terrain': {'Name': 'dem', 'AlgCheck': True, 'AlgReq': True},
                    'Mask': {'Name': 'mask', 'AlgCheck': True, 'AlgReq': False},
                    },
        'FileType': 1,
        'FileTimeRes': 0,
    },

    Point={'FileName': '$DOMAIN.info_$VAR.txt',
           'FilePath': '/point',
           'FileVars': {'Dam': {'Name': 'dam', 'AlgCheck': True, 'AlgReq': True},
                        'Intake': {'Name': 'intake', 'AlgCheck': True, 'AlgReq': False},
                        'Joint': {'Name': 'joint', 'AlgCheck': True, 'AlgReq': False},
                        'Lake': {'Name': 'lake', 'AlgCheck': True, 'AlgReq': False},
                        'Section': {'Name': 'section', 'AlgCheck': True, 'AlgReq': True},
                        },
           'FileType': 1,
           'FileTimeRes': 0.
           },

)

oDataAllocate = dict(
    Point={
        'FileName': '',
        'FilePath': '',
        'FileVars': {'Dam': {'Data': None, 'FileName': '', 'Attrs': None},
                     'Section': {'Data': None, 'FileName': '', 'Attrs': None},
                     'Info': {},
                    },
        'FileType': 0,
        'FileTimeRes': 0.
    },

    Gridded={
        'FileName': '',
        'FilePath': '',
        'FileVars': {'Vegetation_Type': {'Data': None, 'FileName': '', 'Attrs': None},
                     'Terrain': {'Data': None, 'FileName': '', 'Attrs': None},
                     'Longitude': {'Data': None, 'FileName': '', 'Attrs': None},
                     'Latitude': {'Data': None, 'FileName': '', 'Attrs': None},
                     'Info': {'GeoBox': None, 'GeoHeader': None,
                              'Forcing': {'LLCorner': None, 'Resolution': None, 'Dims': None, 'ScaleFactor': None},
                              },
                    },
        'FileType': 0,
        'FileTimeRes': 0,
    },
)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Resume dictionary
oDataStatic = dict(DataLand=oDataLand, DataAllocate=oDataAllocate)
# -------------------------------------------------------------------------------------
