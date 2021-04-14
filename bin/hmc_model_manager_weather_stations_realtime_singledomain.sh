#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='HMC MODEL - MANAGER WEATHER STATIONS - REALTIME SINGLEDOMAIN'
script_version="1.0.0"
script_date='2020/11/27'

virtualenv_folder='/hydro/library/fp_libs_python3/'
virtualenv_name='virtualenv_python3'
script_folder='/hydro/library/hmc/'

# Execution example:
# python3 HMC_Model_RUN_Manager.py -settings_algorithm hmc_model_settings_algorithm.json -settings_datasets hmc_model_settings_datasets.json -time "2020-11-02 12:00"
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get file information
script_file_runner='/hydro/library/hmc/apps/HMC_Model_RUN_Manager.py'
settings_algorithm_runner='/hydro/fp_tools_runner/weather_stations_realtime/hmc_model_settings_algorithm_weather_stations_realtime.json'
settings_datasets_runner='/hydro/fp_tools_runner/weather_stations_realtime/hmc_model_settings_datasets_weather_stations_realtime.json'

script_file_converter_json2dew='/hydro/library/hmc/tools/postprocessing_tool_json2dew_converter/hmc_tool_postprocessing_json2dew_converter.py'
settings_algorithm_converter_json2dew='/hydro/fp_tools_runner/weather_stations_realtime/hmc_model_converter_json2dew_weather_stations_realtime.json'

folder_name_obs_raw='/hydro/data/data_dynamic/outcome/obs/weather_stations/%Y/%m/%d/'
file_name_obs_raw='ws.db.%Y%m%d%H00.nc.gz'
searching_period_hour_obs=2

# Get information (-u to get gmt time)
time_now=$(date -u +"%Y-%m-%d %H:00")
# time_now='2020-12-21 09:55' # DEBUG 
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Activate virtualenv
export PATH=$virtualenv_folder/bin:$PATH
source activate $virtualenv_name

# Add path to pythonpath
export PYTHONPATH="${PYTHONPATH}:$script_folder"
#-----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script start
echo " ==================================================================================="
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> START ..."
echo " ===> EXECUTION ..."

time_now=$(date -d "$time_now" +'%Y-%m-%d %H:00')
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Search obs latest filename
echo " ====> SEARCH LATEST OBS FILENAME ..."
for hour in $(seq 0 $searching_period_hour_obs); do
    
    # ----------------------------------------------------------------------------------------
    # Get time step
    time_step_obs=$(date -d "$time_now ${hour} hour ago" +'%Y-%m-%d %H:00')
	# ----------------------------------------------------------------------------------------
	
    # ----------------------------------------------------------------------------------------
    # Info time start
    echo " =====> TIME_STEP "$time_step_obs" ... "

    year_step=$(date -u -d "$time_step_obs" +"%Y")
    month_step=$(date -u -d "$time_step_obs" +"%m")
    day_step=$(date -u -d "$time_step_obs" +"%d")
    hour_step=$(date -u -d "$time_step_obs" +"%H")
    minute_step=$(date -u -d "$time_step_obs" +"%M")
    # ----------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------
    # Define dynamic folder(s)
    folder_name_obs_step=${folder_name_obs_raw/'%Y'/$year_step}
    folder_name_obs_step=${folder_name_obs_step/'%m'/$month_step}
    folder_name_obs_step=${folder_name_obs_step/'%d'/$day_step}
    folder_name_obs_step=${folder_name_obs_step/'%H'/$hour_step}

    file_name_obs_step=${file_name_obs_raw/'%Y'/$year_step}
    file_name_obs_step=${file_name_obs_step/'%m'/$month_step}
    file_name_obs_step=${file_name_obs_step/'%d'/$day_step}
    file_name_obs_step=${file_name_obs_step/'%H'/$hour_step}
    # ----------------------------------------------------------------------------------------
    
    # ----------------------------------------------------------------------------------------
    # Search obs file name
    echo " ======> FILENAME ${file_name_obs_step} ... "
    # Create local folder
    if [ -f "${folder_name_obs_step}${file_name_obs_step}" ]; then
        echo " ======> FILENAME ${file_name_obs_step} ... FOUND"
        echo " =====> TIME_STEP "$time_step_obs" ... DONE"
        time_step_obs_ref=$time_step_obs
        file_name_obs_flag=true
        break
    else
        echo " ======> FILENAME ${file_name_obs_step} ... NOT FOUND"
        echo " =====> TIME_STEP "$time_step_obs" ... DONE"
        file_name_obs_flag=false
    fi
    # ----------------------------------------------------------------------------------------
    
done
echo " ====> SEARCH LATEST OBS FILENAME ... DONE"
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Select reference time
echo " ====> SELECT REFERENCE TIME ... "
if $file_name_obs_flag ; then
    echo " =====> TIME NOW: ${time_now} -- TIME OBS: ${time_step_obs_ref} "
    time_ref=$time_step_obs_ref
    echo " =====> TIME REFERENCE: ${time_step_obs_ref} :: USE TIME OBS"
else
    echo " ====> SELECT REFERENCE TIME ... FAILED. OBS OR FOR FILENAMES WERE NOT SELECTED. EXIT."
    exit
fi 
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Run python model instance (using settings and time)
echo " ====> RUN HMC MODEL INSTANCE ... "

# Execute python script to run the model instance
echo " =====> COMMAND LINE: " python $script_file_runner -settings_algorithm $settings_algorithm_runner -settings_datasets $settings_datasets_runner -time $time_ref
python $script_file_runner -settings_algorithm $settings_algorithm_runner -settings_datasets $settings_datasets_runner -time "$time_ref"

echo " ====> RUN HMC MODEL INSTANCE ... DONE"

# Postprocess model instance (using settings and time)
echo " ====> POSTPROCESS HMC MODEL INSTANCE ... "

# # Execute python script to convert time-series from json to dewetra format
echo " =====> CONVERT JSON2DEW ... "
echo " ======> COMMAND LINE: " python $script_file_converter_json2dew -settings_file $settings_algorithm_converter_json2dew -time $time_ref
python $script_file_converter_json2dew -settings_file $settings_algorithm_converter_json2dew -time "$time_ref"
echo " =====> CONVERT JSON2DEW ... DONE"

echo " ====> POSTPROCESS HMC MODEL INSTANCE ... DONE"
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script end
echo " ===> EXECUTION ... DONE"
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------



