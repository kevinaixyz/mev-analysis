import yaml
import logging
import configparser

def load_config(file_path):
    """
    Load a YAML configuration file.

    Args:
        file_path (str): The path to the YAML file.

    Returns:
        dict: The loaded configuration as a dictionary.
    """
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_logger():
    logging.basicConfig(
        level=logging.DEBUG,  # Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s - %(levelname)s - %(message)s',  # Set the log message format
        filename='app.log',  # Specify the log file name
        filemode='w'  # Set the file mode (w for write, a for append)
    )

    # Define a logger
    logger = logging.getLogger('app')
    return logger

def get_key(section, option):
    keys_config = configparser.ConfigParser()

    # Read the configuration from the file
    keys_config.read('keys.ini')

    # Access values from the configuration
    value = keys_config.get(section, option)
    return value

config = load_config('./config.yml')
logger = get_logger()