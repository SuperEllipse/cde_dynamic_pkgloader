import importlib
import configparser
import subprocess
import sys
import traceback

    
def get_workload_config(config_file='config.ini'):
    """
    Retrieve the cluster configuration value and set it globally
    Args:
    - config_file (str): The path to the configuration file.

    Returns:
    - boolen: The cluster mode status TRUE if running on CDE or false if running locally
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    try:
        run_mode = config['Workload'].get('run_mode', 'local')
        return run_mode
    except KeyError as e:
        print(f"Error: Missing 'Workload' section in the config file. Exception: {e}")
        raise
    

def get_registry_url(config_file='config.ini'):
    """
    Retrieve the package registry URL from the configuration file.

    Args:
    - config_file (str): The path to the configuration file.

    Returns:
    - str: The package registry URL.
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    try:
        return config['Registry'].get('url', 'https://pypi.org/simple/')
    except KeyError as e:
        print(f"Error: Missing 'Registry' section or 'url' key in the config file. Exception: {e}")
        raise



def get_packages_info(config_file='config.ini'):
    """
    Get information about packages to be installed from the configuration file.

    Args:
    - config_file (str): The path to the configuration file.

    Returns:
    - dict: A dictionary where the key is the package name and the value
            is another dictionary containing 'version' and 'submodules'.
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    packages_info = {}
    for section in config.sections():
        if section not in ('Registry', 'Workload'):            
            version = config[section].get('version', 'latest')
            submodules = [sm.strip() for sm in config[section].get('submodules', '').split(',')]
            packages_info[section] = {'version': version, 'submodules': submodules}
    return packages_info

def install_and_import(package_name, version, index_url, run_mode):
    """
    Install the specified package and version using pip.

    Args:
    - package_name (str): The name of the package to install.
    - version (str): The version of the package to install.
    - index_url (str): The URL of the package registry.
    - run_mode (str): local or cde changes the target folder path because in cde we do not have access to the pythonic folders
    """
    if run_mode == "cde" : 
        pip_cmd = [sys.executable, '-m', 'pip', 'install', f'{package_name}=={version}', '--index-url', index_url, '--target', '/app/mount/custom_packages']
    else:  # you are running it locally doesnt require a "--target" , it can be installed in a virtual env    
        pip_cmd = [sys.executable, '-m', 'pip', 'install', f'{package_name}=={version}', '--index-url', index_url]

    try:
        subprocess.check_call(pip_cmd)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install {package_name}. Command: {pip_cmd}")
        print(f"Exception: {e}")
        raise

def import_submodules(package_name, submodules):
    """
    Import specified submodules of a package.

    Args:
    - package_name (str): The name of the main package.
    - submodules (list): A list of submodule names to import.

    Returns:
    - dict: A dictionary where the key is the submodule name and the value is the imported module.
    """
    imported_modules = {}
    for submodule in submodules:
        full_module_name = f"{package_name}.{submodule}"
        try:
            module = importlib.import_module(full_module_name)
            imported_modules[submodule] = module
            print(f"Imported submodule '{full_module_name}' successfully.")
        except ImportError as e:
            print(f"Failed to import submodule '{full_module_name}'.")
            print(f"Exception: {e}")
            traceback.print_exc()  # Print the stack trace
            raise
    return imported_modules

def load_packages(config_file='config.ini'):
    """
    Load and install packages as specified in the configuration file,
    and dynamically import their submodules into the global namespace.

    Args:
    - config_file (str): The path to the configuration file.

    Returns:
    - dict: A dictionary where the key is the main package name and the value
            is another dictionary containing its submodules.
    """
    all_imported_modules = {}
    run_mode="local" # we are running locally by default, change it in the config.ini to "cde" for executing in CDE
    try:
        # Get the package registry URL and package information
        registry_url = get_registry_url(config_file)
        run_mode = get_workload_config(config_file)
        # set the PYTHON path to the custom_packages folder in CDE. This folder must exist in CDE resources
        if run_mode == "cde": sys.path.insert(0, '/app/mount/custom_packages')
        
        packages_info = get_packages_info(config_file)

        # Install packages and import submodules
        for main_package, info in packages_info.items():
            package_version = info['version']
            submodules = info['submodules']
            install_and_import(main_package, package_version, registry_url, run_mode)
            imported_modules = import_submodules(main_package, submodules)
            all_imported_modules[main_package] = imported_modules

            # Inject submodules into the main package module
            main_package_module = importlib.import_module(main_package)
            for submodule_name, submodule in imported_modules.items():
                setattr(main_package_module, submodule_name, submodule)
                
    except Exception as e:
        print("An error occurred while loading packages.")
        print(f"Exception: {e}")
        traceback.print_exc()  # Print the stack trace for more details

    return all_imported_modules

