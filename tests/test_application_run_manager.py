'''
Tests for the application run manager
Created on Mon Jul  6 12:49:07 2015
'''

# -------------------------------------------------------------------------------------
# Libraries
import os
import git
import pytest

from apps import HMC_Model_RUN_Manager

# Test attribute(s)
repository_root = 'https://github.com/c-hydro/'
repository_folder = 'hmc-datasets'
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Application test for Africa/Zambia case study
@pytest.mark.run_manager_africa_zambia
def test_application_run_manager_africa_zambia(app_folder_name):
    """
    Test application framework with af2400 datasets for Africa Zambia domain
    """

    # Repository information
    repository_case = 'Africa_AF2400'

    # Application argument(s)
    settings_algorithm = 'hmc_configuration_algorithm_dev_AF2400.json'
    settings_datasets = 'hmc_configuration_datasets_dev_AF2400.json'
    settings_time = '2051-01-31 12:00'

    # Define configuration path(s)
    settings_algorithm = search_file(app_folder_name, settings_algorithm)
    settings_datasets = search_file(app_folder_name, settings_datasets)

    # Open application instance
    HMC_Model_RUN_Manager.main(settings_algorithm, settings_datasets, settings_time)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Application test for Italy/Marche case study
@pytest.mark.run_manager_italy_marche
def test_application_run_manager_italy_marche(app_folder_name):
    """
    Test application framework with Marche datasets for Italy/Marche domain
    """


    # Application argument(s)
    settings_algorithm = 'hmc_configuration_algorithm_dev_RegMarche.json'
    settings_datasets = 'hmc_configuration_datasets_dev_RegMarche.json'
    settings_time = '2016-10-20 09:23'

    # Get application path
    app_file_path = os.path.abspath(HMC_Model_RUN_Manager.__file__)
    app_folder_name, app_file_name = os.path.split(app_file_path)

    # Define configuration path(s)
    settings_algorithm = search_file(app_folder_name, settings_algorithm)
    settings_datasets = search_file(app_folder_name, settings_datasets)

    # Open application instance
    HMC_Model_RUN_Manager.main(settings_algorithm, settings_datasets, settings_time)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to search file in sub-folders
def search_file(src_path, file_name, file_format='.json'):
    for path_name_list, _, file_name_list in os.walk(src_path):
        for file_name_tmp in file_name_list:
            if file_name == file_name_tmp:
                if file_name_tmp.endswith(file_format):
                    return os.path.join(path_name_list, file_name)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Main configuration
if __name__ == "__main__":

    print(" *** Running test for HMC application manager ... ***")

    # Define repository address
    repository_address = os.path.join(repository_root, repository_folder)

    # Get application path
    app_file_path = os.path.abspath(HMC_Model_RUN_Manager.__file__)
    app_folder_name, app_file_name = os.path.split(app_file_path)

    # Download datasets
    if not os.path.exists(os.path.join(app_folder_name, repository_folder)):
        git.Repo.clone_from(repository_address, os.path.join(app_folder_name, repository_folder), branch='master')

    # Test 1: Africa/Zambia
    test_application_run_manager_africa_zambia(app_folder_name)
    # Test 2: Italy/Marche
    test_application_run_manager_italy_marche(app_folder_name)

    print(" *** Running test for HMC application manager ... DONE. Everything PASSED ***")

# -------------------------------------------------------------------------------------
