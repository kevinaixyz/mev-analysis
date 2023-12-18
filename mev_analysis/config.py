import yaml
import logging
import configparser
from pathlib import Path


def load_config():
    """
    Load a YAML configuration file.

    Args:
        file_path (str): The path to the YAML file.

    Returns:
        dict: The loaded configuration as a dictionary.
    """
    abs_path = Path(__file__).parent
    file_path = abs_path / 'config.yml'
    with file_path.open('r') as file:
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


def load_keys():
    keys_config = configparser.ConfigParser()
    parent_path = Path(__file__).parent
    file_path = parent_path / 'keys.ini'
    # Read the configuration from the file
    keys_config.read(file_path)
    return keys_config


def get_key(section, option):
    # Access values from the configuration
    return keys_config.get(section, option)


config = load_config()
keys_config = load_keys()
logger = get_logger()
