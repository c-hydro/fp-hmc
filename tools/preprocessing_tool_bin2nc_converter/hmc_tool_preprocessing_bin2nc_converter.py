"""
HMC Conversion Tool - forcing bin2netcdf
__date__ = '20201214'
__version__ = '0.0.2'
__author__ =
        'Lorenzo Alfieri' (lorenzo.alfieri@cimafoundation.org',
        'Fabio Delogu' (fabio.delogu@cimafoundation.org',
        'Andrea Libertino (andrea.libertino@cimafoundation.org',
__library__ = 'hmc'
General command line:
### python3 bin_forcing_to_netcdf.py -settings_file "model.json"
Version(s):
20201203 (0.0.1) --> Beta release
20201214 (0.0.2) --> Various bug fixes
"""
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
import numpy as np
import logging, json, os, time, struct
from argparse import ArgumentParser
import pandas as pd
import rasterio as rio
import xarray as xr
from copy import deepcopy

# -------------------------------------------------------------------------------------
# Algorithm information
alg_name = 'HMC Conversion Tool - forcing bin2netcdf'
alg_version = '0.0.2'
alg_release = '2020-12-14'
# Algorithm parameter(s)
time_format = '%Y%m%d%H%M'
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Defined attributes look-up table
attributes_defined_lut = {
    'blocking_attrs': ['coordinates'],
    'encoding_attrs': {
        '_FillValue': ['_FillValue', 'fill_value'],
        'scale_factor': ['scale_factor', 'ScaleFactor']
    },
    'filtering_attrs': {
        'Valid_range': ['Valid_range', 'valid_range'],
        'Missing_value': ['Missing_value', 'missing_value']
    }
}

# -------------------------------------------------------------------------------------

def main():

    # -------------------------------------------------------------------------------------
    # Get algorithm settings
    alg_settings = get_args()

    # Set algorithm settings
    data_settings = read_file_json(alg_settings)

    # Set algorithm logging
    os.makedirs(data_settings['log']['logPath'], exist_ok=True)
    set_logging(logger_file=os.path.join(data_settings['log']['logPath'], data_settings['log']['logName']))

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Info algorithm
    logging.info(' ============================================================================ ')
    logging.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_release + ')')
    logging.info(' ==> START ... ')
    logging.info(' ')

    # Time algorithm information
    start_time = time.time()

    # -------------------------------------------------------------------------------------
    # Get algorithm time range
    logging.info(" ----> Compute data from " + data_settings['algorithm']['time']['time_start'] + " to " + data_settings['algorithm']['time']['time_end'])
    run_start = pd.Timestamp(data_settings['algorithm']['time']['time_start'])
    run_end = pd.Timestamp(data_settings['algorithm']['time']['time_end'])
    time_run_range = pd.date_range(start=run_start,end=run_end,freq=data_settings['algorithm']['time']['freq'])

    varIn = [i for i in data_settings['data']['variables'] if data_settings['data']['variables'][i]['compute']]

    logging.info(" ----> Available variables: " + ",".join(varIn))

    if data_settings['algorithm']['general']['meteogrid_dem_available']:
        logging.info(" ----> Meteogrid dem available, extract geographic reference information")
        dem = xr.open_rasterio(os.path.join(data_settings['grid']['meteogrid_dem_available']['meteogrid_dem_path'], data_settings['grid']['meteogrid_dem_available']['meteogrid_dem_file']))
        nrows = len(dem.y)
        ncols = len(dem.x)
        xll = dem.transform[2]
        yll = dem.transform[5]
        res = abs(dem.transform[0])
        geo_data_values = np.flipud(dem.values)
        meteogrid_dem_available = True

        geo_x_values = np.sort(dem.x.values)
        geo_y_values = np.sort(dem.y.values)
    else:
        logging.info(" ----> Meteogrid dem not available, load geographic reference information from config file")
        nrows = data_settings['grid']['meteogrid_dem_not_available']['nrows']
        ncols = data_settings['grid']['meteogrid_dem_not_available']['ncols']
        xll = data_settings['grid']['meteogrid_dem_not_available']['xll']
        yll = data_settings['grid']['meteogrid_dem_not_available']['yll']
        res =  data_settings['grid']['meteogrid_dem_not_available']['res']
        geo_data_values = -9999
        meteogrid_dem_available = False

        geo_x_values = np.arange(xll + res / 2, xll + res / 2 + res * ncols, res)
        geo_y_values = np.arange(yll + res / 2, yll + res / 2 + res * nrows, res)

    attributes_dict = {'ncols': ncols,
                       'nrows': nrows,
                       'nodata_value': -9999.0,
                       'xllcorner': xll,
                       'yllcorner': yll,
                       'cellsize': res}

    for timeNow in time_run_range:
        logging.info(' ----> Compute time step ' + timeNow.strftime("%Y-%m-%d %H:%M") + '...')
        inMaps = {}

        for var in varIn:
            logging.info(' ---> Extract variable: ' + var)
            file_time_step = os.path.join(data_settings['data']['variables'][var]['filePath'], data_settings['data']['variables'][var]['fileName'])
            for i in data_settings['template']:
                file_time_step = file_time_step.replace("{" + i + "}", timeNow.strftime(data_settings['template'][i]))
            if data_settings['algorithm']['general']['compressed_input_forcings']:
                os.system('gunzip ' + file_time_step + '.gz')
            inMaps[var] = read_var2d(file_time_step, nrows, ncols, file_format='i', scale_factor=data_settings['algorithm']['general']['scale_factor'])
            if data_settings['algorithm']['general']['compressed_input_forcings']:
                os.system('gzip ' + file_time_step)

        logging.info(' ---> Create variables dataset...')
        dset_data = create_dset(inMaps, geo_data_values, geo_x_values, geo_y_values, timeNow, global_attrs_dict=attributes_dict, meteogrid_dem_available=meteogrid_dem_available)

        file_out_time_step = os.path.join(data_settings['data']['output']['outPath'],'hmc.forcing-grid.' + timeNow.strftime('%Y%m%d%H%M') + '.nc')
        for i in data_settings['template']:
            file_out_time_step = file_out_time_step.replace("{" + i + "}", timeNow.strftime(data_settings['template'][i]))

        logging.info(' ---> Write output...')
        os.makedirs(os.path.dirname(file_out_time_step), exist_ok=True)
        write_dset(file_out_time_step, dset_data, dset_mode='w', dset_engine='h5netcdf', dset_compression_level=0, dset_format='NETCDF4',
               dim_key_time='time', fill_value=-9999.0)
        os.system('gzip -f ' + file_out_time_step)

    #Ending info
    logging.info(' ----> Compute time step ' + timeNow.strftime("%Y-%m-%d %H:%M") + '... DONE')
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Info algorithm
    time_elapsed = round(time.time() - start_time, 1)

    logging.info(' ')
    logging.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_release + ')')
    logging.info(' ==> TIME ELAPSED: ' + str(time_elapsed) + ' seconds')
    logging.info(' ==> ... END')
    logging.info(' ==> Bye, Bye')
    logging.info(' ============================================================================ ')
    # -------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# Method to read 2d variable in binary format (saved as 1d integer array)
def read_var2d(file_name, rows, cols, file_format='i', scale_factor=10):

    # Open file handle
    file_handle = open(file_name, 'rb')

    # Values shape (1d)
    file_n = rows * cols
    # Values format
    data_format = file_format * file_n
    # Open and read binary file
    file_stream = file_handle.read(-1)
    array_data = struct.unpack(data_format, file_stream)

    # Reshape binary file in Fortran order and scale Data (float32)
    file_data = np.reshape(array_data, (rows, cols), order='F')
    file_data = np.float32(file_data / scale_factor)

    # Close file handle
    file_handle.close()

    return file_data
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to create datasets
def create_dset(var_data_dict, geo_data_values, geo_x_values, geo_y_values, time_data_values,
                var_attrs_dict=None,
                geo_data_attrs_dict=None, geo_data_name='terrain',
                geo_x_attrs_dict=None, geo_x_name='longitude',
                geo_y_attrs_dict=None, geo_y_name='latitude',
                geo_data_1d=False,
                global_attrs_dict=None,
                coord_name_x='longitude', coord_name_y='latitude', coord_name_time='time',
                dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                dims_order_2d=None, dims_order_3d=None,
                missing_value_default=-9999.0, fill_value_default=-9999.0, meteogrid_dem_available=False):

    geo_x_values_tmp = geo_x_values
    geo_y_values_tmp = geo_y_values
    if geo_data_1d:
        if (geo_x_values.shape.__len__() == 2) and (geo_y_values.shape.__len__() == 2):
            geo_x_values_tmp = geo_x_values[0, :]
            geo_y_values_tmp = geo_y_values[:, 0]
    else:
        if (geo_x_values.shape.__len__() == 1) and (geo_y_values.shape.__len__() == 1):
            geo_x_values_tmp, geo_y_values_tmp = np.meshgrid(geo_x_values, geo_y_values)

    if dims_order_2d is None:
        dims_order_2d = [dim_name_y, dim_name_x]
    if dims_order_3d is None:
        dims_order_3d = [dim_name_y, dim_name_x, dim_name_time]

    if not isinstance(time_data_values, list):
        time_data_values = [time_data_values]

    if var_attrs_dict is None:
        var_attrs_dict = {}
        for var_name_step in var_data_dict.keys():
            var_attrs_dict[var_name_step] = None

    var_dset = xr.Dataset(coords={coord_name_time: ([dim_name_time], time_data_values)})
    if global_attrs_dict is not None:
        for global_attrs_name, global_attrs_value in global_attrs_dict.items():
            var_dset.attrs[global_attrs_name] = global_attrs_value
        if 'nodata_value' not in list(global_attrs_dict.keys()):
            global_attrs_dict['nodata_value'] = -9999.0
    var_dset.coords[coord_name_time] = var_dset.coords[coord_name_time].astype('datetime64[ns]')

    if meteogrid_dem_available==True:
        var_da_terrain = xr.DataArray(np.flipud(geo_data_values),  name=geo_data_name,
                                      dims=dims_order_2d,
                                      coords={coord_name_x: ([dim_name_y, dim_name_x], geo_x_values_tmp),
                                              coord_name_y: ([dim_name_y, dim_name_x], geo_y_values_tmp)})
        var_dset[geo_data_name] = var_da_terrain

    if geo_data_attrs_dict is not None:
        geo_attrs_dict_info, geo_attrs_dict_encoded = select_attrs(geo_data_attrs_dict)
        if geo_attrs_dict_info is not None:
            var_dset[geo_data_name].attrs = geo_attrs_dict_info
        if geo_attrs_dict_encoded is not None:
            var_dset[geo_data_name].encoding = geo_attrs_dict_encoded

    if geo_x_name in list(var_dset.coords):
        if geo_x_attrs_dict is not None:
            geo_attrs_dict_info, geo_attrs_dict_encoded = select_attrs(geo_x_attrs_dict)
            if geo_attrs_dict_info is not None:
                var_dset[geo_x_name].attrs = geo_attrs_dict_info
            if geo_attrs_dict_encoded is not None:
                var_dset[geo_x_name].encoding = geo_attrs_dict_encoded

    if geo_y_name in list(var_dset.coords):
        if geo_y_attrs_dict is not None:
            geo_attrs_dict_info, geo_attrs_dict_encoded = select_attrs(geo_y_attrs_dict)
            if geo_attrs_dict_info is not None:
                var_dset[geo_y_name].attrs = geo_attrs_dict_info
            if geo_attrs_dict_encoded is not None:
                var_dset[geo_y_name].encoding = geo_attrs_dict_encoded

    for (var_name_step, var_data_step), var_attrs_step in zip(var_data_dict.items(), var_attrs_dict.values()):

        if var_data_step.shape.__len__() == 2:
            var_da_data = xr.DataArray(np.flipud(var_data_step), name=var_name_step,
                                       dims=dims_order_2d,
                                       coords={coord_name_x: ([dim_name_y, dim_name_x], geo_x_values_tmp),
                                               coord_name_y: ([dim_name_y, dim_name_x], geo_y_values_tmp)})      #QUA HO MODIFICATO, verificare che non flippi
        elif var_data_step.shape.__len__() == 3:
            var_da_data = xr.DataArray(np.flipud(var_data_step), name=var_name_step,
                                       dims=dims_order_3d,
                                       coords={coord_name_time: ([dim_name_time], time_data),                    # QUESTO time_data non era già definito nella funzione che mi hai mandato
                                               coord_name_x: ([dim_name_y, dim_name_x], geo_x_values_tmp),
                                               coord_name_y: ([dim_name_y, dim_name_x], np.flipud(geo_y_values_tmp))})
        else:
            raise NotImplemented

        if var_attrs_step is not None:

            missing_value = None
            for attrs_name in attributes_defined_lut['filtering_attrs']['Missing_value']:
                if attrs_name in list(var_attrs_step.keys()):
                    missing_value = var_attrs_step[attrs_name]
            if missing_value is None:
                missing_value = missing_value_default
            for attrs_name in attributes_defined_lut['filtering_attrs']['Valid_range']:
                if attrs_name in list(var_attrs_step.keys()):
                    valid_range = var_attrs_step[attrs_name]
                    var_da_data = clip_data(var_da_data, valid_range, missing_value=missing_value)

            fill_value = None
            for attrs_name in attributes_defined_lut['encoding_attrs']['_FillValue']:
                if attrs_name in list(var_attrs_step.keys()):
                    fill_value = var_attrs_step[attrs_name]
            if fill_value is None:
                fill_value = fill_value_default
            if meteogrid_dem_available==True:
                var_da_data = var_da_data.where(var_da_terrain > global_attrs_dict['nodata_value'], other=fill_value)

        var_dset[var_name_step] = var_da_data

        if var_attrs_step is not None:
            var_attrs_step_info, var_attrs_step_encoded = select_attrs(var_attrs_step)
        else:
            var_attrs_step_info = None
            var_attrs_step_encoded = None

        if var_attrs_step_info is not None:
            var_dset[var_name_step].attrs = var_attrs_step_info
        if var_attrs_step_encoded is not None:
            var_dset[var_name_step].encoding = var_attrs_step_encoded

    return var_dset
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to select attributes
def select_attrs(attrs_var_raw):

    if attrs_var_raw is not None:

        attrs_var_tmp = deepcopy(attrs_var_raw)
        for attrs_def_key, attrs_def_items in attributes_defined_lut.items():

            if isinstance(attrs_def_items, dict):
                for field_key, field_items in attrs_def_items.items():
                    if isinstance(field_items, list):
                        for field_name in field_items:
                            if field_name in attrs_var_tmp:
                                if field_name != field_key:
                                    field_value = attrs_var_tmp[field_name]
                                    attrs_var_tmp.pop(field_name, None)
                                    attrs_var_tmp[field_key] = field_value
                    else:
                        logging.error(' ===> Type variable not allowed')
                        raise NotImplemented('Attributes values type not implemented yet')

            elif isinstance(attrs_def_items, list):
                pass
            else:
                logging.error(' ===> Type variable not allowed')
                raise NotImplemented('Attributes values type not implemented yet')

        blocked_attrs = attributes_defined_lut['blocking_attrs']
        encoded_attrs = list(attributes_defined_lut['encoding_attrs'].keys())

        attrs_var_info = {}
        attrs_var_encoded = {}
        for attrs_var_key, attrs_var_value in attrs_var_tmp.items():

            if attrs_var_value is not None:
                if isinstance(attrs_var_value, list):
                    var_string = [str(value) for value in attrs_var_value]
                    attrs_var_value = ','.join(var_string)
                if isinstance(attrs_var_value, dict):
                    var_string = json.dumps(attrs_var_value)
                    attrs_var_value = var_string

                if attrs_var_key in encoded_attrs:
                    attrs_var_encoded[attrs_var_key] = attrs_var_value
                elif attrs_var_key in blocked_attrs:
                    pass
                else:
                    attrs_var_info[attrs_var_key] = attrs_var_value
    else:
        attrs_var_info = None
        attrs_var_encoded = None

    return attrs_var_info, attrs_var_encoded
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to clip data 2D/3D using a min/max threshold(s) and assign a missing value
def clip_data(map, valid_range=None, missing_value=None):

    # Set variable valid range
    if valid_range is None:
        valid_range = [None, None]

    if valid_range is not None:
        if valid_range[0] is not None:
            valid_range_min = float(valid_range[0])
        else:
            valid_range_min = None
        if valid_range[1] is not None:
            valid_range_max = float(valid_range[1])
        else:
            valid_range_max = None
        # Set variable missing value
        if missing_value is None:
            missing_value_min = valid_range_min
            missing_value_max = valid_range_max
        else:
            missing_value_min = missing_value
            missing_value_max = missing_value

        # Apply min and max condition(s)
        if valid_range_min is not None:
            map = map.where(map >= valid_range_min, missing_value_min)
        if valid_range_max is not None:
            map = map.where(map <= valid_range_max, missing_value_max)
        return map
    else:
        return map
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to write dataset
def write_dset(file_name,
               dset_data, dset_mode='w', dset_engine='h5netcdf', dset_compression_level=0, dset_format='NETCDF4',
               dim_key_time='time', fill_value=-9999.0):

    dset_encoding = {}
    for var_name in dset_data.data_vars:

        if isinstance(var_name, bytes):
            var_name_upd = var_name.decode("utf-8")
            dset_data = var_name.rename({var_name: var_name_upd})
            var_name = var_name_upd

        var_attrs_encoding = dset_data[var_name].encoding

        if '_FillValue' not in list(var_attrs_encoding.keys()):
            var_attrs_encoding['_FillValue'] = fill_value
        if dset_compression_level > 0:
            if 'zlib' not in list(var_attrs_encoding.keys()):
                var_attrs_encoding['zlib'] = True
            if 'complevel' not in list(var_attrs_encoding.keys()):
                var_attrs_encoding['complevel'] = dset_compression_level

        dset_encoding[var_name] = var_attrs_encoding

    if dim_key_time in list(dset_data.coords):
        dset_encoding[dim_key_time] = {'calendar': 'gregorian'}

    dset_data.to_netcdf(path=file_name, format=dset_format, mode=dset_mode, engine=dset_engine,
                        encoding=dset_encoding)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get script argument(s)
def get_args():
    parser_handle = ArgumentParser()
    parser_handle.add_argument('-settings_file', action="store", dest="alg_settings")
    parser_values = parser_handle.parse_args()

    if parser_values.alg_settings:
        alg_settings = parser_values.alg_settings
    else:
        alg_settings = 'configuration.json'

    return alg_settings
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to read file json
def read_file_json(file_name):
    env_ws = {}
    for env_item, env_value in os.environ.items():
        env_ws[env_item] = env_value

    with open(file_name, "r") as file_handle:
        json_block = []
        for file_row in file_handle:

            for env_key, env_value in env_ws.items():
                env_tag = '$' + env_key
                if env_tag in file_row:
                    env_value = env_value.strip("'\\'")
                    file_row = file_row.replace(env_tag, env_value)
                    file_row = file_row.replace('//', '/')

            # Add the line to our JSON block
            json_block.append(file_row)

            # Check whether we closed our JSON block
            if file_row.startswith('}'):
                # Do something with the JSON dictionary
                json_dict = json.loads(''.join(json_block))
                # Start a new block
                json_block = []

    return json_dict
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to set logging information
def set_logging(logger_file='log.txt', logger_format=None):
    if logger_format is None:
        logger_format = '%(asctime)s %(name)-12s %(levelname)-8s ' \
                        '%(filename)s:[%(lineno)-6s - %(funcName)20s()] %(message)s'

    # Remove old logging file
    if os.path.exists(logger_file):
        os.remove(logger_file)

    # Set level of root debugger
    logging.root.setLevel(logging.INFO)

    # Open logging basic configuration
    logging.basicConfig(level=logging.INFO, format=logger_format, filename=logger_file, filemode='w')

    # Set logger handle
    logger_handle_1 = logging.FileHandler(logger_file, 'w')
    logger_handle_2 = logging.StreamHandler()
    # Set logger level
    logger_handle_1.setLevel(logging.INFO)
    logger_handle_2.setLevel(logging.INFO)
    # Set logger formatter
    logger_formatter = logging.Formatter(logger_format)
    logger_handle_1.setFormatter(logger_formatter)
    logger_handle_2.setFormatter(logger_formatter)

    # Add handle to logging
    logging.getLogger('').addHandler(logger_handle_1)
    logging.getLogger('').addHandler(logger_handle_2)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to fill path names
def fillScriptSettings(data_settings, domain):
    path_settings = {}

    for k, d in data_settings['path'].items():
        for k1, strValue in d.items():
            if isinstance(strValue, str):
                if '{' in strValue:
                    strValue = strValue.replace('{domain}', domain)
            path_settings[k1] = strValue

    return path_settings
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Call script from external library

if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------------