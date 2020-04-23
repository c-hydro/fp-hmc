============
Applications
============

The **HMC python3 package** is a library to wrap the HMC model into a python environment; 
generally, the python part performs all the actions that are needed to configure and run the model. 
All the model codes are available in the **HMC model package**; the routines
about the model computational part are written in Fortran2003 programming language and
they are linked and controlled by the python library. The workflow between **HMC python3 package** 
and **HMC model package** is reported below:

.. graphviz::

    digraph {
      compound=true;
      subgraph cluster_hmc_model_package {
        
        label = "HMC Python3 package";

        land_data [label = "Land Data"]
        forcing_data [label = "Forcing Data"]
        restart_data [label = "Restart Data"]
        updating_data [label = "Updating Data"]
        outcome_data [label = "Outcome Data"]
        state_data [label = "State Data"]
        
        land_data -> hmc_model_core [lhead=cluster_hmc_model_core, minlen=2];
        forcing_data -> hmc_model_core [lhead=cluster_hmc_model_core, minlen=2];
        restart_data -> hmc_model_core [lhead=cluster_hmc_model_core, minlen=2];
        updating_data -> hmc_model_core [lhead=cluster_hmc_model_core, minlen=2];

        subgraph cluster_hmc_model_core {
          label = "HMC model package";
          hmc_model_core [shape=polygon, sides=4, label = "HMC core"]
        }

        hmc_model_core -> outcome_data [ltail=cluster_hmc_model_core, minlen=1];
        hmc_model_core -> state_data [ltail=cluster_hmc_model_core, minlen=1];
    }
  }

Generally, the applications for running HMC, available in the HMC python3 package, are able to:
   * prepare the HMC namelist file;
   * collect and control HMC land data;
   * collect and control HMC forcing, restart and updating data;
   * run HMC using namelist, land and forcing data;
   * save and organize HMC state and outcome data. 

The running applications require two default arguments to set model and time information:

1. -settings_file
2. -time

The first argument [-settings_file], for running the HMC model, is a **configuration file**; it 
is mandatory to run the  HMC model because all the information, needed by the HMC simulations, are 
set in this configuration file; the second argoment [-time] is the **model simulation time** for 
applying model in a selected date. 

The structure of HMC python3 package is shown below.

::

    hmc-master
    ├── **apps**
    │   ├── HMC_Model_Run_Manager.py
    │   ├── configuration_run_app_1.json
    │   ├── configuration_run_app_2.json
    │   ├── configuration_data_app_1.json
    │   ├── configuration_data_app_2.json
    │   └── ...
    ├── bin
    │   ├── local
    │   ├── server
    │   └── ...
    ├── docs
    ├── hmc
    ├── AUTHORS.rst
    ├── CHANGELOG.rst
    ├── LICENSE.rst
    └── README.rst

The application for running HMC model and all its part is named "HMC_Model_Run_Manager.py" and, in the following 
line, the generic usage of this procedure is reported: 

.. code-block:: bash

  >> python3 HMC_Model_RUN_Manager.py -settings_file configuration.json -time "yyyymmddHHMM"

Configuration file
******************

As previously said, the HMC python3 package needs two arguments to run the HMC model over a 
domain during a selected period, The first arguments [-settings_file] is a **configuration file** 
in JSON format, usually named **hmc_configuration_{domain}_{run}.json**; this file is used to set 
all information needed by the model. The second arguments [-time] is the **model simulation time** 
in 'yyyymmddHHMM' format. 

The available sections in the configuration file are:
* General Info
* Parameters Info
* Geographical Info  

The **General Info** section is used to store information about the version and the release date of the model,
the conventions used by input/output files, the authors and their contacts, the reference project and so on. 
An example of GeneralInfo data structure is reported in the following block.

.. code-block:: json

    {
      "Conventions": "CF-1.7",
      "title": "HMC Run Manager", 
      "institution": "CIMA Research Foundation - www.cimafoundation.org",
      "website": "",
      "source": "",
      "history": "Python settings algorithm for running hydrological model Continuum (HMC)",
      "references": "http://cf-pcmdi.llnl.gov/ ; http://cf-pcmdi.llnl.gov/documents/cf-standard-names/ecmwf-grib-mapping",
      "authors": "Fabio Delogu",
      "email": "",
      "project": "HMC Project",
      "version": "2.0.7",
      "date": "20180521"
    }

The **Parameters Info** section is used to store information about the model configuration. 
This part present different subsections that users have to fill before running the HMC model. 

+ **Run_Params**
	
  In this subsection, users have to decide information about the run type:

  * RunDomain is the reference name for the domain.
  * RunName is the reference name for the run.
  * RunMode is the configuration of the run (deterministic or probabilistic); the flag EnsMode 
    should be set using a boolean operator equal to "false" for deterministic run and equal 
    to "true" for probabilistic run. If probabilistic mode is activated, 
    the name of variable, used by the ensemble, and its limits have to be set.
    
  In the example, a nwp probabilistic run of 30 ensembles over the Italy domain is reported.

	.. code-block:: json

		{
		"RunDomain": "italy",
	  	"RunName": "italy_nwp_probabilistic",
	  	"RunMode": 
			{"EnsMode": true,
			 "EnsVar": {"VarName": "RFarm_ID", "VarMin": 1, "VarMax": 30, "VarStep": 1} }
	 	}

+ **Run_VarExec**

  In this subsection, users have to fill the fields for setting model executable. Particularly:

  * RunModelExec is the name of the model executable (where $RUN is the name of the run).
  * RunModelNamelist is the name of model namelist (where $DOMAIN is the name of domain).
  * RunModelCLine is the command line to execute the model and $UC, $UH, $CT, $CF, 
    $DOMAIN, $CPI, $KSATRATIO, $WTABLEHBR, $SLOPEMAX are the parameters requested by the model.
  
  In the example, generic executable and namelist files are set in configuration file.
	
	.. code-block:: json

		{
		"RunModelExec": "HMC_Model_V2_$RUN.x",
		"RunModelNamelist": "$DOMAIN.info.txt",
		"RunModelCLine": "$UC $UH $CT $CF $DOMAIN $CPI $KSATRATIO $WTABLEHBR $SLOPEMAX"
		}

+ **Run_ConfigFile**

  In this subsection, users have to decide the following arguments:
  
  * FileData is the configuration file of the datasets that will be used by the model execution.
  * FileLog is the logging file that will be used by both HMC python3 package and HMC model package 
    for saving log and debug information.
  
  In the example, the configurations files are defined for a probabilistic run of Italy domain.

	.. code-block:: json

		{
		"FileData": "hmc_configuration_data_italy_nwp_probabilistic.json",
		"FileLog": "hmc_logging_italy_nwp_probabilistic.txt"
		}

+ **Run_Path**

  In this subsection, users have to set useuful paths needed by the model execution. 
  
  * PathTemp is the temporary path.
  * PathCache is the cache path.
  * PathExec is the execution path (where copy executable and namelist files). 
  * PathLibrary is the library path where HMC Fortran2003 codes are build.
  
  The example shows how to organize a model execution using a root path named "run"; 
  all the pahs are generic and use $RUN and $MODE to specify the running paths. 

	.. code-block:: json

		{
		"PathTemp": "/run/$RUN/temp/$MODE/",
		"PathCache": "/run/$RUN/cache/$MODE/$yyyy/$mm/$dd/$HH/",
		"PathExec": "/run/$RUN/exec/$MODE/",
		"PathLibrary": "/library/"
		}

+ **Time_Params**

  In this subsection, users have to set the information about time. The meaning of each field is 
  defined as follows:

  * TimeNow is the simulation time in "yyyymmddHHMM"; if the value is set to "null", TimeNow is 
    defined according with the machine time.
  * TimeDelta is the time frequency of data (forcing, updating, restart, state and outcome) [seconds]
  * TimeStepObs is the running period of observed data steps.
  * TimeStepFor is the running period of forecast data steps.
  * TimeStepCheck is the checking period of observed data steps (in operational mode).
  * TimeRestart is used to set the restart time; starting from the previous "RestartStep" value until the time
    step hour is not equal to "RestartHH" value.
  * TimeWorldRef is defined by two values: 'gmt' or 'local'.
  * TimeTcMax is the maximum corrivation time; if the parameter is set to "-9999", the value is automatically
    computed as function of Digital Terrain Model static layer.

  In the example above, a configuration of operational run with data each 3600 [seconds] is reported; 
  the execution takes care both the observed part (10 steps) and the forecast part (36 steps); the period 
  for checking data is set (4 steps) and the restart part is configured (at least 24 steps in the past 
  at 00.00). The reference time is "gmt" and the corrivation time is calculated using the 
  information of the Digital Terrain Model.

	.. code-block:: json

		{
		"TimeNow": null,
		"TimeDelta": 3600,
		"TimeStepObs": 10,
		"TimeStepFor": 36,
		"TimeStepCheck": 4,
		"TimeRestart": {"RestartStep": 24, "RestartHH": "00"},
		"TimeWorldRef": {"RefType": "gmt", "RefLoad": 0, "RefSave": 0},
		"TimeTcMax": -9999
		}

+ **HMC_Params**

  In this subsection, users have to set the parameters of the HMC model; these values are
  avarage over the domain; in case of a distributed file for Ct, Cf, Uc and Uh is available
  the value will be overwritten during the model simulation. For further information of the 
  meaning and validity range of each parameter see the :doc:`description <../description>` section. 
  
  In the following example, the default value for each parameter.
   
	.. code-block:: json

		{
		"Ct": 0.5,
		"Cf": 0.02,
		"Uc": 20,
		"Uh": 1.5,
		"CPI": 0.3,
		"KSatRatio": 1,
		"WTableHbr": 500,
		"SlopeMax": 70
		}

+ **HMC_Flag**

  In this subsection, users have to decide which physics or conditions have to be activated
  or not. The meaning of each of them is defined as follows:
  
  * Flag_OS
      - 1 Windows machine
      - 10 Linux Debian/Ubuntu machine
  * Flag_Restart
      - 1 to activate restart conditions.
      - 0 to deactivate restart condition (default starting condition).
  * Flag_FlowDeep
      - 1 to activate the flow deep flow
      - 0 to deactivate the flow deep flow
  * Flag_DtPhysConv
      - 1 to use a dynamic integration convolution step
      - 0 to use a static integration convolution step 
  * Flag_Snow
      - 1 to activate snow physics
      - 0 to deactivate snow physics
  * Flag_Snow_Assim
      - 1 to activate assimilation of snow variables
      - 0 to deactivate assimilation of snow variables
  * Flag_SM_Assim
      - 1 to activate assimilation of soil moisture variable
      - 0 to deactivate assimilation of soil moisture variable
  * Flag_LAI
      - 1 to use a LAI datasets
      - 0 to use an empiric relationship
  * Flag_Albedo
      - 1 to use a dynamic monthly values
      - 0 to use a static value
  * Flag_CoeffRes
      - 1 to use an empiric relationship
      - 0 to not use an empiric relationship (null)
  * Flag_WS
      - 1 to use the water sources mode
      - 0 to not use the water sources mode
  * Flag_ReleaseMass
      - 1 to use the mass balance control
      - 0 to not use the mass balance control
  * Flag_DebugSet
      - 1 to activate debugging mode
      - 0 to deactivate debugging mode
  * Flag_DebugLevel
      - 0 to set debugging mode to BASIC info
      - 1 to set debugging mode to MAIN info
      - 2 to set debugging mode to VERBOS info
      - 3 to set debugging mode to EXTRA info

  An example of flags configuration is reported below; in this case, the
  assimilation of soil moisture variable and the snow physics are activated.
  The debug is set to 0 for running in operational mode without extra 
  information in logging file. 

	.. code-block:: json

		{
		"Flag_OS": 10,
		"Flag_Restart": 1,
		"Flag_FlowDeep": 1,
		"Flag_DtPhysConv": 1,
		"Flag_Snow": 1,
		"Flag_Snow_Assim": 0,
		"Flag_SM_Assim": 1,
		"Flag_DebugSet": 0,
		"Flag_DebugLevel": 3,
		"Flag_CoeffRes": 0,
		"Flag_WS": 0,
		"Flag_ReleaseMass": 1,
		"Flag_LAI": 0,
		"Flag_Albedo": 0
		}

+ **HMC_Dt**

  In this subsection, users have to set the dt of the model. The meaning of the parameters
  is reported below:

  * Dt_Model is used to set the model step [seconds]
  * Dt_PhysConv is used to set the convolution integration step [seconds]
  
  For example in the following block, the Dt of the model is set to 3600 [seconds] and the 
  convolution integration step is 50 [seconds].
    
  .. code-block:: json
  
    {
    "Dt_Model": 3600,
    "Dt_PhysConv": 50
    } 
   
+ **HMC_Data**

  In this subsection, users have to set data forcing attributes if data used
  by the model are in binary format (old versions). 
  In the following list, the meaning of each variable is shown:
    
  * ForcingGridFactor is equal to 10, 100 or 1000 if binary data were saved, using a scale factor, in integer 
    type
  * ForcingGeo is the LowerLeft corner of the reference Digital Terrain Model
  * ForcingRes is the resolution of the reference Digital Terrain Model
  * ForcingDataThr is the minimum threshold of valid data used during 
    the model running [%]

The example above reported a condition with the data are not in binary format.
The minimum threshold of valid data is set to 95 [%].

	.. code-block:: json

		{
		"ForcingGridSwitch": 0,
		"ForcingScaleFactor": -9999,
		"ForcingGeo": [-9999.0, -9999.0],
		"ForcingRes": [-9999.0, -9999.0],
		"ForcingDims": [-9999.0, -9999.0],
		"ForcingDataThr": 95
		}

The **GeoSysten Info** section is used to store information about the geographical reference of the data.
Usually, in HMC model the reference epsg is 4326 (`WGS 84 -- WGS84 - World Geodetic System 1984`_). 

In the example, all the information needed by the model to correctly georeferecing data in the epsg 4326 system.

.. code-block:: json

	{
	"epsg_code": 4326,
	"grid_mapping_name": "latitude_longitude",
	"longitude_of_prime_meridian": 0.0,
	"semi_major_axis": 6378137.0,
	"inverse_flattening": 298.257223563
	}

.. _WGS 84 -- WGS84 - World Geodetic System 1984: https://epsg.io/4326

Model settings
--------------



Data settings
-------------

The data settings file is divided in different sections to set all the datasets needed
by the model for performing simulations. The available sections are reported below:

* Data Land
* Data Forcing
* Data Updating
* Data Outcome
* Data State
* Data Restart

In all section we can defined name, location, type, time resolution and variables of
each datasets.

Data Land
.........

The Data Land part is used to specify the features of static data needed by HMC to initilize
physics and parameters variables. Two data flags are set for configuring algorithm:

* AlgCheck: to check if file is available into data folder;
* AlgReq: to set if a variable is mandatory (true) or ancillary (false).

It is possible to specify two type of datasets; Gridded datasets are in ASCII format raster, Point datasets
are defined using both a shapefile (section) and a generic ASCII file (dam, intake, joint, lake).

* Gridded
    - Alpha --> angle alpha map for defining watertable 
    - Beta --> angle beta map for defining watertable
    - Cf --> Cf parameter map
    - Ct --> Ct parameter map
    - Uh --> Uh parameter map
    - Uc --> Uc parameter map 
    - Drainage_Area --> drained area map [-]
    - Channels_Distinction --> hills and channels map [0, 1]
    - Cell_Area --> cell area map [km^2]
    - Coeff_Resolution --> coefficient resolution map [-]
    - Flow_Directions --> flow directions map [1, 2, 3, 4, 6, 7, 8, 9]
    - Partial_Distance --> partial distance map [-]
    - Vegetation_IA --> vegetation retention map [-]
    - Vegetation_Type --> curve number [-]
    - Terrain --> digital terrain model [m]
    - Mask --> domain mask [0, 1]
    - WaterSource --> water sources map [-]
    - Nature --> nature map [0, 100]

Gridded data are saved in ASCII format raster; the file begins with header information that defines 
the properties of the raster such as the cell size, the number of rows and columns, and the 
coordinates of the origin of the raster. The header information is followed by cell value 
information specified in space-delimited row-major order, with each row seperated by a carraige return. 
In order to convert an ASCII file to a raster, the data must be in this same format. The parameters 
in the header part of the file must match correctly with the structure of the data values.
The basic structure of the ASCII raster has the header information at the beginning of the file 
followed by the cell value data.

* Point
    - Dam --> to define index positions and features of dam(s)
    - Intake --> to define index positions and features of intake(s)
    - Joint --> to define index positions and features of joint(s)
    - Lake --> to define index positions and features of lake(s)
    - Section --> to define index positions of outlet section(s) 

.. code-block:: json

  {
  "Gridded"     : {
    "FileName"    : "$DOMAIN.$VAR.txt",
    "FilePath"    : "$HOME/hmc-ws/data/static/land/",
    "FileType"    : 1,
    "FileTimeRes" : null,
    "FileVars"    : {
      "Alpha"                 : {"Name": "alpha",             "AlgCheck": true,   "AlgReq": false },
      "Beta"                  : {"Name": "beta",              "AlgCheck": true,   "AlgReq": false },
      "Cf"                    : {"Name": "cf",                "AlgCheck": true,   "AlgReq": false },
      "Ct"                    : {"Name": "ct",                "AlgCheck": true,   "AlgReq": false },
      "Uh"                    : {"Name": "uh",                "AlgCheck": true,   "AlgReq": false },
      "Uc"                    : {"Name": "uc",                "AlgCheck": true,   "AlgReq": false },
      "Drainage_Area"         : {"Name": "area",              "AlgCheck": true,   "AlgReq": false },
      "Channels_Distinction"  : {"Name": "choice",            "AlgCheck": true,   "AlgReq": false },
      "Cell_Area"             : {"Name": "areacell",          "AlgCheck": true,   "AlgReq": false },
      "Coeff_Resolution"      : {"Name": "coeffres",          "AlgCheck": true,   "AlgReq": false },
      "Flow_Directions"       : {"Name": "pnt",               "AlgCheck": true,   "AlgReq": false },
      "Partial_Distance"      : {"Name": "partial_distance",  "AlgCheck": true,   "AlgReq": false },
      "Vegetation_IA"         : {"Name": "ia",                "AlgCheck": true,   "AlgReq": false },
      "Vegetation_Type"       : {"Name": "cn",                "AlgCheck": true,   "AlgReq": true  },
      "Terrain"               : {"Name": "dem",               "AlgCheck": true,   "AlgReq": true  },
      "Mask"                  : {"Name": "mask",              "AlgCheck": true,   "AlgReq": false },
      "WaterSource"           : {"Name": "ws",                "AlgCheck": true,   "AlgReq": false },
      "Nature"                : {"Name": "nature",            "AlgCheck": true,   "AlgReq": false }
    }
  },
  "Point": {
    "FileName"    : "$DOMAIN.info_$VAR.txt",
    "FilePath"    : "$HOME/hmc-ws/data/static/point/",
    "FileType"    : 1,
    "FileTimeRes" : null,
    "FileVars"    : {
      "Dam"                   : {"Name": "dam",               "AlgCheck": true,   "AlgReq": true  },
      "Intake"                : {"Name": "intake",            "AlgCheck": true,   "AlgReq": true  },
      "Joint"                 : {"Name": "joint",             "AlgCheck": true,   "AlgReq": false },
      "Lake"                  : {"Name": "lake",              "AlgCheck": true,   "AlgReq": false },
      "Section"               : {"Name": "section",           "AlgCheck": true,   "AlgReq": true  }
    }
  }


example of file(s) here


Data Forcing
............

The Data Forcing part is used to specify the features of the forcing data needed by HMC to properly
run, compute physics variables and obtain related results. 
Usually, the forcing data used by the model can be divided in three main groups:

    - Gridded
    - Point
    - Time Series

For each group, some features have to be set to configure its generic part:

    - FileName: generic name of the forcing data file(s) [example: "hmc.forcing-grid.$yyyy$mm$dd$HH$MM.nc"].
    - FilePath: generic path of the forcing data file(s) [example: "$HOME/hmc-ws/run/$RUN/data/forcing/$MODE/gridded/$yyyy/$mm/$dd/"].
    - FileType: flag for defining the format of the forcing data file(s) in netCDF format [2]. 
    - FileTimeRes: resolution time of the forcing data file(s) in seconds [example: 3600].
    - FileVars: variables available in the specified file(s).

The variables included in each group are defined by the attributes in the "FileVars" section; these attributes
are used by the model routines to get and use data, read related information and prevent unexpected failures.

* Gridded

The forcing gridded files are in netCDF format; the forcing data are divided in two different types of variables:

    - OBS: to define the observed dataset (if needed).
    - FOR: to define the forecast dataset (if needed).

Each variable, in OBS and FOR section, is defined by a list of attributes in order to correctly parser the 
information; the attributes available are reported below:

    - VarResolution: resolution time of the variable in seconds [example: 3600].
    - VarArrival: arrival time of the variable.
        - Day: to define the variable arrival day [example: 0].
        - Hour: to define the variable arrival hour [example: null].
    - VarOp: ancillary defined operations of the variable.
        - Merging: to merge variable from different sources in a common dataset [example: true].
        - Splitting: to split variable in different time steps [example: false].
    - VarStep: step of the variable [example: 1].
    - VarDims: dimensions of the variable.
        - X: dimension along X axis [example: "west_east"].
        - Y: dimension along Y axis [example: "south_north"].
        - Time: dimension along T axis [example: "time"].
    - VarName: name of the variable.
        - FileName: the name of the source file [example: "ws.db.$yyyy$mm$dd$HH$MM.nc.gz"]
        - FilePath: the path of the source file [example: "$HOME/hmc-ws/data/dynamic/outcome/observation/ws/$yyyy/$mm/$dd/"]
        - FileVar: the name of the variable in the source file [example: "Rain"]

An example of the forcing gridded data structure is reported below.

.. code-block:: json

  {
  "Gridded"     : {
    "FileName"    : "hmc.forcing-grid.$yyyy$mm$dd$HH$MM.nc",
    "FilePath"    : "$HOME/hmc-ws/run/$RUN/data/forcing/$MODE/gridded/$yyyy/$mm/$dd/",
    "FileType"    : 2,
    "FileTimeRes" : 3600,
    "FileVars"    : {
      "OBS"         : {
        "VarResolution"   : 3600,
        "VarArrival"      : {"Day": 0, "Hour": null},
        "VarOp"           : {"Merging": true, "Splitting": false},
        "VarStep"         : 1,
        "VarDims"         : {"X": "west_east", "Y": "south_north"},
        "VarName"         : {
          "Rain"            : {
            "FileName"          : "ws.db.$yyyy$mm$dd$HH$MM.nc.gz",
            "FilePath"          : "$HOME/hmc-ws/data/dynamic/outcome/observation/ws/$yyyy/$mm/$dd/",
            "FileVar"           : "Rain"
                            },
          "AirTemperature"  : {
            "FileName"          : "ws.db.$yyyy$mm$dd$HH$MM.nc.gz",
            "FilePath"          : "$HOME/hmc-ws/data/dynamic/outcome/observation/ws/$yyyy/$mm/$dd/",
            "FileVar"           : "AirTemperature"
                            },
                          },
                    },

      "FOR"	      : {
        "VarResolution"   : 3600,
        "VarArrival"     	: {"Day": 1, "Hour": ["00"]},
        "VarOp"           : {"Merging": false, "Splitting": true},
        "VarStep"         : 72,
        "VarDims"         : {"X": "west_east", "Y": "south_north", "time" :"time"},
        "VarName"         : {
          "Rain"				    : {
            "FileName"          : "nwp.lami.$yyyy$mm$dd0000.nc.gz",
            "FilePath"          : "$HOME/hmc-ws/data/dynamic/outcome/nwp/lami-i7/$yyyy/$mm/$dd/$RFarm_ID/",
            "FileVar"           : "Rain"
                            },
          "AirTemperature"	: {
            "FileName"          : "nwp.lami.$yyyy$mm$dd0000.nc.gz",
            "FilePath"          : "$HOME/hmc-ws/data/dynamic/outcome/nwp/lami-i7/$yyyy/$mm/$dd/",
            "FileVar"           : "AirTemperature"
                            },
          "Wind"				    : {
            "FileName"          : "nwp.lami.$yyyy$mm$dd0000.nc.gz",
            "FilePath"          : "$HOME/hmc-ws/data/dynamic/outcome/nwp/lami-i7/$yyyy/$mm/$dd/",
            "FileVar"           : "Wind"
                            },
                    },
                     
                  },
              },
  }

In the gridded forcing section, the following variables are mandatory:
    - Rain [mm]
    - Air Temperature [C]
    - Wind Speed [m/s]
    - Relative Humidity [%]
    - Incoming Radiation [W/m^2]
Other variables are optional:
    - Air Pressure [kPa]
    - Albedo [0, 1]
    - Leaf Area Index [0, 8]

* Point

The forcing point files are in ASCII format; the forcing data, as seen in the gridded section, are divided in two 
different types of variables:

    - OBS: to define the observed dataset (if needed).
    - FOR: to define the forecast dataset (if needed).

Each variable, in OBS and FOR section, is defined by a list of attributes in order to correctly parser the 
information; the attributes available are reported below:

    - VarResolution: resolution time of the variable in seconds [example: 3600].
    - VarArrival: arrival time of the variable.
        - Day: to define the variable arrival day [example: 0].
        - Hour: to define the variable arrival hour [example: null].
    - VarOp: ancillary defined operations of the variable.
        - Merging: to merge variable from different sources in a common dataset [example: null].
        - Splitting: to split variable in different time steps [example: false].
    - VarStep: step of the variable [example: 1].
    - VarDims: dimensions of the variable.
        - Time: dimension along T axis [example: "time"].
    - VarName: name of the variable.
        - FileName: the name of the source file [example: "rs.db.$yyyy$mm$dd$HH$MM.txt"]
        - FilePath: the path of the source file [example: "$HOME/hmc-ws/data/dynamic/outcome/observation/rs/$yyyy/$mm/$dd/"]
        - FileVar: the name of the variable in the source file [example: "Discharge"]

An example of the forcing point data structure is reported below.

.. code-block:: json

  {
  "Point"       : {
    "FileName"    : "hmc.$VAR.$yyyy$mm$dd$HH$MM.txt",
    "FilePath"	  : "$HOME/hmc-ws/run/$RUN/data/forcing/point/$yyyy/$mm/$dd/",
    "FileType"	  : 1,		
    "FileTimeRes"	: 3600, 	
    "FileVars"	  : {
      "OBS"       	: {
        "VarResolution"   : 3600,
        "VarArrival"      : {"Day": 0, "Hour": null},
        "VarOp"           : {"Merging": null, "Splitting": null},
        "VarStep"         : 1,
        "VarDims"         : {"T": "time"},
        "VarName"         : {
          "Discharge"			  : {
            "FileName"          : "rs.db.$yyyy$mm$dd$HH$MM.txt",
            "FilePath"          : "$HOME/hmc-ws/data/dynamic/outcome/observation/rs/$yyyy/$mm/$dd/",
            "FileVar"		        : "discharge"
                            },
          "DamV"				    : {
            "FileName"          : "damv.db.$yyyy$mm$dd$HH$MM.txt",
            "FilePath"          : "$HOME/hmc-ws/data/dynamic/outcome/observation/dp/$yyyy/$mm/$dd/",
            "FileVar"           : "damv"
                            },
          "DamL"				    : {
            "FileName"          : "daml.db.$yyyy$mm$dd$HH$MM.txt",
            "FilePath"          : "$HOME/hmc-ws/data/dynamic/outcome/observation/dp/$yyyy/$mm/$dd/",
            "FileVar"		        : "daml"
                            }
                          }
                    },  
        "FOR" 	    : {}
                }
  }

In the point forcing section, all variables are optional:
    - Discharge [m^3/s]
    - Dam Volume [m^3]
    - Dam Level [m]

* Time Series

The forcing time-series files are in ASCII format; the forcing data, as seen in the gridded section, are divided in two 
different types of variables:

    - OBS: to define the observed dataset (if needed).
    - FOR: to define the forecast dataset (if needed).

Each variable, in OBS and FOR section, is defined by a list of attributes in order to correctly parser the 
information; the attributes available are reported below:

    - VarResolution: resolution time of the variable in seconds [example: 3600].
    - VarArrival: arrival time of the variable.
        - Day: to define the variable arrival day [example: 0].
        - Hour: to define the variable arrival hour [example: null].
    - VarOp: ancillary defined operations of the variable.
        - Merging: to merge variable from different sources in a common dataset [example: null].
        - Splitting: to split variable in different time steps [example: null].
    - VarStep: step of the variable [example: null].
    - VarDims: dimensions of the variable.
        - Time: dimension along T axis [example: "time"].
    - VarName: name of the variable.
        - FileName: the name of the source file [example: "hnc.forcing-ts.plant_$NAME_PLANT.txt"]
        - FilePath: the path of the source file [example: "$HOME/hmc-ws/data/dynamic/outcome/observation/turbinate/$yyyy/$mm/$dd/"]
        - FileVar: the name of the variable in the source file [example: "DamQ"]

An example of the forcing time-series data structure is reported below.

.. code-block:: json

  {
  "TimeSeries"  : {
    "FileName"    : "hmc.forcing-ts.plant_$NAME_PLANT.txt",
    "FilePath"	  : "$HOME/hmc-ws/run/$RUN/data/forcing/timeseries/",
    "FileType"	  : 1,		
    "FileTimeRes" : 3600, 	
    "FileVars"	  : {
      "OBS" 	      : {
        "VarResolution"   : 3600,
        "VarArrival"      : {"Day": 0, "Hour": null},
        "VarOp"           : {"Merging": null, "Splitting": null},
        "VarStep"         : null,
        "VarDims"         : {"T": "time"},
        "VarName"         : {
          "DamQ"				    : {
            "FileName"          : "hmc.forcing-ts.plant_$NAME_PLANT.txt",
            "FilePath"          : "$HOME/hmc-ws/data/dynamic/outcome/observation/turbinate/$yyyy/$mm/$dd/",
            "FileVar"		        : ""
                            },
            "IntakeQ"			  : {
              "FileName"        : "hmc.forcing-ts.plant_$NAME_PLANT.txt",
              "FilePath"        : "$HOME/hmc-ws/data/dynamic/outcome/observation/turbinate/$yyyy/$mm/$dd/",
              "FileVar"		      : ""
                            }
                          }
                    },
        "FOR" 	  	: {}
                  }
                } 
  }

In the time-series forcing section, all variables are optional:
    - Dam Discharge [m^3/s]
    - Intake Discharge [m^3/s]

Data Updating
.............

* Gridded

        !------------------------------------------------------------------------------------------
        ! Updating data (optional):                                                              
        !   a2dVarSnowCAL       : snow cover area [-2,3] 
        !   a2dVarSnowQAL       : snow cover quality [0,1] 
        !   a2dVarSnowMaskL     : snow mask [0,1] 
        !   
        !   a2dVarSMStarL       : soil moisture value [0, 1]
        !   a2dVarSMGainL       : soil moisture gain [0, 1]
        !   a2dVarSnowHeightF   : snow height [cm]                                                    
        !   a2dVarSnowKernelF   : snow kernel [0,1]  
        !------------------------------------------------------------------------------------------


Data Outcome
............

* Gridded

The outcome gridded files are in netCDF format; the outcome data are defined using the ARCHIVE key word. This 
definition is used to specify and manage the results of the model.

Each variable, as seen in previous sections, is defined by a list of attributes in order to correctly parser the 
information; the attributes available are reported below:

    - VarResolution: resolution time of the variable in seconds [example: 3600].
    - VarArrival: arrival time of the variable.
        - Day: to define the variable arrival day [example: 0].
        - Hour: to define the variable arrival hour [example: null].
    - VarOp: ancillary defined operations of the variable.
        - Merging: to merge variable from different sources in a common dataset [example: null].
        - Splitting: to split variable in different time steps [example: null].
    - VarStep: step of the variable [example: 1].
    - VarDims: dimensions of the variable.
        - X: dimension along X axis [example: "west_east"].
        - Y: dimension along Y axis [example: "south_north"].
    - VarName: name of the variable.
        - FileName: the name of the source file [example: "hmc.output-grid.$yyyy$mm$dd$HH$MM.nc.gz"]
        - FilePath: the path of the source file [example: "$HOME/hmc-ws/run/$RUN/data/outcome/$MODE/gridded/$yyyy/$mm/$dd/"]
        - FileVar: the name of the variable in the source file [example: "Discharge"]

An example of the outcome gridded data structure is reported below.

.. code-block:: json

  {
  "Gridded"	    : {
    "FileName"    : "hmc.output-grid.$yyyy$mm$dd$HH$MM.nc.gz",	
    "FilePath"	  : "$HOME/hmc-ws/run/$RUN/data/outcome/$MODE/gridded/$yyyy/$mm/$dd/",
    "FileType"	  : 2,
    "FileTimeRes"	: 3600, 
    "FileVars"	  : {
      "ARCHIVE"	    : {
        "VarResolution"   : 3600,
        "VarArrival"      : {"Day": 0, "Hour": null},
        "VarOp"           : {"Merging": null, "Splitting": null},
        "VarStep"         : 1,
        "VarDims"         : {"X": "west_east", "Y": "south_north"},
        "VarName"         : {
          "ALL"				      : {
            "FileName"          : "hmc.output-grid.$yyyy$mm$dd$HH$MM.nc.gz",
            "FilePath"          : "$HOME/hmc-ws/data/archive/$RUN/$yyyy/$mm/$dd/$HH/outcome/gridded/$MODE/",
            "FileVar"           : "ALL"
                            }
                          }
                    }
                  }
                } 
  }

In the gridded outcome files, the default configuration of outcome variables are reported below:
    - Discharge: Discharge [m^3/s]
    - Daily Accumulated Evapotranspiration: ETCum [mm]
    - Sensible Heat: H [W/m^2]
    - Latent Heat: LE [W/m^2]
    - Land Surface Temperature: LST [K]
    - Soil Moisture: SM [%]
    - Total Soil Capacity: VTot [mm]

If the snow part is activated, the following variables are added in the outcome files:
    - Snow Water Equivalent: SWE [mm]
    - Snow Melting: MeltingS [mm]
    - Snow Density: RhoS [kg/m^3]
    - Snowfall: Snowfall [mm]
    - Snow Albedo: AlbedoS [-]
    - Snow Age: AgeS [steps]
    - Daily Accumulated Snow Melting: MeltingSDayCum [mm]

* Point

The outcome point files are in ASCII format; the outcome data are defined using the ARCHIVE key word. This 
definition is used to specify and manage the results of the model.

Each variable, as seen in previous sections, is defined by a list of attributes in order to correctly parser the 
information; the attributes available are reported below:

    - VarResolution: resolution time of the variable in seconds [example: 3600].
    - VarArrival: arrival time of the variable.
        - Day: to define the variable arrival day [example: 0].
        - Hour: to define the variable arrival hour [example: null].
    - VarOp: ancillary defined operations of the variable.
        - Merging: to merge variable from different sources in a common dataset [example: null].
        - Splitting: to split variable in different time steps [example: null].
    - VarStep: step of the variable [example: 1].
    - VarDims: dimensions of the variable.
        - T: dimension along t axis [example: "time"].
    - VarName: name of the variable.
        - FileName: the name of the source file [example: "hmc.$VAR.$yyyy$mm$dd$HH$MM.txt"]
        - FilePath: the path of the source file [example: "$HOME/hmc-ws/run/$RUN/data/outcome/$MODE/point/$yyyy/$mm/$dd/"]
        - FileVar: the name of the variable in the source file [example: "DamV"]

An example of the outcome point data structure is reported below.

.. code-block:: json

  {
  "Point"       : {
    "FileName"    : "hmc.$VAR.$yyyy$mm$dd$HH$MM.txt",
    "FilePath"    : "$HOME/hmc-ws/run/$RUN/data/outcome/$MODE/point/$yyyy/$mm/$dd/",
    "FileType"    : 1,
    "FileTimeRes" : 3600,
    "FileVars"    : { 
      "ARCHIVE"     : {
        "VarResolution"   : 3600,
        "VarArrival"      : {"Day": 0, "Hour": null},
        "VarOp"           : {"Merging": null, "Splitting": null},
        "VarStep"         : 1,
        "VarDims"         : {"T": "time"},
        "VarName"         : {
          "Discharge"       : {
            "FileName"          : "hmc.discharge.$yyyy$mm$dd$HH$MM.txt",
            "FilePath"          : "$HOME/hmc-ws/data/archive/$RUN/$yyyy/$mm/$dd/$HH/outcome/point/$MODE/discharge/",
            "FileVar"           : "discharge"
                            },
          "DamV"            : {
            "FileName"          : "hmc.vdam.$yyyy$mm$dd$HH$MM.txt",
            "FilePath"          : "$HOME/hmc-ws/data/archive/$RUN/$yyyy/$mm/$dd/$HH/outcome/point/$MODE/dam_volume/",
            "FileVar"           : "vdam"
                            },
          "DamL"            : {
            "FileName"          : "hmc.ldam.$yyyy$mm$dd$HH$MM.txt",
            "FilePath"          : "$HOME/hmc-ws/data/archive/$RUN/$yyyy/$mm/$dd/$HH/outcome/point/$MODE/dam_level/",
            "FileVar"           : "ldam"
                            },
          "VarAnalysis"     : {
            "FileName"          : "hmc.var-analysis.$yyyy$mm$dd$HH$MM.txt",
            "FilePath"          : "$HOME/hmc-ws/data/archive/$RUN/$yyyy/$mm/$dd/$HH/outcome/point/$MODE/analysis/",
            "FileVar"           : "var-analysis"
                            }
                          }
                    }
                  }
                }  
  }

The default variables saved by the model in point format are reported:
    - Discharge: discharge [m^3/s]
In addition, if dams are included in the model configuration, the following variables are added:
    - Dam volume: vdam [m^3];
    - Dam Level: ldam [m].

Moreover, a point analysis file, to control and check the run of the model, is saved, 
when the FlagDebug > 0,  with information for some state variables:
    - Average variables: var-analysis.

In the analysis file, the following fields are saved on three columns [average, max, min]: 

  1. Rain [mm]
  2. AirTemperature [C]
  3. IncomingRadiation [W/m^2]
  4. Wind Speed [m/s]
  5. Relative Humidity [%]
  6. AirPressure [kPa]
  7. LAI [-]
  8. Albedo [0,1]
  9. Land Surface Temperature [K]
  10. Sensible Heat [W/m^2]
  11. Laten Heat [W/m^2]
  12. Evapotranspiration [mm]
  13. Intensity [mm]
  14. VTot [mm]
  15. Volume Retention [mm] 
  16. Volume Subflow [mm]
  17. Volume Losses [mm]
  18. Volume Exfiltration [mm]
  19. Flow Deep [mm]
  20. Watertable [mm]

* Time Series

The outcome time-series files are in ASCII format; the outcome data are defined using the ARCHIVE key word. This 
definition is used to specify and manage the results of the model.

Each variable, as seen in previous sections, is defined by a list of attributes in order to correctly parser the 
information; the attributes available are reported below:

    - VarResolution: resolution time of the variable in seconds [example: 3600].
    - VarArrival: arrival time of the variable.
        - Day: to define the variable arrival day [example: 0].
        - Hour: to define the variable arrival hour [example: null].
    - VarOp: ancillary defined operations of the variable.
        - Merging: to merge variable from different sources in a common dataset [example: null].
        - Splitting: to split variable in different time steps [example: null].
    - VarStep: step of the variable [example: 1].
    - VarDims: dimensions of the variable.
        - T: dimension along t axis [example: "time"].
    - VarName: name of the variable.
        - FileName: the name of the source file [example: "hmc.$VAR.txt"]
        - FilePath: the path of the source file [example: "$HOME/hmc-ws/run/$RUN/data/outcome/time-series/$MODE/"]
        - FileVar: the name of the variable in the source file [example: "hydrograph"]

An example of the outcome time-series data structure is reported below.

.. code-block:: json

  {
  "TimeSeries"  : {
    "FileName"    : "hmc.$VAR.txt",
    "FilePath"    : "$HOME/hmc-ws/run/$RUN/data/outcome/$MODE/timeseries/",
    "FileType"	  : 1,
    "FileTimeRes"	: 3600,
    "FileVars"	  : {
        "ARCHIVE"   : {
          "VarResolution"   : 3600,
          "VarArrival"      : {"Day": 0, "Hour": null},
          "VarOp"           : {"Merging": null, "Splitting": null},
          "VarStep"         : 1,
          "VarDims"         : {"T": "time"},
          "VarName"         : {
            "Discharge"       : {
              "FileName"          : "hmc.hydrograph.txt",
              "FilePath"          : "$HOME/hmc-ws/data/archive/$RUN/$yyyy/$mm/$dd/$HH/outcome/timeseries/$MODE/",
              "FileVar"           : "hydrograph"
                              },
            "DamV"            : {
              "FileName"          : "hmc.vdam.txt",
              "FilePath"          : "$HOME/hmc-ws/data/archive/$RUN/$yyyy/$mm/$dd/$HH/outcome/timeseries/$MODE/",
              "FileVar"           : "vdam"
                              },
            "DamL"				    : {
              "FileName"          : "hmc.ldam.txt",
              "FilePath"          : "$HOME/hmc-ws/data/archive/$RUN/$yyyy/$mm/$dd/$HH/outcome/timeseries/$MODE/",
              "FileVar"		        : "ldam"
                              },
            "VarAnalysis"		  : {
              "FileName"          : "hmc.var-analysis.txt",
              "FilePath"          : "$HOME/hmc-ws/data/archive/$RUN/$yyyy/$mm/$dd/$HH/outcome/timeseries/$MODE/",
              "FileVar"		        : "var-analysis"
                              }
                            }
                    }
                  }
                } 
  }

The default variables saved by the model in time-series format are reported:
    - Discharge: discharge [m^3/s]
In addition, if dams are included in the model configuration, the following variables are added:
    - Dam volume: vdam [m^3];
    - Dam Level: ldam [m].

Moreover, a time-series analysis file, to control and check the run of the model, is saved, 
when the FlagDebug > 0, with information for some state variables:
    - Average variables: var-analysis.
The time-series variables saved in the outcome file are the same as reported in the outcome point files.

Data State / Data Restart
.........................

* Gridded

The Hydrological Model Continuum saves, using the temporal resolution set in the namelist, the following gridded variables:

    - Total volume [mm]
    - Retention volume [mm] 
    - Hydro level [-]
    - Routing [-]
    - Flow deep and exfilration [-]
    - Water table level [m]
    - Land surface temperature [K]
    - Air temperature marked [K]
    - Air temperaure last 24 hours [K]
    - Water sources [m^3/s]

If the snow part is activated, in addition the variables related to the snow physics will be saved:

    - Snow water equivalent [mm] 
    - Snow density [kg/m^3]
    - Snow albedo [-]
    - Snow age [day]
    - Air temperature last day [C]
    - Air temperature last 5 day(s) [C]

* Point

The Hydrological Model Continuum saves, using the temporal resolution set in the namelist, the following point variables:
		
		- Dam(s)
			- matrix coordinates of dams [-]
			- codes of dams [-]
			- dams volume max [m^3]
			- dams volume [m^3]
		- Lake(s)				
      - matrix coordinates of lakes [-]
			- codes of lakes [-]
			- lakes volume min\ [m^3]
			- lakes volume [m^3]        

Model execution
***************

The Hydrological Model Continuum can be run in different configurations according with the use and
the applications for which it is designed for. It is possible to configure model using the hmc python3 package or in stand-alone version;
using the stand-alone version, the model can be easily integrated in different frameworks ensuring the dependencies
of zlib, hdf5 and netCDF4 libraries. Usually, the model is distributed with a configure file to compile the source 
codes in a generic Linux Debian/Ubuntu system and to select different configuration flags.
Generally, to properly build the model, the users have to follow the following steps:

  1. build the model dependencies compiling zlib, hdf5 and netCDF4 libraries;
  2. build the model codes against the libraries previouly installed

Wrapping mode
-------------

As said in the previous paragraph, the Hydrological Model Continuum can be configured using the hmc python3 package; it is the 
generic packege to use the model and in the previous sections all parameters and datasets are fully explained for avoiding 
mismatches and failures in setting parameters or preparing datasets.

The application for running the model is stored in the Apps folder in the main root of the package as reported in the 
following package tree:

::

    hmc-master
    ├── apps
    │   ├── **HMC_Model_Run_Manager.py**
    │   ├── configuration_run_app_1.json
    │   ├── configuration_run_app_2.json
    │   ├── configuration_data_app_1.json
    │   ├── configuration_data_app_2.json
    │   └── ...
    ├── bin
    ├── docs
    ├── hmc
    ├── AUTHORS.rst
    ├── CHANGELOG.rst
    ├── LICENSE.rst
    └── README.rst

As said at the beginning of this documentation, a generic execution of the model is performed using the following line in a terminal:

.. code-block:: bash

  >> python3 HMC_Model_RUN_Manager.py -settings_file configuration.json -time "yyyymmddHHMM"


Standalone mode
---------------

The Hydrological Model Continuum can be run in a stand-alone version too; the users have to be properly filled the namelist of the model
and using the command-line to launch the following instructions to set the libraries:

.. code-block:: bash
  
  >> export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/path_to_netcdf_folder/lib/
  >> ulimit -s unlimited

**EXECUTION TYPE 1:**
The executable of the model can ben launch using a list of seven parameters according with the following notation:

.. code-block:: bash

  >> ./HMC_Model_V2_DomainName.x [parameters: uc, uh, ct, cf, domain, cpi, rf, vmax, slopemax]  

An filled example of the previous command-line, is reported:

.. code-block:: bash

  >> ./HMC_Model_V2_DomainName.x 30 3 0.6 0.015 DomainName 0.3 500 1 70

**EXECUTION TYPE 2:**
It is possible to run the Hydrological Model Continuum using a command-line in which only the model namelist is passed:

.. code-block:: bash

  >> ./HMC_Model_V2_DomainName.x domainname.info.txt

This approach is generally preferred because the number of argument is fixed and never vary in different configuration 
and applications; in fact, all the changes in the model (e.g. flags, datasets, parameters) will be managed using the namelist file.

Debugging mode
--------------

The users could be interested in debugging codes to have a deeper knowledge of the Hydrological Model Continuum; usually, for
doing this task, the common advice is used a IDE (e.g, CodeBlock, VS Code, Apache Netbeans) in order to easily analyze codes and memory
usage. In this part, the configuration of a debug workspace in Apache NetBeans IDE will be presented.

First of all, the package for C, C++ and Fortran programming languages have to be installed in Apache NetBeans; to complete this
step, the users have to install the package related with C/C++ language. Particuarly, following these instructions:

  1) Tools --> Plugins --> Settings --> Tick "NetBeans 8.2 Plugin Portal" --> Close 

and Reboot the Apache NetBeans IDE.
Next step, users should create a New Project following these instructions: 

  2) File --> New Project --> Category :: Sample :: C/C++ --> Project :: Hello World Fortran Application --> Next --> Choose Name --> Close

After creating a folder project, users have to import all source code in the project folder; Using the left menu where the name of projects
are visible, right click on selected project:

  3) Source Files --> Add existing items ...

performing this action, a form to select all file will be opened. Finally, all source files will be available into source file folder
of the selected project. 
Next steps cover the configuration of the dependencies in the project. Particularly, the main task is linking the NetCDF library against
the project.
For configuring the NetCDF4 in Apache NetBeans IDE, the users have to add in:

  4) Project --> Properties --> Linker --> Libraries
     
     in /path_to_netcdf/ find the following files
     netcdff.a and netcdff.so 
     and note "double f" for fortran libraries

  5) Project --> Properties --> Linker --> Additional Options
     
      -I/path_to_netcdf/include/ 
      -L/path_to_netcdf/lib/ 
      -lnetcdff -lnetcdf   

  6) Project --> Properties --> Fortran Compiler --> Additional Options

      -I/path_to_netcdf/include/ 
      -L/path_to_netcdf/lib/ 
      -lnetcdff -lnetcdf  

  7) Project --> Properties --> Fortran Compiler --> Additional Options
  
      gfortran: -cpp -DLIB_NC
      ifort: -fpp -DLIB_NC  

  8) Project --> Properties --> Run --> Environment --> NewValue
  
      Name: LD_LIBRARY_PATH 
      Value: $LD_LIBRARY_PATH:/path_to_necdf/lib/

Once the NetCDF4 are linked, it will be possible to compile each source file using the F9 key.
After doing all these steps, the users have to set the debug command to run Hydrological Model Continuum 
using, for instance, a namelist file of a study case:  
  
  9) Debug --> Debug Command 
  	
  		"${OUTPUT_PATH}" domainname.info.txt

After setting the environment and all needed options for running the model, the users will are able to get a 
deeper information using the options to execute code in a debugging mode using breakpoints and all the features
available in **gdb** debugging library. 

Profiling Mode
--------------

Another option for the users is the profiling of the model using the **gprof** command. This tool provides a 
detailed postmortem analysis of program timing at the subprogram level, including how many times a subprogram was 
called, who called it, whom it called, and how much time was spent in the routine and by the routines it called.

To enable gprof profiling, the users have to compile and link the program with the -pg option; in the configure
program is a section for compiling the model in profiling model.

.. code-block:: bash

  >> ./HMC_Model_V2_DomainName.x domainname.info.txt

The simulation must complete normally for gprof to obtain meaningful timing information. At program termination, 
the file **gmon.out** is automatically written in the working directory. This file contains the profiling data 
that will be interpreted by gprof. 
To obtain a ascii file for all information, the following command have to be execute 
./$name_exec 30 3 0.6 0.015 marche 0.3 500 1 70 

.. code-block:: bash

  >> gprof HMC_Model_V2_DomainName.x gmon.out > hmc_model_analysis.txt

Alternatively, a python script to plot a scheme of model flow is provided in the hmc package:

.. code-block:: bash

  >> gprof HMC_Model_V2_DomainName.x | ./gprof2dot.py | dot -Tpng -o hmc_model_analysis.png


