# Global setting to check this works locally and change the flag to make it work in a CDE Cluster
import dynamic_pkgloader
import configparser
import os
import sys


def print_config_contents(config_file_path='config.ini'):
    """
    Load and print the contents of a configuration file.

    Args:
    - config_file_path (str): The path to the configuration file.

    Returns:
    - None
    """
    # Check if the file exists at the specified path
    if not os.path.exists(config_file_path):
        print(f"Error: Configuration file '{config_file_path}' not found.")
        return

    # Initialize the ConfigParser
    config = configparser.ConfigParser()

    try:
        # Read the configuration file
        config.read(config_file_path)

        # Print all sections and their key-value pairs
        print(f"Contents of '{config_file_path}':")
        for section in config.sections():
            print(f"[{section}]")
            for key, value in config.items(section):
                print(f"{key} = {value}")
            print()  # Print a blank line between sections

    except Exception as e:
        print(f"Error: Failed to read the configuration file '{config_file_path}'.")
        print(f"Exception: {e}")


def test_example_add_one():
    """
    Loads the packages and the submodules in the config.in file in this Python file 

    Args:
    - None

    Returns:
    - None
    """
    # we assume a default config file is present in the local folder, if not then pass it as an argument when calling this python file
    config_file = "config.ini"

    # Check if a command line argument is provided with the python file
    if len(sys.argv) > 1:
        # Load packages from configuration and ensure they are injected correctly
        print(f"Argument passed to this job should be the path of config file  : {sys.argv[1]}")
        config_file = sys.argv[1]
                               
    print_config_contents(config_file)
    
    dynamic_pkgloader.load_packages(config_file=config_file) #

    # Example usage  of the newly loaded package
    try:
        # We access the newly loaded package using our using From <package name> import <submodule> format. 
        # Both package name and submodule name is to be added in the config.ini file
        from example_package_superellipse import example
        if hasattr(example, 'add_one'):
            result = example.add_one(5)
            print(f"example.add_one(5): {result}")
        else:
            print("Function 'add_three' not found in 'example' module.")
    except ImportError as e:
        print(f"Import error: {e}")

if __name__ == "__main__":
    test_example_add_one()
