"""
IGAD Operational Chain - Mosaic outputs
__date__ = '20210412'
__version__ = '1.0.0'
__author__ =
        'Andrea Libertino (andrea.libertino@cimafoundation.org',
__library__ = 'igad'
General command line:
### python igad_mosaic_output.py -settings_file igad_mosaic_output.json -time "YYYY-MM-DD HH:MM"
Version(s):
20210412 (1.0.0) --> Beta release
"""
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Complete library
import logging
from os.path import join
import datetime as dt
from argparse import ArgumentParser
import json
import time
import pandas as pd
import xarray as xr
import numpy as np
import rasterio as rio
import os
import sys

# -------------------------------------------------------------------------------------
# Script Main
def main():
    # -------------------------------------------------------------------------------------
    # Version and algorithm information
    alg_name = 'IGAD Operational Chain - Mosaic outputs '
    alg_version = '1.0.0'
    alg_release = '2021-04-12'
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Get algorithm settings
    alg_settings, alg_time = get_args()

    # Set algorithm settings
    data_settings = read_file_json(alg_settings)

    # Set algorithm logging
    os.makedirs(data_settings['data']['log']['folder'], exist_ok=True)
    set_logging(logger_file=join(data_settings['data']['log']['folder'], data_settings['data']['log']['filename']))
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Info algorithm
    logging.info(' ============================================================================ ')
    logging.info(' ==> START ... ')
    logging.info(' ')

    # Time algorithm information
    start_time = time.time()
    # -------------------------------------------------------------------------------------
    # Extract bounding box
    logging.info(" --> Set up geographical references...")
    grid_settings = data_settings['data']['outcome']['output_grid']

    transform = rio.transform.Affine.translation(grid_settings['xmin'], grid_settings['ymin']) * rio.transform.Affine.scale(grid_settings['res'], grid_settings['res'])

    lat_out = np.arange(grid_settings['ymin'] + (grid_settings['res']/2), grid_settings['ymax'] + (grid_settings['res']/2), grid_settings['res'])
    lon_out = np.arange(grid_settings['xmin'] + (grid_settings['res']/2), grid_settings['xmax'] + (grid_settings['res']/2), grid_settings['res'])

    sm_map = (np.ones([len(lat_out), len(lon_out)])*-9999).astype(np.float32)
    et_map = (np.ones([len(lat_out), len(lon_out)])*-9999).astype(np.float32)
    logging.info(" --> Set up geographical references... DONE")

    # -------------------------------------------------------------------------------------
    # Set up algorithm time
    logging.info(" --> Set up time reference")
    date_run = dt.datetime.strptime(alg_time, "%Y-%m-%d %H:%M")
    date_ref = date_run + pd.Timedelta(data_settings['data']['input']['reference_day'])
    time_ref = dt.datetime(date_ref.year, date_ref.month, date_ref.day, data_settings['data']['input']['reference_hour'])

    # Fill template list
    template_now = data_settings['algorithm']['template']
    for key in template_now.keys():
        template_now[key] = time_ref.strftime(template_now[key])

    file_out_sm = os.path.join(data_settings['data']['outcome']['folder'],data_settings['data']['outcome']['filename_sm']).format(**template_now)
    file_out_et = os.path.join(data_settings['data']['outcome']['folder'], data_settings['data']['outcome']['filename_et']).format(**template_now)
    os.makedirs(os.path.dirname(file_out_sm), exist_ok=True)
    logging.info(" --> Set up time reference... DONE")
    
    logging.info(" --> Set up domain list")
    list_domain = data_settings['data']['input']['domains'].split(",")

    # -------------------------------------------------------------------------------------
    # Loop through domains
    not_available_run = 0

    for domain in list_domain:
        logging.info(" ---> Compute domain :" + domain)

        template_now['domain'] = domain
        file_in = os.path.join(data_settings['data']['input']['folder'],data_settings['data']['input']['filename']).format(**template_now)
        dem_in = xr.open_rasterio(data_settings['data']['input']['dem'].format(**template_now))

        try:
            os.system('gunzip -fk ' + file_in + ".gz")
            data = xr.open_dataset(file_in)
        except:
            logging.warning(' --> WARNING! output for domain ' + domain + ' is missing!')
            not_available_run = not_available_run + 1
            continue

        lat_in= np.flipud(dem_in['y'].values)
        lon_in= dem_in['x'].values
        
        et_in = xr.DataArray(np.where(data['SM']<0, np.nan, data['ETCum']), dims=['lat', 'lon'], coords={'lat': lat_in, 'lon': lon_in})
        sm_in = xr.DataArray(np.where(data['SM']<0, np.nan, data['SM']), dims=['lat','lon'], coords={'lat': lat_in,'lon': lon_in})
        
        sm_out = sm_in.reindex({'lat': lat_out,'lon': lon_out}, method='nearest')
        et_out = et_in.reindex({'lat': lat_out, 'lon': lon_out}, method='nearest')

        sm_map = np.where(sm_out.values>=0, sm_out, sm_map)
        et_map = np.where(et_out.values>=0, et_out, et_map)

    # -------------------------------------------------------------------------------------
    # Write outputs

    logging.info(" --> Write outputs")
    
    with rio.open(file_out_sm,'w',height=len(lat_out), width=len(lon_out), count=1, dtype='float32', crs='+proj=latlong', transform=transform, driver='GTiff') as out:
        out.write(sm_map,1)
    if data_settings['algorithm']['flags']['compress_output']:
        os.system('gzip -f ' + file_out_sm)
    
    with rio.open(file_out_et,'w',height=len(lat_out), width=len(lon_out), count=1, dtype='float32', crs='+proj=latlong', transform=transform, driver='GTiff') as out:
        out.write(et_map,1)
    if data_settings['algorithm']['flags']['compress_output']:
        os.system('gzip -f ' + file_out_et)

    # -------------------------------------------------------------------------------------
    # Info algorithm
    time_elapsed = round(time.time() - start_time, 1)

    if not_available_run > 0 :
        logging.info(' ')
        logging.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_release + ')')
        logging.info(' ==> TIME ELAPSED: ' + str(time_elapsed) + ' seconds')
        logging.info(' ==> SOME RUN RESULTS ARE MISSING! SKIP LOCK FILE CREATION')
        logging.info(' ==> Bye, Bye')
        logging.info(' ============================================================================ ')
        sys.exit(1)
        # -------------------------------------------------------------------------------------

    else:
        logging.info(' ')
        logging.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_release + ')')
        logging.info(' ==> TIME ELAPSED: ' + str(time_elapsed) + ' seconds')
        logging.info(' ==> ... END')
        logging.info(' ==> Bye, Bye')
        logging.info(' ============================================================================ ')
        sys.exit(0)
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
# Method to get script argument(s)
def get_args():
    parser_handle = ArgumentParser()
    parser_handle.add_argument('-settings_file', action="store", dest="alg_settings")
    parser_handle.add_argument('-time', action="store", dest="alg_time")
    parser_values = parser_handle.parse_args()

    if parser_values.alg_settings:
        alg_settings = parser_values.alg_settings
    else:
        alg_settings = 'configuration.json'

    if parser_values.alg_time:
        alg_time = parser_values.alg_time
    else:
        alg_time = None

    return alg_settings, alg_time
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

# ----------------------------------------------------------------------------
# Call script from external library
if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------------

