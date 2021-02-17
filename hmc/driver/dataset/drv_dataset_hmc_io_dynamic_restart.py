"""
Class Features

Name:          drv_dataset_hmc_io_dynamic_restart
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging

from hmc.algorithm.default.lib_default_args import logger_name

from hmc.driver.dataset.drv_dataset_hmc_io_dynamic_forcing import DSetManager as DSetManager_Dynamic

# Log
log_stream = logging.getLogger(logger_name)

# Debug
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to configure datasets
class DSetManager(DSetManager_Dynamic):

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, dset,
                 terrain_values=None, terrain_geo_x=None, terrain_geo_y=None, terrain_transform=None, terrain_bbox=None,
                 dset_list_format=None,
                 dset_list_type=None,
                 dset_list_group=None,
                 template_time=None,
                 model_tag='hmc', datasets_tag='datasets',
                 coord_name_geo_x='Longitude', coord_name_geo_y='Latitude', coord_name_time='time',
                 dim_name_geo_x='west_east', dim_name_geo_y='south_north', dim_name_time='time',
                 dset_write_engine='netcdf4', dset_write_compression_level=9, dset_write_format='NETCDF4',
                 file_compression_mode=False, file_compression_ext='.gz',
                 **kwargs):

        if dset_list_format is None:
            dset_list_format = ['Gridded', 'Point']
        if dset_list_type is None:
            dset_list_type = ['ARCHIVE']
        if dset_list_group is None:
            dset_list_group = ['RESTART']

        super(DSetManager, self).__init__(dset,
                                          terrain_values, terrain_geo_x, terrain_geo_y,
                                          terrain_transform, terrain_bbox,
                                          dset_list_format=dset_list_format,
                                          dset_list_type=dset_list_type,
                                          dset_list_group=dset_list_group,
                                          template_time=template_time,
                                          model_tag=model_tag, datasets_tag=datasets_tag,
                                          coord_name_geo_x=coord_name_geo_x, coord_name_geo_y=coord_name_geo_y,
                                          coord_name_time=coord_name_time,
                                          dim_name_geo_x=dim_name_geo_x, dim_name_geo_y=dim_name_geo_y,
                                          dim_name_time=dim_name_time,
                                          dset_write_engine=dset_write_engine,
                                          dset_write_compression_level=dset_write_compression_level,
                                          dset_write_format=dset_write_format,
                                          file_compression_mode=file_compression_mode,
                                          file_compression_ext=file_compression_ext,
                                          )
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
