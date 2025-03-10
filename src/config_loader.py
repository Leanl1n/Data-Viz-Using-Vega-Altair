import json

def load_config(config_path="config.json"):
    """Loads the configuration file and returns the config dictionary."""
    with open(config_path, "r") as f:
        return json.load(f)

def get_keywords():
    """Returns a list of keywords from the config file."""
    config = load_config()
    return config.get("keywords", [])  # Returns an empty list if 'keywords' is missing