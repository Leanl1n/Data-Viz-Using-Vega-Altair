"""Load configuration from JSON."""

import json
import os
from typing import Any

from ..constants import CONFIG_PATH


def load_config(config_path: str | None = None) -> dict[str, Any]:
    """Load the configuration file and return the config dictionary."""
    path = config_path or CONFIG_PATH
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_keywords() -> list[str]:
    """Return the list of keywords from the config file."""
    config = load_config()
    return config.get("keywords", [])


def get_keyword_media() -> dict[str, Any]:
    """Return the mapping of keywords to media sources."""
    config = load_config()
    return config.get("media_types", {})


def get_keyword_media_sites() -> list[str]:
    """Return the list of media types (e.g. blog, broadcast, social media, print)."""
    default_sites = ["blog", "broadcast", "social media", "print"]
    config = load_config()
    config_sites = list(config.get("media_types", {}).keys())
    return list(set(default_sites + config_sites))


def get_sites_by_type(media_type: str) -> list[str]:
    """Return the list of sites for the given media type."""
    config = load_config()
    return config.get("media_types", {}).get(media_type, [])
