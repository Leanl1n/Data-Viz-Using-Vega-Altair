"""Streamlit UI components for data overview and airline analysis."""

import numpy as np
import pandas as pd
import streamlit as st

from .chart_creator import ChartCreator
from .constants import COLUMN_RATIO, DATAFRAME_DISPLAY_WIDTH
from .reader.excel_handler import ExcelFileHandler
from .utils.helpers import format_number


def display_airline_metrics(
    handler: ExcelFileHandler,
    keyword: str,
    secondary_keyword: str,
) -> None:
    """Render metrics (coverage, headline presence, reach, AVE) for one airline."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            f"Media Coverage Volume {keyword}",
            handler.get_total_articles_keywords(keyword),
        )
    with col2:
        st.metric(
            f"Headline Presence {keyword}",
            handler.count_mentions_headlines(keyword, secondary_keyword),
        )
    with col3:
        st.metric(
            f"{keyword} Reach Metrics",
            format_number(handler.get_reach_sum(keyword)),
        )
    with col4:
        st.metric(
            f"{keyword} AVE Metrics",
            format_number(handler.get_ave_sum(keyword)),
        )


def display_sentiment_analysis(handler: ExcelFileHandler, keyword: str) -> None:
    """Render sentiment counts and pie chart for one keyword."""
    st.subheader("Sentiment Analysis")
    counts = handler.get_sentiment_counts(keyword)
    sentiment_df = pd.DataFrame(
        {
            "Sentiment": ["Positive", "Neutral", "Negative"],
            "Count": [counts["Positive"], counts["Neutral"], counts["Negative"]],
        }
    )
    col1, col2 = st.columns(COLUMN_RATIO)
    with col1:
        st.dataframe(sentiment_df, hide_index=True, width=DATAFRAME_DISPLAY_WIDTH)
    with col2:
        chart = ChartCreator.create_sentiment_pie_chart(
            [counts["Positive"], counts["Neutral"], counts["Negative"]]
        )
        st.altair_chart(chart, use_container_width=True, theme=None)


def display_daily_trendline(
    handler: ExcelFileHandler, keyword: str, color_key: str
) -> None:
    """Render daily trendline with slider (time window), smoothing, and trend line."""
    st.subheader("Daily Trendline")
    daily = handler.count_daily_trendline(keyword)
    n_total = len(daily)
    if n_total == 0:
        st.warning("No daily data for this keyword.")
        return

    key_suffix = keyword.replace(" ", "_").replace(".", "_") if keyword else "trend"
    with st.expander("Trendline controls", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            window_options = [
                ("All", n_total),
                ("Last 30 days", min(30, n_total)),
                ("Last 14 days", min(14, n_total)),
                ("Last 7 days", min(7, n_total)),
            ]
            window_labels = [label for label, n in window_options]
            window_idx = st.selectbox(
                "Time window",
                range(len(window_options)),
                format_func=lambda i: window_labels[i],
                help="Limit the range of dates shown on the chart.",
                key=f"trendline_window_{key_suffix}",
            )
            n_show = window_options[window_idx][1]
        with c2:
            smooth_options = ["None", "3-day rolling average", "7-day rolling average"]
            smooth_choice = st.selectbox(
                "Smoothing",
                smooth_options,
                help="Overlay a moving average to reduce noise.",
                key=f"trendline_smooth_{key_suffix}",
            )
        with c3:
            show_trend = st.checkbox(
                "Show trend line (linear fit)",
                value=False,
                help="Display a linear regression trend line.",
                key=f"trendline_show_trend_{key_suffix}",
            )

    # Apply time window (last n points)
    daily_view = daily.tail(n_show).reset_index(drop=True)
    smoothed_series = None
    trend_series = None

    if smooth_choice == "3-day rolling average":
        window = 3
        s = daily["Count"].rolling(window=window, min_periods=1).mean()
        smoothed_series = s.tail(n_show).reset_index(drop=True)
    elif smooth_choice == "7-day rolling average":
        window = 7
        s = daily["Count"].rolling(window=window, min_periods=1).mean()
        smoothed_series = s.tail(n_show).reset_index(drop=True)

    if show_trend and len(daily_view) >= 2:
        x = np.arange(len(daily_view))
        y = daily_view["Count"].values
        coeffs = np.polyfit(x, y, 1)
        trend_series = pd.Series(np.polyval(coeffs, x))

    col1, col2 = st.columns(COLUMN_RATIO)
    with col1:
        st.caption("Data (filtered by time window)")
        st.dataframe(daily_view, hide_index=True, width=DATAFRAME_DISPLAY_WIDTH)
        if show_trend and trend_series is not None and len(daily_view) >= 2:
            slope = np.polyfit(np.arange(len(daily_view)), daily_view["Count"], 1)[0]
            st.caption(f"Trend slope: **{slope:+.2f}** articles/day")
    with col2:
        chart = ChartCreator.create_daily_trendline_chart(
            daily_view,
            color_key,
            smoothed_series=smoothed_series,
            trend_series=trend_series,
        )
        st.altair_chart(chart, use_container_width=True, theme=None)
        if smoothed_series is not None or trend_series is not None:
            parts = []
            if smoothed_series is not None:
                parts.append("Orange dashed: smoothing")
            if trend_series is not None:
                parts.append("Red dashed: linear trend")
            st.caption(" — ".join(parts))


def display_top_publications_authors(
    handler: ExcelFileHandler, keyword: str, color_key: str
) -> None:
    """Render top publications and top authors for one keyword."""
    st.subheader(f"{keyword} Top Publications")
    top_pub = handler.get_top_publications(keyword)
    col1, col2 = st.columns(COLUMN_RATIO)
    with col1:
        st.dataframe(top_pub, hide_index=True, width=DATAFRAME_DISPLAY_WIDTH)
    with col2:
        st.altair_chart(
            ChartCreator.create_publications_horizontal_bar(top_pub, color_key),
            use_container_width=True,
            theme=None,
        )
    st.subheader(f"{keyword} Top Authors")
    top_auth = handler.get_top_authors(keyword)
    col1, col2 = st.columns(COLUMN_RATIO)
    with col1:
        st.dataframe(top_auth, hide_index=True, width=DATAFRAME_DISPLAY_WIDTH)
    with col2:
        st.altair_chart(
            ChartCreator.create_get_top_authors(top_auth, color_key),
            use_container_width=True,
            theme=None,
        )


def display_brand_comparison(
    handler: ExcelFileHandler, airlines: list[str]
) -> None:
    """Render brand comparison table and pie chart."""
    st.subheader("Brand Comparison")
    mentions = [handler.get_total_articles_keywords(kw) for kw in airlines]
    df = pd.DataFrame({"Airline": airlines, "Mentions": mentions})
    col1, col2 = st.columns(COLUMN_RATIO)
    with col1:
        st.dataframe(df, hide_index=True, width=DATAFRAME_DISPLAY_WIDTH)
    with col2:
        chart = ChartCreator.create_airline_mentions_pie_chart(mentions, airlines)
        st.altair_chart(chart, use_container_width=True, theme=None)


def display_pie_to_pie_analysis(
    handler: ExcelFileHandler, overview_keywords: list[str]
) -> None:
    """Render summary table and side-by-side airline/sentiment pie charts."""
    st.subheader("Pie to Pie Analysis")
    summary_df = handler.create_summary_dataframe(overview_keywords)
    values = summary_df["Value"].tolist()
    airline_data = values[:3]
    sentiment_data = values
    col1, col2 = st.columns(COLUMN_RATIO)
    with col1:
        st.dataframe(summary_df, hide_index=True, width=DATAFRAME_DISPLAY_WIDTH)
    with col2:
        fig = ChartCreator.create_side_by_side_pie_charts(
            airline_data, sentiment_data, overview_keywords[:3]
        )
        st.pyplot(fig)


def display_airlines_overview(
    handler: ExcelFileHandler, overview_keywords: list[str]
) -> None:
    """Render sentiment overview table and stacked bar chart."""
    st.subheader("Airlines Sentiment Overview")
    sentiment_df = handler.sentiment_overview(overview_keywords)
    col1, col2 = st.columns(COLUMN_RATIO)
    with col1:
        st.dataframe(sentiment_df, hide_index=True, width=DATAFRAME_DISPLAY_WIDTH)
    with col2:
        chart = ChartCreator.create_airlines_sentiment_overview(
            sentiment_df, keyword_order=overview_keywords[:3]
        )
        st.altair_chart(chart, use_container_width=True, theme=None)


def display_prominence_score_df(
    handler: ExcelFileHandler,
    keyword_groups: list[list[str] | tuple[str, ...]],
) -> None:
    """Render prominence score table for multiple keyword groups (article-level detail)."""
    df = handler.prominence_score(keyword_groups[0], *keyword_groups[1:])
    if df.empty:
        st.caption("No prominence score data.")
        return
    with st.expander("Article-level prominence scores (detail)", expanded=False):
        st.caption("One row per article with prominence score per keyword set.")
        st.dataframe(df, hide_index=True)


def display_prominence_score_extra(
    handler: ExcelFileHandler,
    keyword_groups: list[list[str] | tuple[str, ...]],
) -> None:
    """Render prominence totals/averages and chart for keyword groups."""
    st.subheader("Prominence Summary")
    col1, col2 = st.columns(COLUMN_RATIO)
    with col1:
        extra = handler.prominence_score_extra(keyword_groups[0], *keyword_groups[1:])
        st.dataframe(extra, hide_index=True, width=DATAFRAME_DISPLAY_WIDTH)
    with col2:
        chart = ChartCreator.create_prominence_score_chart_extra(extra)
        st.altair_chart(chart, use_container_width=True, theme=None)
