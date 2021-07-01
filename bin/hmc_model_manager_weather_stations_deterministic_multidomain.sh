#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='HMC MODEL - MANAGER WEATHER STATIONS - REALTIME MULTIDOMAIN'
script_version="1.1.0"
script_date='2021/04/07'

virtualenv_folder='/home/cfmi.arpal.org/continuum/library/fp_virtualenv_python3_hmc/'
virtualenv_name='fp_virtualenv_python3_hmc_libraries'
script_folder='/home/cfmi.arpal.org/continuum/library/fp-dev-hmc/'

# Domain list
domain_name_list=("CentaDomain")

# Execution example:
# python3 HMC_Model_RUN_Manager.py -settings_algorithm hmc_model_settings_algorithm.json -settings_datasets hmc_model_settings_datasets.json -time "2020-11-02 12:00"
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get file information
script_file='/home/cfmi.arpal.org/continuum/library/fp-dev-hmc/apps/HMC_Model_RUN_Manager.py'
settings_algorithm_raw='/home/cfmi.arpal.org/continuum/fp_tools_runner/weather_stations_state/%DOMAIN_NAME/hmc_model_settings_algorithm_weather_stations_state.json'
settings_datasets_raw='/home/cfmi.arpal.org/continuum/fp_tools_runner/weather_stations_state/%DOMAIN_NAME/hmc_model_settings_datasets_weather_stations_state.json'

folder_name_obs_raw='/home/cfmi.arpal.org/continuum/ModelloContinuum/data/data_dynamic/LiguriaDomain/forcing/%Y/%m/%d/'
file_name_obs_raw='Rain_%Y%m%d%H00.tif'
searching_period_hour_obs=2

file_lock_init=true
folder_name_lock_raw="/home/cfmi.arpal.org/continuum/lock/hmc/weather_stations_state/"
file_name_lock_start_raw="hmc_%DOMAIN_NAME_lock_%Y%m%d_%H_START.txt"
file_name_lock_end_raw="hmc_%DOMAIN_NAME_lock_%Y%m%d_%H_END.txt"

# Get information (-u to get gmt time)
time_now=$(date -u +"%Y-%m-%d 12:00")
#time_now='2020-10-02 23:15' # DEBUG 
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

#-----------------------------------------------------------------------------------------
# Iterate over domain list
for domain_name_name in ${domain_name_list[@]}; do
	(
	
	# ----------------------------------------------------------------------------------------
	# Info domain name
	echo " ====> DOMAIN NAME "$domain_name_name" ... "
	
    # Execution pid
    execution_pid=$$
	
	# Define dynamic settings and datasets model files
	settings_algorithm_step=${settings_algorithm_raw/'%DOMAIN_NAME'/$domain_name_name}
	settings_datasets_step=${settings_datasets_raw/'%DOMAIN_NAME'/$domain_name_name}
	# ----------------------------------------------------------------------------------------
	
	# ----------------------------------------------------------------------------------------
	# Search obs latest filename
	echo " =====> SEARCH LATEST OBS FILENAME ..."
	for hour in $(seq 0 $searching_period_hour_obs); do
		
		# ----------------------------------------------------------------------------------------
		# Get time step
		time_step_obs=$(date -d "$time_now ${hour} hour ago" +'%Y-%m-%d %H:00')
		# ----------------------------------------------------------------------------------------
		
		# ----------------------------------------------------------------------------------------
		# Info time start
		echo " ======> TIME_STEP "$time_step_obs" ... "

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
		echo " =======> FILENAME ${file_name_obs_step} ... "
		# Create local folder
		if [ -f "${folder_name_obs_step}${file_name_obs_step}" ]; then
		    echo " =======> FILENAME ${file_name_obs_step} ... FOUND"
		    echo " ======> TIME_STEP "$time_step_obs" ... DONE"
		    time_step_obs_ref=$time_step_obs
		    file_name_obs_flag=true
		    break
		else
		    echo " =======> FILENAME ${file_name_obs_step} ... NOT FOUND"
		    echo " ======> TIME_STEP "$time_step_obs" ... FAILED"
		    file_name_obs_flag=false
		fi
		# ----------------------------------------------------------------------------------------
		
	done
	echo " =====> SEARCH LATEST OBS FILENAME ... DONE"
	# ----------------------------------------------------------------------------------------

	# ----------------------------------------------------------------------------------------
	# Select reference time
	echo " =====> SELECT REFERENCE TIME ... "
	if $file_name_obs_flag ; then
		echo " ======> TIME NOW: ${time_now} -- TIME OBS: ${time_step_obs_ref} "
		time_ref=$time_step_obs_ref
		echo " ======> TIME REFERENCE: ${time_step_obs_ref} :: USE TIME OBS"
	else
		echo " =====> SELECT REFERENCE TIME ... FAILED. OBS FILENAMES HAVE NOT BEEN SELECTED. EXIT."
		exit
	fi 
	# ----------------------------------------------------------------------------------------
	
	# ----------------------------------------------------------------------------------------
    # Define path data
    folder_name_lock_def=${folder_name_lock_raw/"%Y"/$year_step}
    folder_name_lock_def=${folder_name_lock_def/"%m"/$month_step}
    folder_name_lock_def=${folder_name_lock_def/"%d"/$day_step}
    folder_name_lock_def=${folder_name_lock_def/"%H"/$hour_step}
    folder_name_lock_def=${folder_name_lock_def/"%DOMAIN_NAME"/$domain_name_name}

    file_name_lock_start_def=${file_name_lock_start_raw/"%Y"/$year_step}
    file_name_lock_start_def=${file_name_lock_start_def/"%m"/$month_step}
    file_name_lock_start_def=${file_name_lock_start_def/"%d"/$day_step}
    file_name_lock_start_def=${file_name_lock_start_def/"%H"/$hour_step}
    file_name_lock_start_def=${file_name_lock_start_def/"%DOMAIN_NAME"/$domain_name_name}

    file_name_lock_end_def=${file_name_lock_end_raw/"%Y"/$year_step}
    file_name_lock_end_def=${file_name_lock_end_def/"%m"/$month_step}
    file_name_lock_end_def=${file_name_lock_end_def/"%d"/$day_step}
    file_name_lock_end_def=${file_name_lock_end_def/"%H"/$hour_step}
    file_name_lock_end_def=${file_name_lock_end_def/"%DOMAIN_NAME"/$domain_name_name}

    # Create folder(s)
    if [ ! -d "$folder_name_lock_def" ]; then
    	mkdir -p $folder_name_lock_def
    fi
    # ----------------------------------------------------------------------------------------	
	
	#-----------------------------------------------------------------------------------------
    # File lock definition
    path_name_lock_start_def=$folder_name_lock_def/$file_name_lock_start_def 
    path_name_lock_end_def=$folder_name_lock_def/$file_name_lock_end_def
   
    # Init lock conditions
    echo " =====> INITILIZE LOCK FILES ... "
    if $file_lock_init; then
        # Delete lock files
        if [ -f "$path_name_lock_start_def" ]; then
           rm "$path_name_lock_start_def"
        fi
        if [ -f "$path_name_lock_end_def" ]; then
           rm "$path_name_lock_end_def"
        fi
        echo " =====> INITILIZE LOCK FILES ... DONE!"
    else
        echo " =====> INITILIZE LOCK FILES ... SKIPPED!"
    fi
    #-----------------------------------------------------------------------------------------  
	
	# ----------------------------------------------------------------------------------------
	# Run python script (using settings, datasets and time arguments) 
    if [ -f $path_name_lock_start_def ] && [ -f $path_name_lock_end_def ]; then   
    
        #-----------------------------------------------------------------------------------------
        # Process completed
        echo " =====> RUN HMC MODEL [DOMAIN: $domain_name_name :: TIME: $time_ref] ... SKIPPED! ALL DATA WERE PROCESSED DURING A PREVIOUSLY RUN"
        #-----------------------------------------------------------------------------------------

    elif [ -f $path_name_lock_start_def ] && [ ! -f $path_name_lock_end_def ]; then
    
        #-----------------------------------------------------------------------------------------
        # Process running condition
        echo " =====> RUN HMC MODEL [DOMAIN: $domain_name_name :: TIME: $time_ref] ... SKIPPED! SCRIPT IS STILL RUNNING ... WAIT FOR PROCESS END"
    	#-----------------------------------------------------------------------------------------

    elif [ ! -f $path_name_lock_start_def ] && [ ! -f $path_name_lock_end_def ]; then
		
		#-----------------------------------------------------------------------------------------
		# Info start model run
		echo " =====> RUN HMC MODEL [DOMAIN: $domain_name_name :: TIME: $time_ref] ... "
		
		# Define command-line
		command_line_exec="python $script_file -settings_algorithm $settings_algorithm_step -settings_datasets $settings_datasets_step -time '"$time_ref"'"
		#command_line_exec="ls -l"
		echo " ======> COMMAND LINE: " $command_line_exec
		#-----------------------------------------------------------------------------------------
		
		#-----------------------------------------------------------------------------------------
		# Lock File START
		time_step=$(date +"%Y-%m-%d %H:%S")
		
		echo " ================================ " >> $path_name_lock_start_def
		echo " ==== EXECUTION START REPORT ==== " >> $path_name_lock_start_def
		echo " "
		echo " ==== PID:" $execution_pid >> $path_name_lock_start_def
		echo " ==== Algorithm: $script_name" >> $path_name_lock_start_def
		echo " ==== RunTime: $time_step" >> $path_name_lock_start_def
		echo " ==== ExecutionTime: $time_now" >> $path_name_lock_start_def
		echo " ==== Domain: $domain_name_name" >> $path_name_lock_start_def
		echo " ==== CMD: $command_line_exec" >> $path_name_lock_start_def
		echo " ==== Status: RUNNING" >> $path_name_lock_start_def
		echo " "
		echo " ================================ " >> $path_name_lock_start_def
		#-----------------------------------------------------------------------------------------
	
		#-----------------------------------------------------------------------------------------
	    # Run python script (using setting and time)
        if python $script_file -settings_algorithm $settings_algorithm_step -settings_datasets $settings_datasets_step -time "$time_ref"
        then
        	
        	#-----------------------------------------------------------------------------------------
			# Lock File END
            time_step=$(date +"%Y-%m-%d %H:%S")
            
    	    echo " ================================ " >> $path_name_lock_end_def
            echo " ==== EXECUTION END REPORT ====== " >> $path_name_lock_end_def
            echo " "
            echo " ==== PID:" $execution_pid >> $path_name_lock_end_def
            echo " ==== Algorithm: $script_name" >> $path_name_lock_end_def
            echo " ==== RunTime: $time_step" >> $path_name_lock_end_def
            echo " ==== ExecutionTime: $time_now" >> $path_name_lock_end_def
            echo " ==== Domain: $domain_name_name" >> $path_name_lock_end_def
			echo " ==== CMD: $command_line_exec" >> $path_name_lock_end_def
            echo " ==== Status: COMPLETED" >>  $path_name_lock_end_def
            echo " "
            echo " ================================ " >> $path_name_lock_end_def
            #-----------------------------------------------------------------------------------------
            
            #-----------------------------------------------------------------------------------------
            # Info end model run
            echo " =====> RUN HMC MODEL [DOMAIN: $domain_name_name :: TIME: $time_ref] ... DONE"
            #-----------------------------------------------------------------------------------------
            
        else
        	
        	#-----------------------------------------------------------------------------------------
        	# Exit with error(s)
            rm $path_name_lock_start_def
            echo " =====> RUN HMC MODEL [DOMAIN: $domain_name_name :: TIME: $time_ref] ... FAILED. HMC OR WRAPPER HAS CRASHED!"
            exit 1
            #-----------------------------------------------------------------------------------------
            
        fi
    
    else
              
		#-----------------------------------------------------------------------------------------
		# Exit unexpected mode
		echo " =====> RUN HMC MODEL [DOMAIN: $domain_name_name :: TIME: $time_ref] ... FAILED! SCRIPT ENDED FOR UNKNOWN LOCK FILES CONDITION!"
		#-----------------------------------------------------------------------------------------
        
    fi
	
	sleep 5
	#-----------------------------------------------------------------------------------------
	
	#-----------------------------------------------------------------------------------------
	# Info domain end
	echo " ====> DOMAIN NAME "$domain_name_name" ... DONE"
	# ----------------------------------------------------------------------------------------
	
    ) &
done

# Wait processe(s)
wait
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script end
echo " ===> EXECUTION ... DONE"
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------



