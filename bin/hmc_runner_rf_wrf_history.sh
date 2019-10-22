#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='HMC RUNNER - RF WRF - HISTORY'
script_version="1.5.0"
script_date='2019/10/16'

script_folder='/share/c-hydro/hmc-master/'
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get file information
script_file_hmc='/share/c-hydro/hmc-master/apps/HMC_Model_RUN_Manager.py'
setting_file_hmc='/share/c-hydro/hmc-master/config/algorithms/hmc_model_run-manager_algorithm_rf_wrf_history.config'

script_file_dewetra='/share/c-hydro/hyde-master/bin/utils/dewetra/HYDE_Dewetra_HMC_Det2Ensemble.py'
setting_file_dewetra='/share/c-hydro/hyde-master/bin/utils/dewetra/hyde_dewetra_hmc_rf_wrf_det2ensemble_history.json'

env_flag=false

folder_lock_raw='/share/c-hydro/lock/'
file_lock_start_raw='hmc_runner_rf_wrf_lock_%YYYY%MM%DD%HH00_history_START.txt'
file_lock_end_raw='hmc_runner_rf_wrf_lock_%YYYY%MM%DD%HH00_history_END.txt'

folder_name_list=('/share/c-hydro/lock/' '/share/c-hydro/lock/' '/share/c-hydro/lock/' '/share/c-hydro/lock/')
file_name_list=('nwp_dynamicdata_wrf_lock_%YYYY%MM%DD%HH00_history_START.txt' 'nwp_dynamicdata_wrf_lock_%YYYY%MM%DD%HH00_history_START.txt'
				 'rf_model_wrf_lock_%YYYY%MM%DD%HH00_history_START.txt' 'rf_model_wrf_lock_%YYYY%MM%DD%HH00_history_END.txt')

# Get information (-u to get gmt time)
time_system=$(date +"%Y-%m-%d %H:00")
# time_system=$(date -u +"%Y-%m-%d %H:00")
time_system='2019-10-16 11:32' # DEBUG 
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Add path to pythonpath
export PYTHONPATH="${PYTHONPATH}:$script_folder"

# Export library for flood proofs package(s)
#export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/zlib-1.2.8/lib/
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/zlib-1.2.11/lib/
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/hdf5-1.8.17/lib/
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/netcdf-4.1.2/lib/
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/geos-3.5.0/lib/
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/proj-4.9.2/lib/
#export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/share/c-hydro/library/gdal-2.3.0/lib/

# Export binaries for flood proofs package(s)
export PATH=/share/c-hydro/library/hdf5-1.8.17/bin:$PATH
#export PATH=/share/c-hydro/library/zlib-1.2.8/bin:$PATH
export PATH=/share/c-hydro/library/zlib-1.2.11/bin:$PATH
export PATH=/share/c-hydro/library/netcdf-4.1.2/bin:$PATH
export PATH=/share/c-hydro/library/geos-3.5.0/bin:$PATH
export PATH=/share/c-hydro/library/proj-4.9.2/bin:$PATH
#export PATH=/share/c-hydro/library/gdal-2.3.0/bin:$PATH
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Set hour of the model starting from time system
hour_system=$(date +%H -d "$time_system")
if [ "$hour_system" -ge 12 ]; then
	time_run=$(date +%Y%m%d1200 -d "$time_system")
	time_now="$(date +%Y-%m-%d -d "$time_system") 12:00"
	time_now=$(date -d "$time_now" +'%Y-%m-%d %H:%M' )
else
	time_run=$(date +%Y%m%d0000 -d "$time_system")
	time_now="$(date +%Y-%m-%d -d "$time_system") 00:00"
	time_now=$(date -d "$time_now" +'%Y-%m-%d %H:%M' )
fi
#-----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script start
echo " ==================================================================================="
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> START ..."
echo " ==> COMMAND LINE: " python3 $script_file -settingfile $setting_file -time $time_now [time_system $time_system]

# Get time information
time_exe=$(date)

year=${time_now:0:4}
month=${time_now:5:2}
day=${time_now:8:2}
hour=${time_now:11:2}

# Define path(s)
folder_lock_def=${folder_lock_raw/"%YYYY"/$year}
folder_lock_def=${folder_lock_def/"%MM"/$month}
folder_lock_def=${folder_lock_def/"%DD"/$day}
folder_lock_def=${folder_lock_def/"%HH"/$hour}

# Define filename(s)
file_lock_start_def=${file_lock_start_raw/"%YYYY"/$year}
file_lock_start_def=${file_lock_start_def/"%MM"/$month}
file_lock_start_def=${file_lock_start_def/"%DD"/$day}
file_lock_start_def=${file_lock_start_def/"%HH"/$hour}

file_lock_end_def=${file_lock_end_raw/"%YYYY"/$year}
file_lock_end_def=${file_lock_end_def/"%MM"/$month}
file_lock_end_def=${file_lock_end_def/"%DD"/$day}
file_lock_end_def=${file_lock_end_def/"%HH"/$hour}
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Check environment flag
if $env_flag; then

	# Iteration(s) to search checking file
	for ((i=0;i<${#folder_name_list[@]};++i)); do
		
		# ----------------------------------------------------------------------------------------
		# Folder and file information
		folder_name_raw=${folder_name_list[i]}
		file_name_raw=${file_name_list[i]}
		
		folder_name_def=${folder_name_raw/"%YYYY"/$year}
		folder_name_def=${folder_name_def/"%MM"/$month}
		folder_name_def=${folder_name_def/"%DD"/$day}
		folder_name_def=${folder_name_def/"%HH"/$hour}    


		file_name_def=${file_name_raw/"%YYYY"/$year}
		file_name_def=${file_name_def/"%MM"/$month}
		file_name_def=${file_name_def/"%DD"/$day}
		file_name_def=${file_name_def/"%HH"/$hour}

		path_name_def=$folder_name_def/$file_name_def
		# ----------------------------------------------------------------------------------------
	   	
		# ----------------------------------------------------------------------------------------
		# Check file availability
		echo " ===> SEARCH FILE: $path_name_def ... "
		if [ -f $path_name_def ]; then
		   	echo " ===> SEARCH FILE: $path_name_def ... DONE"
			file_check=true
		else
			echo " ===> SEARCH FILE: $path_name_def ... FAILED! FILE NOT FOUND!"
			file_check=false
			break
		fi
		# ----------------------------------------------------------------------------------------

	done
	
	# Resume of data availability
	if $file_check; then
		echo " ===> SEARCH FILE(S) COMPLETED. ALL FILES ARE AVAILABLE"
	else
		echo " ===> SEARCH FILE(S) INTERRUPTED. ONE OR MORE FILE(S) IN SEARCHING PERIOD ARE NOT AVAILABLE"
	fi
	# ----------------------------------------------------------------------------------------

else
	# ----------------------------------------------------------------------------------------
	# Condition for environment flag deactivated
	echo " ===> SEARCH FILE(S) SKIPPED. ENVIRONMENT FLAG IS DEACTIVATED"
	file_check=true
	# ----------------------------------------------------------------------------------------
fi
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Run according with file(s) availability
echo " ===> EXECUTE SCRIPT ... "
if $file_check; then

	# ----------------------------------------------------------------------------------------	
	# Create folder(s)
	if [ ! -d "$folder_lock_def" ]; then
		mkdir -p $folder_lock_def
	fi
	
	# Define path(s) 
    path_file_lock_def_start=$folder_lock_def/$file_lock_start_def
    path_file_lock_def_end=$folder_lock_def/$file_lock_end_def

	if ! $env_flag; then
		if [ -f $path_file_lock_def_start ]; then
			rm $path_file_lock_def_start
		fi
		if [ -f $path_file_lock_def_end ]; then
			rm $path_file_lock_def_end
		fi
	fi
    #-----------------------------------------------------------------------------------------
    
    #-----------------------------------------------------------------------------------------
    # Run check
    if [ -f $path_file_lock_def_start ] && [ -f $path_file_lock_def_end ]; then
        
        #-----------------------------------------------------------------------------------------
        # Process completed
        echo " ===> EXECUTE SCRIPT ... SKIPPED!"
		echo " ===> ALL DATA HAVE BEEN PROCESSED DURING A PREVIOUSLY RUN"
        #-----------------------------------------------------------------------------------------
    
    elif [ -f $path_file_lock_def_start ] && [ ! -f $path_file_lock_def_end ]; then
        
        #-----------------------------------------------------------------------------------------
        # Process running condition
        echo " ===> EXECUTE SCRIPT ... SKIPPED!"
		echo " ===> SCRIPT STILL RUNNING ... WAIT FOR PROCESS END"
        #-----------------------------------------------------------------------------------------
        
    elif [ ! -f $path_file_lock_def_start ] && [ ! -f $path_file_lock_def_end ]; then
        
        #-----------------------------------------------------------------------------------------
        # Lock File START
        time_step=$(date +"%Y%m%d%H%S")
        echo " ==== SCRIPT START" >> $path_file_lock_def_start
        echo " ==== Script name: $script_name" >> $path_file_lock_def_start
        echo " ==== Script run time: $time_step" >> $path_file_lock_def_start
        echo " ==== Script exe time: $time_exe" >> $path_file_lock_def_start
        echo " ==== Script execution running ..." >> $path_file_lock_def_start
        #-----------------------------------------------------------------------------------------

		#-----------------------------------------------------------------------------------------
		# Run python script (using setting and time)
		echo " ====> HMC RUN(S) ... "
		python3 $script_file_hmc -settingfile $setting_file_hmc -time $time_run
		echo " ====> HMC RUN(S) ... DONE"
		
		echo " ====> DEWETRA PROBABILISTIC TIME-SERIES ... "
		python3 $script_file_dewetra -settingfile $setting_file_dewetra -time $time_run
		echo " ====> DEWETRA PROBABILISTIC TIME-SERIES ... DONE"
		#-----------------------------------------------------------------------------------------
        
        #-----------------------------------------------------------------------------------------
        # Lock File END
        time_step=$(date +"%Y%m%d%H%S")
        echo " ==== SCRIPT END" >> $path_file_lock_def_end
        echo " ==== Script name: $script_name" >> $path_file_lock_def_end
        echo " ==== Script run time: $time_step" >> $path_file_lock_def_end
        echo " ==== Script exe time: $time_exe" >> $path_file_lock_def_end
        echo " ==== Script execution finished" >>  $path_file_lock_def_end
        #-----------------------------------------------------------------------------------------
        
        #-----------------------------------------------------------------------------------------
        # Exit
        echo " ===> EXECUTE SCRIPT ... DONE!"
        #-----------------------------------------------------------------------------------------

    else
        
        #-----------------------------------------------------------------------------------------
        # Exit unexpected mode
        echo " ===> EXECUTE SCRIPT ... FAILED!"
		echo " ===> SCRIPT ENDED FOR UNKNOWN LOCK CONDITION!"
        #-----------------------------------------------------------------------------------------
        
    fi
    #-----------------------------------------------------------------------------------------

else

    #-----------------------------------------------------------------------------------------
    # Exit
    echo " ===> EXECUTE SCRIPT ... FAILED!"
	echo " ===> SCRIPT INTERRUPTED! ONE OR MORE INPUT FILE(S) ARE UNAVAILABLE!"
    #-----------------------------------------------------------------------------------------
    
fi

# Info script end
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> ... END"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------







