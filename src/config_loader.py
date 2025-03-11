import json

def load_config(config_path="config.json"):
    """Loads the configuration file and returns the config dictionary."""
    with open(config_path, "r") as f:
        return json.load(f)

def get_keywords():
    """Returns a list of keywords from the config file."""
    config = load_config()
    return config.get("keywords", [])  # Returns an empty list if 'keywords' is missing

def get_keyword_media():
    """Returns a dictionary of keywords and their respective media sources."""
    config = load_config()
    return config.get("media_types", {})  # Returns an empty dictionary if 'keyword_media' is missing

def get_keyword_media_sites():
    """Returns a list of media types in lowercase: blog, broadcast, social media, and print."""
    default_sites = ["blog", "broadcast", "social media", "print"]
    config = load_config()
    config_sites = list(config.get("media_types", {}).keys())  # Extract only the keys
    return list(set(default_sites + config_sites))  # Remove duplicates

def get_sites_by_type(media_type):
    """
    Returns a list of sites for the specified media type from the config file.
    Args:
        media_type (str): The type of media (e.g., 'Blog', 'Broadcast', 'Social Media', 'Print')
    Returns:
        list: List of sites for the specified media type
    """
    config = load_config()
    return config.get("media_types", {}).get(media_type, [])

