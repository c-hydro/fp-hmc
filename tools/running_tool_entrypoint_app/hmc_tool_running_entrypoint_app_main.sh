#!/bin/bash -e

# ----------------------------------------------------------------------------------------
# Script information
script_name='HMC Entrypoint - App'
script_version='1.0.0'
script_date='2022/10/14'

# Argument(s) constants definition(s)
file_entrypoint_app_main_default='hmc_tool_running_entrypoint_app_main.py'
file_entrypoint_app_configuration_default='hmc_tool_running_entrypoint_app_configuration_hmc_generic.json'

# Virtualenv constants definition(s)
virtualenv_folder='/home/fabio/fp_system_conda/'
virtualenv_name='fp_system_conda_hmc_libraries'

# Default script folder
script_folder=$PWD

# Default filename(s)
path_entrypoint_app_main_default=$script_folder/$file_entrypoint_app_main_default
path_entrypoint_app_configuration_default=$script_folder/$file_entrypoint_app_configuration_default

# Set script Help messages
container_help_text="\
Usage of docker runner:
./fp-docker_entrypoint_app_interface.sh <options>
  	-h	display this help message;
	-m	filename of entrypoint app main;		
  	-c	filename of entrypoint app configuration;"
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

# Source profile environment(s)
set -e

if [ -t 0 ] ; then
	echo "(interactive shell)"
	source $HOME/.bashrc
else
	echo "(not interactive shell)"
	source $HOME/.profile
fi

# Check environment variable(s) to set entrypoint script
if [ -z ${APP_MAIN} ] ; then
	echo " ===> ENV variable \$APP_MAIN is empty"
	echo " ===> Script arguments or default arguments will be used." 
	parse_arg=true
else
	echo " ===> ENV variable \$APP_MAIN is defined"
	echo " ===> Script argument \$APP_MAIN = $APP_MAIN" 
	path_entrypoint_app_main=$APP_MAIN	
	parse_arg=false
fi

if [ -z ${APP_CONFIG} ] ; then
	echo " ===> ENV variable \$APP_CONFIG is empty"
	echo " ===> Script arguments or default arguments will be used." 
	parse_arg=true
else
	echo " ===> ENV variable \$APP_CONFIG is defined"
	echo " ===> Script argument \$APP_CONFIG = $APP_CONFIG" 
	path_entrypoint_app_configuration=$APP_CONFIG
	parse_arg=false
fi
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Define script option(s)
if "$parse_arg" ; then
	
	path_entrypoint_app_main=$path_entrypoint_app_main_default
	path_entrypoint_app_configuration=$path_entrypoint_app_configuration_default

	echo " ===> Get script arguments ... "
	while (( "$#" )); do
		
		echo $1
		echo $2

		case "$1" in
			
			-m) # filename of entrypoint app main
			  	path_entrypoint_app_main=$2
				shift 2
			  	;;
		  	-c) # filename of entrypoint app configuration
			  	path_entrypoint_app_configuration=$2	
				shift 2	
			  	;;
			*)  # exit message for unknown option
				echo " ===> ERROR: entrypoint app interface option $1 not recognized" 
				exit 1
				;;
		esac
	done
	echo " ===> Get script arguments ... OK"
else
	echo " ===> Get script arguments ... FROM ENV VARIABLES ... OK"
fi
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Check availability of file(s) 
echo " ===> Check entrypoint app main [$path_entrypoint_app_main] ... "
if [ -f $path_entrypoint_app_main ] ; then
	echo " ===> Check entrypoint app main ... OK"
else
	echo " ===> Check entrypoint app main ... FILE DOES NOT EXIST - FAILED" 
	exit 1
fi
echo " ===> Check entrypoint app configuration [$path_entrypoint_app_configuration] ... "
if [ -f $path_entrypoint_app_configuration ] ; then
	echo " ===> Check entrypoint app configuration ... OK"
else
	echo " ===> Check entrypoint app configuration ... FILE DOES NOT EXIST - FAILED" 
	exit 1
fi
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info 
echo echo " ===> ENTRYPOINT INTERFACE ... "

# Run interface application 
python $path_entrypoint_app_main -settings_file $path_entrypoint_app_configuration

echo echo " ===> ENTRYPOINT INTERFACE ... DONE"
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script end
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> ... END"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------
