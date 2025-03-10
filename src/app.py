import streamlit as st
from excel_handler import ExcelFileHandler
from config_loader import get_keywords
from display_components import (
    display_airline_metrics,
    display_sentiment_analysis,
    display_daily_trendline,
    display_top_publications_authors,
    display_brand_comparison,
    display_pie_to_pie_analysis,
    display_airlines_overview,
    display_prominence_score_df
)

# Load keywords
keyword_list = get_keywords()

# Initialize keywords
selected_keyword1 = keyword_list[0] if len(keyword_list) > 0 else None  # Philippine Airlines
selected_keyword2 = keyword_list[1] if len(keyword_list) > 1 else None  # PAL
selected_keyword3 = keyword_list[2] if len(keyword_list) > 2 else None  # Cebu Pacific
selected_keyword4 = keyword_list[3] if len(keyword_list) > 3 else None  # AirAsia
selected_keyword5 = keyword_list[4] if len(keyword_list) > 4 else None  # CebPac
selected_keyword6 = keyword_list[5] if len(keyword_list) > 5 else None  # AirAsia
combined_keywords = [selected_keyword1, selected_keyword2]
combined_keywords1 = [selected_keyword3, selected_keyword5]

def display_general_overview(handler, df):
    """Display general data overview sections"""
    st.dataframe(df)
    
    # Overall Brand Comparison
    display_brand_comparison(handler, [selected_keyword1, selected_keyword3, selected_keyword4])
    
    # Overall Airlines Overview
    display_pie_to_pie_analysis(handler)
    
    # Overall Pie to Pie Analysis
    display_airlines_overview(handler)

    # Prominece Score
    display_prominence_score_df(handler, combined_keywords1)

def display_pal_analysis(handler):
    """Display Philippine Airlines specific analysis"""
    # PAL Metrics
    display_airline_metrics(handler, selected_keyword1, selected_keyword2)
    
    # PAL Sentiment Analysis
    display_sentiment_analysis(handler, selected_keyword1)
    
    # PAL Daily Trendline
    display_daily_trendline(handler, selected_keyword1, "selected_keyword1_color")
    
    # PAL Publications and Authors
    display_top_publications_authors(handler, selected_keyword1, "selected_keyword1_color")

def display_competitor_analysis(handler, competitor, sec_keyword, color_key):
    """Display analysis for competitor airlines"""
    # Competitor Metrics
    display_airline_metrics(handler, competitor, sec_keyword)
    
    # Competitor Sentiment Analysis
    display_sentiment_analysis(handler, competitor)

    # Competitor Daily Trendline
    display_daily_trendline(handler, competitor, color_key)

    # Competitor Publications and Authors
    display_top_publications_authors(handler, competitor, color_key)

def main():
    st.title("Data Visualization Guide")
    uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx', 'xls'])

    if uploaded_file is not None:
        try:
            handler = ExcelFileHandler(uploaded_file, "1. Dataset")
            df = handler.open_excel_file()

            # Create tabs
            tab_overview, tab_pal, tab_cebu, tab_airasia = st.tabs([
                "Overview", 
                "Philippine Airlines", 
                "Cebu Pacific", 
                "AirAsia"
            ])

            # Overview Tab
            with tab_overview:
                st.header("Data Overview")
                display_general_overview(handler, df)
            
            # Philippine Airlines Tab
            with tab_pal:
                st.header("Philippine Airlines Analysis")
                display_pal_analysis(handler)
            
            # Cebu Pacific Tab
            with tab_cebu:
                st.header("Cebu Pacific Analysis")
                display_competitor_analysis(
                    handler, 
                    selected_keyword3, 
                    selected_keyword5, 
                    "selected_keyword3_color"
                )
            
            # AirAsia Tab
            with tab_airasia:
                st.header("AirAsia Analysis")
                display_competitor_analysis(
                    handler, 
                    selected_keyword4, 
                    selected_keyword6, 
                    "selected_keyword4_color"
                )

        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.info("Please upload an Excel file to begin the analysis.")

if __name__ == "__main__":
    main()