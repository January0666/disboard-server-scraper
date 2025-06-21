import json


def load_config(file_path: str = "data/input/config.json"):
    """
    Load configuration from a JSON file.
    :param file_path: Path to the JSON configuration file.
    :return: Dictionary containing the configuration.
    """
    try:
        with open(file_path, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Configuration file {file_path} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the configuration file {file_path}.")
        return {}
