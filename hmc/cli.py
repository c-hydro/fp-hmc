# ----------------------------------------------------------------------------
# Libraries
import argparse
from apps import HMC_Model_RUN_Manager
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Method to parse argument(s)
def create_parser(subparsers):
    create = subparsers.add_parser('create', help='Create new configuration files for a WRF run')
    create.add_argument(
        '-settings_algorithm', default='configuration_algorithm.json',
        help='Name of the settings algorithm file in json format')
    create.add_argument(
        '-settings_datasets', default='configuration_datasets.json',
        help='Name of the settings datasets file in json format')
    create.add_argument(
        '-time', default=None,
        help='Time of the simulation in YYYY-MM-DD HH:MM format')
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Method to run application
def run_command(args):
    if args.cmd == 'create':
        HMC_Model_RUN_Manager(args.input, args.namelist, args.wps)
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Main script
def main():
    parser = argparse.ArgumentParser(prog='hmc', description="Create an instance of HMC application")
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    create_parser(subparsers)

    args = parser.parse_args()
    run_command(args)
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Call script from external library
if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------------
