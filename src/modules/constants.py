"""Application constants: paths, sheet names, column names, colors, and UI copy."""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_FILENAME = "config.json"
DEFAULT_DATA_DIR = "data"
DEFAULT_DATA_FILENAME = "PAL Excel Template (initial draft ver 1.0).xlsx"
DEFAULT_DATA_PATH = os.path.join(PROJECT_ROOT, DEFAULT_DATA_DIR, DEFAULT_DATA_FILENAME)
DEFAULT_SHEET_NAME = "1. Dataset"

UPLOAD_FILE_TYPES = ["xlsx", "xls"]

COLUMN_KEYWORDS = "Keywords"
COLUMN_HEADLINE = "Headline"
COLUMN_DATE = "Date"
COLUMN_SENTIMENT = "Sentiment"
COLUMN_REACH = "Reach"
COLUMN_AVE = "AVE"
COLUMN_SOURCE = "Source"
COLUMN_INFLUENCER = "Influencer"
COLUMN_OPENING_TEXT = "Opening Text"
COLUMN_HIT_SENTENCE = "Hit Sentence"

DATE_FORMAT_READ = "%d-%b-%Y %I:%M%p"
DATE_FORMAT_DISPLAY_TREND = "%b-%d"
DATE_FORMAT_DISPLAY_PROMINENCE = "%Y-%m-%d"

SENTIMENT_VALUES = ("Positive", "Neutral", "Negative")

COLOR_KEYWORD_1 = "#001F60"
COLOR_KEYWORD_3 = "#039482"
COLOR_KEYWORD_4 = "#ff0000"
COLOR_MAPPING = {
    "selected_keyword1_color": COLOR_KEYWORD_1,
    "selected_keyword3_color": COLOR_KEYWORD_3,
    "selected_keyword4_color": COLOR_KEYWORD_4,
}

PIE_AIRLINE_COLORS = [COLOR_KEYWORD_1, "#FFD700", "#EE2A29"]
PIE_SENTIMENT_COLORS = ["#2ecc71", "#95a5a6", "#e74c3c"]
PIE_SENTIMENT_COLORS_MATPLOTLIB = ["#3b7d23", "#7f7f7f", "#c00000"]

REQUIRED_FIELDS_NOTE = """
**Required columns in your Excel (sheet \"1. Dataset\") for the analysis to work:**
- **Keywords** — terms/brands (e.g. airline names)
- **Headline** — article headline
- **Date** — e.g. `DD-Mon-YYYY HH:MMam/pm`
- **Sentiment** — one of: Positive, Neutral, Negative
- **Reach** — numeric
- **AVE** — advertising value equivalent (numeric)
- **Source** — publication/source name
- **Influencer** — author/influencer name
- **Opening Text** — first part of article text
- **Hit Sentence** — quoted or key sentence
""".strip()

DATAFRAME_DISPLAY_WIDTH = 400
CHART_HEIGHT = 300
COLUMN_RATIO = [1, 2]
