#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='IGAD - POSTPROCESSING - MOSAIC OUTPUT'
script_version="1.0.0"
script_date='2021/04/12'

system_library_folder='/home/fp/library/'
fp_folder='/home/fp/fp_igad/'
lock_folder='/home/fp/fp_igad/lock/'
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get file information
virtualenv_folder=$system_library_folder'fp_virtualenv_python3/'
virtualenv_name='fp_virtualenv_python3_hyde'

script_folder=$system_library_folder'igad/'
script_file=$script_folder'postprocessing/igad_postprocessing_merge_gridded_output.py'
settings_file=$fp_folder'fp_tools_postprocessing/storage/igad_postprocessing_merge_gridded_output.json'

# Get information (-u to get gmt time)
#hour_run=00
time_now=$(date -u +"%Y-%m-%d %H:00")
time_now_folder=$(date -u +"/%Y/%m/%d")
#time_now='2021-03-24 00:00' # DEBUG
#time_now_folder='/2021/03/24' # DEBUG

# Get lock information
file_lock_start_raw='igad_lock_mosaic_output_%YYYY%MM%DD_%HH_START.txt'
file_lock_end_raw='igad_lock_mosaic_output_%YYYY%MM%DD_%HH_END.txt'

file_lock_init=false
folder_lock_raw=$lock_folder'postprocessing/'

# Out folder information
out_folder_step=${out_folder}${time_now_folder}
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Activate virtualenv
export PATH=$virtualenv_folder/bin:$PATH
source activate $virtualenv_name

# Add path to pythonpath
export PYTHONPATH="${PYTHONPATH}:$script_folder"

#-----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Get time information
year=${time_now:0:4}
month=${time_now:5:2}
day=${time_now:8:2}
hour=${time_now:11:2}

# Define path data
folder_lock_def=${folder_lock_raw/"%YYYY"/$year}
folder_lock_def=${folder_lock_def/"%MM"/$month}
folder_lock_def=${folder_lock_def/"%DD"/$day}

file_lock_start_def=${file_lock_start_raw/"%YYYY"/$year}
file_lock_start_def=${file_lock_start_def/"%MM"/$month}
file_lock_start_def=${file_lock_start_def/"%DD"/$day}
file_lock_start_def=${file_lock_start_def/"%HH"/$hour}

file_lock_end_def=${file_lock_end_raw/"%YYYY"/$year}
file_lock_end_def=${file_lock_end_def/"%MM"/$month}
file_lock_end_def=${file_lock_end_def/"%DD"/$day}
file_lock_end_def=${file_lock_end_def/"%HH"/$hour}

# Create folder(s)
if [ ! -d "$folder_lock_def" ]; then
	mkdir -p $folder_lock_def
fi
# ----------------------------------------------------------------------------------------	

#-----------------------------------------------------------------------------------------
# Info script start
echo " ==================================================================================="
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> START ..."
echo " ==> COMMAND LINE: " python3 $script_file -settings_file $settings_file -time $time_now

# Execution pid
execution_pid=$$

#-----------------------------------------------------------------------------------------
# File lock definition
path_file_lock_def_start=$folder_lock_def/$file_lock_start_def 
path_file_lock_def_end=$folder_lock_def/$file_lock_end_def
   
# Init lock conditions
echo " ====> INITILIZE LOCK FILES ... "
if $file_lock_init; then
    # Delete lock files
    if [ -f "$path_file_lock_def_start" ]; then
       rm "$path_file_lock_def_start"
    fi
    if [ -f "$path_file_lock_def_end" ]; then
       rm "$path_file_lock_def_end"
    fi
    echo " ====> INITILIZE LOCK FILES ... DONE!"
else
    echo " ====> INITILIZE LOCK FILES ... SKIPPED!"
fi
#-----------------------------------------------------------------------------------------  

#-----------------------------------------------------------------------------------------
# Run check
if [ -f $path_file_lock_def_start ] && [ -f $path_file_lock_def_end ]; then   

    #-----------------------------------------------------------------------------------------
    # Process completed
    echo " ===> EXECUTION ... SKIPPED! ALL DATA WERE PROCESSED DURING A PREVIOUSLY RUN"
    #-----------------------------------------------------------------------------------------

elif [ -f $path_file_lock_def_start ] && [ ! -f $path_file_lock_def_end ]; then
        
    #-----------------------------------------------------------------------------------------
    # Process running condition
    echo " ===> EXECUTION ... SKIPPED! SCRIPT IS STILL RUNNING ... WAIT FOR PROCESS END"
    #-----------------------------------------------------------------------------------------

elif [ ! -f $path_file_lock_def_start ] && [ ! -f $path_file_lock_def_end ]; then

    #-----------------------------------------------------------------------------------------
    # Lock File START
    time_step=$(date +"%Y-%m-%d %H:%S")
    echo " ================================ " >> $path_file_lock_def_start
    echo " ==== EXECUTION START REPORT ==== " >> $path_file_lock_def_start
    echo " "
    echo " ==== PID:" $execution_pid >> $path_file_lock_def_start
    echo " ==== Algorithm: $script_name" >> $path_file_lock_def_start
    echo " ==== RunTime: $time_step" >> $path_file_lock_def_start
    echo " ==== ExecutionTime: $time_now" >> $path_file_lock_def_start
    echo " ==== Status: RUNNING" >> $path_file_lock_def_start
    echo " "
    echo " ================================ " >> $path_file_lock_def_start

    # Run python script (using setting and time)
    python3 $script_file -settings_file $settings_file -time "$time_now" || { rm $path_file_lock_def_start ; echo " ===> EXECUTION ... FAILED" ; exit 1; } 
    
    # Lock File END
    time_step=$(date +"%Y-%m-%d %H:%S")
    echo " ============================== " >> $path_file_lock_def_end
    echo " ==== EXECUTION END REPORT ==== " >> $path_file_lock_def_end
    echo " "
    echo " ==== PID:" $execution_pid >> $path_file_lock_def_start
    echo " ==== Algorithm: $script_name" >> $path_file_lock_def_end
    echo " ==== RunTime: $time_step" >> $path_file_lock_def_end
    echo " ==== ExecutionTime: $time_now" >> $path_file_lock_def_end
    echo " ==== Status: COMPLETED" >>  $path_file_lock_def_end
    echo " "
    echo " ============================== " >> $path_file_lock_def_end
        
    # Info script end
    echo " ===> EXECUTION ... DONE"
    
else
        
    #-----------------------------------------------------------------------------------------
    # Exit unexpected mode
    echo " ===> EXECUTION ... FAILED! SCRIPT ENDED FOR UNKNOWN LOCK FILES CONDITION!"
    #-----------------------------------------------------------------------------------------
        
fi
#-----------------------------------------------------------------------------------------

# Info script end
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> ... END"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------

