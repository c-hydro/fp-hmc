"""
Library Features:

Name:          lib_default_variables
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

# -------------------------------------------------------------------------------------
# Variables default information
variable_default_fields = {
    "Rain": {
        "var_file_name": "hmc.forcing-grid.{dset_datetime_forcing_obs}.nc.gz",
        "var_file_folder": None,
        "var_file_dset": "Rain",
        "var_file_format": "netcdf",
        "var_file_limits": [0, None],
        "var_file_units": "mm"
    },
    "AirTemperature": {
        "var_file_name": "hmc.forcing-grid.{dset_datetime_forcing_obs}.nc.gz",
        "var_file_folder": None,
        "var_file_dset": "Air_Temperature",
        "var_file_format": "netcdf",
        "var_file_limits": [-20, 40],
        "var_file_units": "C"
    },
    "Wind": {
        "var_file_name": "hmc.forcing-grid.{dset_datetime_forcing_obs}.nc.gz",
        "var_file_folder": None,
        "var_file_dset": "Wind",
        "var_file_format": "netcdf",
        "var_file_limits": [0, 10],
        "var_file_units": "m/s"
    },
    "RelHumidity": {
        "var_file_name": "hmc.forcing-grid.{dset_datetime_forcing_obs}.nc.gz",
        "var_file_folder": None,
        "var_file_dset": "Relative_Humidity",
        "var_file_format": "netcdf",
        "var_file_limits": [0, 100],
        "var_file_units": "%"
    },
    "IncRadiation": {
        "var_file_name": "hmc.forcing-grid.{dset_datetime_forcing_obs}.nc.gz",
        "var_file_folder": None,
        "var_file_dset": "Incoming_Radiation",
        "var_file_format": "netcdf",
        "var_file_limits": [-100, 1200],
        "var_file_units": "W^2/m"
    },
    "AirPressure": {
        "var_file_name": "hmc.forcing-grid.{dset_datetime_forcing_obs}.nc.gz",
        "var_file_folder": None,
        "var_file_dset": "AirPressure",
        "var_file_format": "netcdf",
        "var_file_limits": [1010.0, 1020.0],
        "var_file_units": "hPa"
    }
}
# -------------------------------------------------------------------------------------
