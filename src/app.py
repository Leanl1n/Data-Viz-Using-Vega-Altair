"""Streamlit app for media and sentiment data visualization."""

import os

import streamlit as st

from modules.constants import (
    DEFAULT_DATA_PATH,
    DEFAULT_SHEET_NAME,
    REQUIRED_FIELDS_NOTE,
    UPLOAD_FILE_TYPES,
)
from modules.display_components import (
    display_airline_metrics,
    display_airlines_overview,
    display_brand_comparison,
    display_daily_trendline,
    display_pie_to_pie_analysis,
    display_prominence_score_df,
    display_prominence_score_extra,
    display_sentiment_analysis,
    display_top_publications_authors,
)
from modules.reader import ExcelFileHandler, get_keywords


def _build_keyword_vars() -> tuple[
    str | None, str | None, str | None, str | None, str | None, str | None,
    list[str], list[str], list[str], list[str],
]:
    kw = get_keywords()
    k1 = kw[0] if len(kw) > 0 else None
    k2 = kw[1] if len(kw) > 1 else None
    k3 = kw[2] if len(kw) > 2 else None
    k4 = kw[3] if len(kw) > 3 else None
    k5 = kw[4] if len(kw) > 4 else None
    k6 = kw[5] if len(kw) > 5 else None
    overview = [k for k in [k1, k3, k4] if k]
    combined = [k1, k2] if k1 and k2 else (([k1] if k1 else []) + ([k2] if k2 else []))
    combined1 = [k3, k5] if k3 and k5 else (([k3] if k3 else []) + ([k5] if k5 else []))
    combined2 = [k4, k6] if k4 and k6 else (([k4] if k4 else []) + ([k6] if k6 else []))
    return k1, k2, k3, k4, k5, k6, overview, combined, combined1, combined2


def main() -> None:
    """Run the Streamlit data visualization app."""
    st.title("Data Visualization Using Streamlit and Altair")
    (
        kw1,
        kw2,
        kw3,
        kw4,
        kw5,
        kw6,
        overview_keywords,
        combined_keywords,
        combined_keywords1,
        combined_keywords2,
    ) = _build_keyword_vars()

    uploaded_file = st.file_uploader(
        "Upload your own Excel file (optional)",
        type=UPLOAD_FILE_TYPES,
        help=REQUIRED_FIELDS_NOTE,
    )
    if uploaded_file is not None:
        data_source: str | object = uploaded_file
    else:
        if not os.path.isfile(DEFAULT_DATA_PATH):
            st.error(f"Default data file not found: {DEFAULT_DATA_PATH}")
            return
        data_source = DEFAULT_DATA_PATH

    try:
        handler = ExcelFileHandler(data_source, DEFAULT_SHEET_NAME)
        df = handler.open_excel_file()
    except Exception as e:
        st.error(f"Error: {e!s}")
        return

    tab_overview, tab_pal, tab_cebu, tab_airasia = st.tabs([
        "Overview",
        "Philippine Airlines",
        "Cebu Pacific",
        "AirAsia",
    ])

    with tab_overview:
        st.header("Data Overview")
        display_general_overview(
            handler,
            df,
            overview_keywords=overview_keywords,
            brand_keywords=[kw1, kw3, kw4] if kw1 and kw3 and kw4 else overview_keywords[:3],
            prominence_groups=[combined_keywords, combined_keywords1, combined_keywords2],
        )

    with tab_pal:
        st.header("Philippine Airlines Analysis")
        if kw1 and kw2:
            display_pal_analysis(handler, kw1, kw2, "selected_keyword1_color")

    with tab_cebu:
        st.header("Cebu Pacific Analysis")
        if kw3 and kw5:
            display_competitor_analysis(
                handler, kw3, kw5, "selected_keyword3_color"
            )

    with tab_airasia:
        st.header("AirAsia Analysis")
        if kw4 and kw6:
            display_competitor_analysis(
                handler, kw4, kw6, "selected_keyword4_color"
            )


def display_general_overview(
    handler: ExcelFileHandler,
    df,
    overview_keywords: list[str],
    brand_keywords: list[str],
    prominence_groups: list[list[str]],
) -> None:
    """Render overview tab: dataframe, brand comparison, pie-to-pie, sentiment overview, prominence."""
    st.dataframe(df)
    display_brand_comparison(handler, brand_keywords)
    display_pie_to_pie_analysis(handler, overview_keywords)
    display_airlines_overview(handler, overview_keywords)
    display_prominence_score_df(handler, prominence_groups)
    display_prominence_score_extra(handler, prominence_groups)


def display_pal_analysis(
    handler: ExcelFileHandler,
    keyword: str,
    secondary_keyword: str,
    color_key: str,
) -> None:
    """Render Philippine Airlines metrics, sentiment, trendline, and top publications/authors."""
    display_airline_metrics(handler, keyword, secondary_keyword)
    display_sentiment_analysis(handler, keyword)
    display_daily_trendline(handler, keyword, color_key)
    display_top_publications_authors(handler, keyword, color_key)


def display_competitor_analysis(
    handler: ExcelFileHandler,
    keyword: str,
    secondary_keyword: str,
    color_key: str,
) -> None:
    """Render competitor airline metrics, sentiment, trendline, and top publications/authors."""
    display_airline_metrics(handler, keyword, secondary_keyword)
    display_sentiment_analysis(handler, keyword)
    display_daily_trendline(handler, keyword, color_key)
    display_top_publications_authors(handler, keyword, color_key)


if __name__ == "__main__":
    main()
