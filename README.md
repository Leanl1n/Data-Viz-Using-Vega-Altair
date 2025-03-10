# Streamlit Data Visualization Project

This project is a Streamlit application designed to visualize data related to Philippine Airlines mentions in media coverage. It processes data from an Excel file and generates various charts to provide insights into brand volume and sentiment analysis.

## Project Structure

```
streamlit-data-viz
├── src
│   ├── app.py               # Main entry point for the Streamlit application
│   ├── chart_creator.py     # Contains the ChartCreator class for generating charts
│   ├── excel_handler.py     # Contains the ExcelFileHandler class for processing Excel data
│   └── utils
│       └── helpers.py       # Utility functions for data processing and formatting
├── data
│   └── PAL Excel Template (initial draft ver 1.0).xlsx  # Excel file with data
├── requirements.txt         # Python dependencies for the project
└── README.md                # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd streamlit-data-viz
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```
   streamlit run src/app.py
   ```

## Usage

Once the application is running, you will be able to:

- View the total number of articles related to Philippine Airlines.
- See the breakdown of mentions for Philippine Airlines, Cebu Pacific, and AirAsia Philippines.
- Analyze sentiment distribution (Positive, Neutral, Negative).
- Visualize daily trends in mentions over time.
- Interact with various charts generated from the data.

## Dependencies

This project requires the following Python packages:

- Streamlit
- Pandas
- NumPy
- Matplotlib

Make sure to install these packages using the `requirements.txt` file provided.

## License

PROVIDED BY: Learning and Development Team -- RDB
