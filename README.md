# Sample Dashboard using Streamlit and Vega Altair

A sample Streamlit dashboard for media coverage and sentiment analysis, with charts built using Vega Altair. Reads an Excel dataset and provides interactive views: brand comparison, sentiment breakdowns, daily trendlines, top publications and authors, and prominence scores.

## Project structure

```
Data-Viz-Using-Vega-Altair/
├── run.py                 # Entry point: run from project root
├── requirements.txt
├── data/
│   ├── config.json        # Keywords and optional media config
│   ├── dashboard.css      # Custom dashboard styles (optional)
│   ├── executive_summary.txt
│   └── PAL Excel Template (initial draft ver 1.0).xlsx
└── src/
    ├── app.py              # Streamlit UI and tab layout (only file at this level)
    └── modules/
        ├── constants.py    # Paths, sheet name, columns, colors, copy
        ├── chart_creator.py
        ├── display_components.py
        ├── reader/
        │   ├── __init__.py
        │   ├── config_loader.py
        │   └── excel_handler.py
        └── utils/
            ├── __init__.py
            └── helpers.py
```

## Setup

1. Clone the repo and go to the project root.
2. Create a virtual environment (recommended) and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure `data/config.json` exists (e.g. with a `keywords` list). Optionally place the default Excel file under `data/` as in the structure above.

## Run

From the project root:

```bash
python run.py
```

Or run Streamlit directly with `src` on `PYTHONPATH`:

```bash
PYTHONPATH=src streamlit run src/app.py
```

The app loads the default Excel file from `data/` if present. You can optionally upload another file via the UI; the tooltip on the uploader describes the required Excel columns and sheet name.

## Required Excel format

- **Sheet name:** `1. Dataset`
- **Columns:** Keywords, Headline, Date, Sentiment, Reach, AVE, Source, Influencer, Opening Text, Hit Sentence

See the in-app tooltip for details.

## Dependencies

- streamlit
- pandas, openpyxl
- altair, vega_datasets
- matplotlib
- numpy

## License

Provided by: Learning and Development Team — RDB
