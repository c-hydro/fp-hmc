#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='HMC MODEL - MANAGER NWP ECMWF0100 - REALTIME'
script_version="1.0.0"
script_date='2020/11/27'

virtualenv_folder='/hydro/library/fp_libs_python3/'
virtualenv_name='virtualenv_python3'
script_folder='/hydro/library/fp_package_hmc/'

# Execution example:
# python3 HMC_Model_RUN_Manager.py -settings_algorithm hmc_model_settings_algorithm.json -settings_datasets hmc_model_settings_datasets.json -time "2020-11-02 12:00"
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get file information
script_file_runner='/hydro/library/fp_package_hmc/apps/HMC_Model_RUN_Manager.py'
settings_algorithm_runner='/hydro/fp_tools_runner/nwp_ecmwf0100_realtime/hmc_model_settings_algorithm_nwp_ecmwf0100_realtime.json'
settings_datasets_runner='/hydro/fp_tools_runner/nwp_ecmwf0100_realtime/hmc_model_settings_datasets_nwp_ecmwf0100_realtime.json'

script_file_converter_json2dew='/hydro/library/fp_package_hmc/tools/postprocessing_tool_json2dew_converter/hmc_tool_postprocessing_json2dew_converter.py'
settings_algorithm_converter_json2dew='/hydro/fp_tools_runner/nwp_ecmwf0100_realtime/hmc_model_converter_json2dew_nwp_ecmwf0100_realtime.json'

folder_name_obs_raw='/hydro/data/data_dynamic/outcome/obs/weather_stations/%Y/%m/%d/'
file_name_obs_raw='ws.db.%Y%m%d%H00.nc.gz'
searching_period_hour_obs=4

folder_name_for_raw='/hydro/data/data_dynamic/outcome/nwp/ecmwf0100/%Y/%m/%d/'
file_name_for_raw='nwp.ecmwf0100.%Y%m%d0000.nc.gz'
searching_period_hour_for=0

folder_name_datasets_lock_raw='/hydro/lock/nwp/'
file_name_datasets_lock_start_raw='hyde_lock_nwp_ecmwf0100_realtime_%Y%m%d_START.txt'
file_name_datasets_lock_end_raw='hyde_lock_nwp_ecmwf0100_realtime_%Y%m%d_END.txt'
file_lock_datasets_check=true

folder_name_hmc_lock_raw='/hydro/lock/hmc/'
file_name_hmc_lock_start_raw='hmc_lock_nwp_ecmwf0100_realtime_%Y%m%d_START.txt'
file_name_hmc_lock_end_raw='hmc_lock_nwp_ecmwf0100_realtime_%Y%m%d_END.txt'
file_lock_hmc_init=false

# Get information (-u to get gmt time)
time_now=$(date -u +"%Y-%m-%d %H:00")
#time_now='2020-12-21 13:21' # DEBUG 
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
# Search forecast latest filename
echo " ====> SEARCH LATEST FOR FILENAME ..."
for hour in $(seq 0 $searching_period_hour_for); do
    
    # ----------------------------------------------------------------------------------------
    # Get time step
    time_step_for=$(date -d "$time_now ${hour} hour ago" +'%Y-%m-%d %H:00')
	# ----------------------------------------------------------------------------------------
	
    # ----------------------------------------------------------------------------------------
    # Info time start
    echo " =====> TIME_STEP "$time_step_for" ... "

    year_step=$(date -u -d "$time_step_for" +"%Y")
    month_step=$(date -u -d "$time_step_for" +"%m")
    day_step=$(date -u -d "$time_step_for" +"%d")
    hour_step=$(date -u -d "$time_step_for" +"%H")
    minute_step=$(date -u -d "$time_step_for" +"%M")
    # ----------------------------------------------------------------------------------------
	
	# ----------------------------------------------------------------------------------------
	# Define dynamic folder(s)
    folder_name_for_step=${folder_name_for_raw/'%Y'/$year_step}
    folder_name_for_step=${folder_name_for_step/'%m'/$month_step}
    folder_name_for_step=${folder_name_for_step/'%d'/$day_step}
    folder_name_for_step=${folder_name_for_step/'%H'/$hour_step}

    file_name_for_step=${file_name_for_raw/'%Y'/$year_step}
    file_name_for_step=${file_name_for_step/'%m'/$month_step}
    file_name_for_step=${file_name_for_step/'%d'/$day_step}
    file_name_for_step=${file_name_for_step/'%H'/$hour_step}
    # ----------------------------------------------------------------------------------------
    
    # ----------------------------------------------------------------------------------------
    # Search obs file name
    echo " ======> FILENAME ${file_name_for_step} ... "
    # Create local folder
    if [ -f "${folder_name_for_step}${file_name_for_step}" ]; then
        echo " ======> FILENAME ${file_name_for_step} ... FOUND"
        echo " =====> TIME_STEP "$time_step_for" ... DONE"
        time_step_for_ref=$time_step_for
        file_name_for_flag=true
        break
    else
        echo " ======> FILENAME ${file_name_for_step} ... NOT FOUND"
        echo " =====> TIME_STEP "$time_step_for" ... DONE"
        file_name_for_flag=false
    fi
    # ----------------------------------------------------------------------------------------
    
done
echo " ====> SEARCH LATEST FOR FILENAME ... DONE"
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Select reference time
echo " ====> SELECT REFERENCE TIME ... "
if $file_name_obs_flag & $file_name_for_flag ; then
    echo " =====> TIME NOW: ${time_now} -- TIME OBS: ${time_step_obs_ref} -- TIME FOR: ${time_step_for_ref} "
    time_ref=$time_step_obs_ref
    echo " =====> TIME REFERENCE: ${time_step_obs_ref} :: USE TIME OBS"
else
    echo " ====> SELECT REFERENCE TIME ... FAILED. OBS OR FOR FILENAMES WERE NOT SELECTED. EXIT."
    echo " ===> EXECUTION ... FAILED."
    exit
fi 

# Get time reference information
year_ref=$(date -u -d "$time_ref" +"%Y")
month_ref=$(date -u -d "$time_ref" +"%m")
day_ref=$(date -u -d "$time_ref" +"%d")
hour_ref=$(date -u -d "$time_ref" +"%H")
minute_ref=$(date -u -d "$time_ref" +"%M")
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Select lock datasets filename()
echo " ====> SELECT DATASETS LOCK FILENAMES ... "

folder_name_datasets_lock_ref=${folder_name_datasets_lock_raw/"%Y"/$year_ref}
folder_name_datasets_lock_ref=${folder_name_datasets_lock_ref/"%m"/$month_ref}
folder_name_datasets_lock_ref=${folder_name_datasets_lock_ref/"%d"/$day_ref}
folder_name_datasets_lock_ref=${folder_name_datasets_lock_ref/"%H"/$hour_ref}

file_name_datasets_lock_start_ref=${file_name_datasets_lock_start_raw/"%Y"/$year_ref}
file_name_datasets_lock_start_ref=${file_name_datasets_lock_start_ref/"%m"/$month_ref}
file_name_datasets_lock_start_ref=${file_name_datasets_lock_start_ref/"%d"/$day_ref}
file_name_datasets_lock_start_ref=${file_name_datasets_lock_start_ref/"%H"/$hour_ref}

file_name_datasets_lock_end_ref=${file_name_datasets_lock_end_raw/"%Y"/$year_ref}
file_name_datasets_lock_end_ref=${file_name_datasets_lock_end_ref/"%m"/$month_ref}
file_name_datasets_lock_end_ref=${file_name_datasets_lock_end_ref/"%d"/$day_ref}
file_name_datasets_lock_end_ref=${file_name_datasets_lock_end_ref/"%H"/$hour_ref}

# Path(S)
path_file_lock_datasets_start_ref=$folder_name_datasets_lock_ref/$file_name_datasets_lock_start_ref 
path_file_lock_datasets_end_ref=$folder_name_datasets_lock_ref/$file_name_datasets_lock_end_ref 

# Check lock conditions
echo " =====> CHECK DATASETS LOCK FILES ... "
if $file_lock_datasets_check; then

    echo " ======> LOCK START FILE ${file_name_datasets_lock_start_ref} ... "
    if [ -f "$path_file_lock_datasets_start_ref" ]; then
       flag_datasets_lock_start_ref=true
       echo " ======> LOCK START FILE ${file_name_datasets_lock_start_ref} ... FOUND"
    else
        flag_datasets_lock_start_ref=false
        echo " ======> LOCK START FILE ${file_name_datasets_lock_start_ref} ... NOT FOUND"
    fi
    
    echo " ======> LOCK END FILE ${file_name_datasets_lock_end_ref} ... "
    if [ -f "$path_file_lock_datasets_end_ref" ]; then
       flag_datasets_lock_end_ref=true
       echo " ======> LOCK START FILE ${file_name_datasets_lock_end_ref} ... FOUND"
    else
       flag_datasets_lock_end_ref=false
       echo " ======> LOCK START FILE ${file_name_datasets_lock_end_ref} ... NOT FOUND"
    fi
    echo " =====> CHECK DATASETS LOCK FILES ... DONE!"
    
else

    echo " =====> CHECK DATASETS LOCK FILES ... SKIPPED!"
    flag_datasets_lock_start_ref=true
    flag_datasets_lock_end_ref=true
    
fi

echo " ====> SELECT DATASETS LOCK FILENAMES ... DONE"
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Select lock datasets and hmc filename()
echo " ====> SELECT HMC LOCK FILENAMES ... "

folder_name_hmc_lock_ref=${folder_name_hmc_lock_raw/"%Y"/$year_ref}
folder_name_hmc_lock_ref=${folder_name_hmc_lock_ref/"%m"/$month_ref}
folder_name_hmc_lock_ref=${folder_name_hmc_lock_ref/"%d"/$day_ref}
folder_name_hmc_lock_ref=${folder_name_hmc_lock_ref/"%H"/$hour_ref}

file_name_hmc_lock_start_ref=${file_name_hmc_lock_start_raw/"%Y"/$year_ref}
file_name_hmc_lock_start_ref=${file_name_hmc_lock_start_ref/"%m"/$month_ref}
file_name_hmc_lock_start_ref=${file_name_hmc_lock_start_ref/"%d"/$day_ref}
file_name_hmc_lock_start_ref=${file_name_hmc_lock_start_ref/"%H"/$hour_ref}

file_name_hmc_lock_end_ref=${file_name_hmc_lock_end_raw/"%Y"/$year_ref}
file_name_hmc_lock_end_ref=${file_name_hmc_lock_end_ref/"%m"/$month_ref}
file_name_hmc_lock_end_ref=${file_name_hmc_lock_end_ref/"%d"/$day_ref}
file_name_hmc_lock_end_ref=${file_name_hmc_lock_end_ref/"%H"/$hour_ref}

# Path(S)
path_file_lock_hmc_start_ref=$folder_name_hmc_lock_ref/$file_name_hmc_lock_start_ref 
path_file_lock_hmc_end_ref=$folder_name_hmc_lock_ref/$file_name_hmc_lock_end_ref 

# Create folder(s)
if [ ! -d "$folder_name_hmc_lock_ref" ]; then
	mkdir -p $folder_name_hmc_lock_ref
fi

# Init lock conditions
echo " =====> INITIALIZE HMC LOCK FILES ... "
if $file_lock_hmc_init; then
    # Delete lock files
    if [ -f "$path_file_lock_hmc_start_ref" ]; then
       rm "$path_file_lock_hmc_start_ref"
    fi
    if [ -f "$path_file_lock_hmc_end_ref" ]; then
       rm "$path_file_lock_hmc_end_ref"
    fi
    echo " =====> INITIALIZE HMC LOCK FILES ... DONE!"
else
    echo " =====> INITIALIZE HMC LOCK FILES ... SKIPPED!"
fi

echo " ====> SELECT HMC LOCK FILENAMES ... DONE"
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Check datasets availability
echo " ====> CHECK DATASETS AVAILABILITY ... "
if [ $flag_datasets_lock_start_ref ] && [ $flag_datasets_lock_end_ref ]; then
    
    #-----------------------------------------------------------------------------------------
    # Datasets lock files found
    echo " ====> CHECK DATASETS AVAILABILITY ... DONE"
    #-----------------------------------------------------------------------------------------
    
    #-----------------------------------------------------------------------------------------
    # Check execution
    if [ -f $path_file_lock_hmc_start_ref ] && [ -f $path_file_lock_hmc_end_ref ]; then
        
        #-----------------------------------------------------------------------------------------
        # Process completed
        echo " ===> EXECUTION ... SKIPPED! ALL DATA WERE PROCESSED DURING A PREVIOUSLY RUN"
        #-----------------------------------------------------------------------------------------

    elif [ -f $path_file_lock_hmc_start_ref ] && [ ! -f $path_file_lock_hmc_end_ref ]; then
        
        #-----------------------------------------------------------------------------------------
        # Process running condition
        echo " ===> EXECUTION ... SKIPPED! SCRIPT IS STILL RUNNING ... WAIT FOR PROCESS END"
        #-----------------------------------------------------------------------------------------
        
    elif [ ! -f $path_file_lock_hmc_start_ref ] && [ ! -f $path_file_lock_hmc_end_ref ]; then
        
        #-----------------------------------------------------------------------------------------
        # Lock File START
        time_lock_start=$(date +"%Y-%m-%d %H:%S")
        echo " ================================ " >> $path_file_lock_hmc_start_ref
        echo " ==== EXECUTION START REPORT ==== " >> $path_file_lock_hmc_start_ref
        echo " " >> $path_file_lock_hmc_start_ref
        echo " ==== PID:" $execution_pid >> $path_file_lock_hmc_start_ref
        echo " ==== Algorithm: $script_name" >> $path_file_lock_hmc_start_ref
        echo " ==== RunTime: $time_lock_start" >> $path_file_lock_hmc_start_ref
        echo " ==== ExecutionTime: $time_ref" >> $path_file_lock_hmc_start_ref
        echo " ==== Status: RUNNING" >> $path_file_lock_hmc_start_ref
        echo " " >> $path_file_lock_hmc_start_ref
        echo " ================================ " >> $path_file_lock_hmc_start_ref
	
        #-----------------------------------------------------------------------------------------
        # Run hmc model instance (using settings and time)
        echo " ====> RUN HMC MODEL INSTANCE ... "
        
        # Execute python script to run the model
	echo " =====> COMMAND LINE: " python $script_file_runner -settings_algorithm $settings_algorithm_runner -settings_datasets $settings_datasets_runner -time $time_now
        python $script_file_runner -settings_algorithm $settings_algorithm_runner -settings_datasets $settings_datasets_runner -time "$time_ref"
        
        echo " ====> RUN HMC MODEL INSTANCE ... DONE"

	# Postprocess model instance (using settings and time)
	echo " ====> POSTPROCESS HMC MODEL INSTANCE ... "

	# Execute python script to convert time-series from json to dewetra format
	echo " =====> CONVERT JSON2DEW ... "
	echo " ======> COMMAND LINE: " python $script_file_converter_json2dew -settings_file $settings_algorithm_converter_json2dew -time $time_ref
	python $script_file_converter_json2dew -settings_file $settings_algorithm_converter_json2dew -time "$time_ref"
	echo " =====> CONVERT JSON2DEW ... DONE"

	echo " ====> POSTPROCESS HMC MODEL INSTANCE ... DONE"
        
        # Lock File END
        time_lock_end=$(date +"%Y-%m-%d %H:%S")
        echo " ============================== " >> $path_file_lock_hmc_end_ref
        echo " ==== EXECUTION END REPORT ==== " >> $path_file_lock_hmc_end_ref
        echo " " >> $path_file_lock_hmc_end_ref
        echo " ==== PID:" $execution_pid >> $path_file_lock_hmc_end_ref
        echo " ==== Algorithm: $script_name" >> $path_file_lock_hmc_end_ref
        echo " ==== RunTime: $time_lock_end" >> $path_file_lock_hmc_end_ref
        echo " ==== ExecutionTime: $time_ref" >> $path_file_lock_hmc_end_ref
        echo " ==== Status: COMPLETED" >>  $path_file_lock_hmc_end_ref
        echo " " >> $path_file_lock_hmc_end_ref
        echo " ============================== " >> $path_file_lock_hmc_end_ref
        
        # Info script end
        echo " ===> EXECUTION ... DONE"
        #-----------------------------------------------------------------------------------------
        
    else
        
        #-----------------------------------------------------------------------------------------
        # Exit unexpected mode
        echo " ===> EXECUTION ... FAILED! SCRIPT ENDED FOR UNKNOWN HMC LOCK FILES CONDITION!"
        #-----------------------------------------------------------------------------------------
        
    fi
    #-----------------------------------------------------------------------------------------
    
else
    
    #-----------------------------------------------------------------------------------------
    # Exit datasest lock files not found
    echo " ====> CHECK DATASETS AVAILABILITY ... FAILED. DATASETS NOT AVAILABLE"
    echo " ===> EXECUTION ... FAILED!"
    #-----------------------------------------------------------------------------------------

fi

echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------	


