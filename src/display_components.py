import streamlit as st
import pandas as pd
from chart_creator import ChartCreator
from utils import helpers

# Add constants for consistent sizing at the top of the file
DATAFRAME_WIDTH = 400
CHART_HEIGHT = 300
COLUMN_RATIO = [1, 2]  # 1:2 ratio for dataframe:chart

def display_airline_metrics(handler, keyword, secondary_keyword):
    """Display metrics for an airline in a 4-column layout"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_articles = handler.get_total_articles_keywords(keyword)
        st.metric(f"Media Coverage Volume {keyword}", total_articles)
    
    with col2:
        headline_mentions = handler.count_mentions_headlines(keyword, secondary_keyword)
        st.metric(f"Headline Presence {keyword}", headline_mentions)
    
    with col3:
        total_reach = handler.get_reach_sum(keyword)
        st.metric(f"{keyword} Reach Metrics", helpers.format_number(total_reach))
    
    with col4:
        total_ave = handler.get_ave_sum(keyword)
        st.metric(f"{keyword} AVE Metrics", helpers.format_number(total_ave))

def display_sentiment_analysis(handler, keyword):
    """Display sentiment analysis for an airline"""
    st.subheader("Sentiment Analysis")
    
    sentiment_counts = handler.get_sentiment_counts(keyword)
    sentiment_df = pd.DataFrame({
        'Sentiment': ['Positive', 'Neutral', 'Negative'],
        'Count': [
            sentiment_counts['Positive'],
            sentiment_counts['Neutral'],
            sentiment_counts['Negative']
        ]
    })
    
    col1, col2 = st.columns(COLUMN_RATIO)
    
    with col1:
        st.dataframe(sentiment_df, hide_index=True, width=DATAFRAME_WIDTH)
    
    with col2:
        chart_sentiment = ChartCreator.create_sentiment_pie_chart([
            sentiment_counts['Positive'],
            sentiment_counts['Neutral'],
            sentiment_counts['Negative']
        ])
        st.altair_chart(chart_sentiment, use_container_width=True, theme=None)

def display_daily_trendline(handler, keyword, color_key):
    """Display daily trendline data and chart"""
    st.subheader("Daily Trendline")
    
    daily_data = handler.count_daily_trendline(keyword)
    col1, col2 = st.columns(COLUMN_RATIO)
    
    with col1:
        st.dataframe(daily_data, hide_index=True, width=DATAFRAME_WIDTH)
    
    with col2:
        chart_trendline = ChartCreator.create_daily_trendline_chart(daily_data, color_key)
        st.altair_chart(chart_trendline, use_container_width=True, theme=None)

def display_top_publications_authors(handler, keyword, color_key):
    """Display top publications and authors for an airline"""
    # Publications section
    st.subheader(f"{keyword} Top Publications")
    top_publications = handler.get_top_publications(keyword)
    
    col1, col2 = st.columns(COLUMN_RATIO)
    
    with col1:
        st.dataframe(top_publications, hide_index=True, width=DATAFRAME_WIDTH)
    
    with col2:
        publications_chart = ChartCreator.create_publications_horizontal_bar(top_publications, color_key)
        st.altair_chart(publications_chart, use_container_width=True, theme=None)
    
    # Authors section
    st.subheader(f"{keyword} Top Authors")
    top_authors = handler.get_top_authors(keyword)
    
    col1, col2 = st.columns(COLUMN_RATIO)
    
    with col1:
        st.dataframe(top_authors, hide_index=True, width=DATAFRAME_WIDTH)
    
    with col2:
        authors_chart = ChartCreator.create_get_top_authors(top_authors, color_key)
        st.altair_chart(authors_chart, use_container_width=True, theme=None)

def display_brand_comparison(handler, airlines):
    """Display brand comparison data and charts"""
    st.subheader("Brand Comparison")
    
    airline_mentions = [handler.get_total_articles_keywords(kw) for kw in airlines]
    airline_df = pd.DataFrame({
        'Airline': airlines,
        'Mentions': airline_mentions
    })
    
    col1, col2 = st.columns(COLUMN_RATIO)
    
    with col1:
        st.dataframe(airline_df, hide_index=True, width=DATAFRAME_WIDTH)
    
    with col2:
        chart_airlines = ChartCreator.create_airline_mentions_pie_chart(airline_mentions)
        st.altair_chart(chart_airlines, use_container_width=True, theme=None)

def display_pie_to_pie_analysis(handler):
    """Display pie to pie analysis"""
    st.subheader("Pie to Pie Analysis")
    
    summary_df = handler.create_summary_dataframe()
    airline_data = summary_df['Value'][:3].tolist()
    sentiment_data = summary_df['Value'].tolist()
    
    col1, col2 = st.columns(COLUMN_RATIO)
    
    with col1:
        st.dataframe(summary_df, hide_index=True, width=DATAFRAME_WIDTH)
    
    with col2:
        fig_side_by_side = ChartCreator.create_side_by_side_pie_charts(airline_data, sentiment_data)
        st.pyplot(fig_side_by_side)

def display_airlines_overview(handler):
    """Display airlines sentiment overview"""
    st.subheader("Airlines Sentiment Overview")
    sentiment_overview = handler.sentiment_overview()
    
    col1, col2 = st.columns(COLUMN_RATIO)
    
    with col1:
        st.dataframe(sentiment_overview, hide_index=True, width=DATAFRAME_WIDTH)
    
    with col2:
        overview_chart = ChartCreator.create_airlines_sentiment_overview(sentiment_overview)
        st.altair_chart(overview_chart, use_container_width=True, theme=None)

def display_prominence_score_df(handler, keyword):
    """
    Display prominence score data and chart
    Args:
        handler: ExcelFileHandler instance
        keyword: Primary keyword to analyze
        secondary_keyword: Secondary keyword (alias) to include
    """
    st.subheader("Prominence Score Analysis")
    
    # Get prominence score data with both keywords
    prominence_df = handler.prominence_score(keyword)
    
    col1, col2 = st.columns(COLUMN_RATIO)
    
    with col1:
        st.dataframe(prominence_df, hide_index=True, width=DATAFRAME_WIDTH)
        
    with col2:
        prominence_chart = ChartCreator.create_prominence_score_chart(prominence_df)
        st.altair_chart(prominence_chart, use_container_width=True, theme=None)