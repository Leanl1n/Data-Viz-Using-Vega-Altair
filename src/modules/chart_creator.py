"""Chart creation for media and sentiment analysis using Altair and Matplotlib."""

import matplotlib
matplotlib.use("Agg")  # headless backend for Streamlit Cloud / servers
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch

import altair as alt
import pandas as pd

from .constants import (
    COLOR_MAPPING,
    PIE_AIRLINE_COLORS,
    PIE_SENTIMENT_COLORS,
    PIE_SENTIMENT_COLORS_MATPLOTLIB,
)


class ChartCreator:
    """Static helpers for building Altair and Matplotlib charts."""

    @staticmethod
    def create_airline_mentions_pie_chart(
        sizes: list[int | float],
        labels: list[str],
        colors: list[str] | None = None,
    ) -> alt.Chart:
        """Build an Altair pie chart for airline mention counts."""
        colors = colors or PIE_AIRLINE_COLORS[: len(labels)]
        df = pd.DataFrame({"category": labels, "value": sizes})
        return (
            alt.Chart(df)
            .mark_arc()
            .encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color=alt.Color(
                    "category:N",
                    scale=alt.Scale(domain=labels, range=colors),
                    legend=alt.Legend(title="Airlines", orient="right", labelLimit=200),
                ),
                tooltip=["category", "value"],
            )
            .properties(width=300, height=300)
        )

    @staticmethod
    def create_sentiment_pie_chart(
        sizes: list[int | float],
        labels: list[str] | None = None,
        colors: list[str] | None = None,
    ) -> alt.Chart:
        """Build an Altair pie chart for sentiment counts."""
        labels = labels or ["Positive", "Neutral", "Negative"]
        colors = colors or PIE_SENTIMENT_COLORS
        df = pd.DataFrame({"sentiment": labels, "value": sizes})
        return (
            alt.Chart(df)
            .mark_arc()
            .encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color=alt.Color(
                    "sentiment:N",
                    scale=alt.Scale(domain=labels, range=colors),
                    legend=alt.Legend(title="Sentiment", orient="right", labelLimit=200),
                ),
                tooltip=["sentiment", "value"],
            )
            .properties(width=300, height=300)
        )

    @staticmethod
    def create_side_by_side_pie_charts(
        airlines_data: list[int | float],
        sentiment_data: list[int | float],
        airline_labels: list[str],
    ) -> plt.Figure:
        """Build a Matplotlib figure with airline and sentiment pie charts side by side."""
        fig = plt.figure(figsize=(12, 6))
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        fig.subplots_adjust(wspace=0)
        sentiment_labels = ["Positive", "Neutral", "Negative"]
        airline_colors = PIE_AIRLINE_COLORS[: len(airline_labels)]
        sentiment_colors = PIE_SENTIMENT_COLORS_MATPLOTLIB
        total_air = sum(airlines_data[:3]) or 1
        angle = -180 * airlines_data[0] / total_air

        wedges1, _, _ = ax1.pie(
            airlines_data[:3],
            labels=airline_labels,
            colors=airline_colors,
            autopct="%1.1f%%",
            startangle=angle,
            pctdistance=0.85,
            explode=[0, 0, 0],
            textprops={"color": "black", "size": 8},
        )
        wedges2, _, _ = ax2.pie(
            sentiment_data[3:6],
            labels=sentiment_labels,
            colors=sentiment_colors,
            autopct="%1.1f%%",
            startangle=angle,
            pctdistance=0.85,
            radius=0.8,
            textprops={"color": "black", "size": 8},
        )

        if wedges1 and wedges2:
            c1, r1 = wedges1[0].center, wedges1[0].r
            c2, r2 = wedges2[0].center, wedges2[0].r
            for (xa, ya), (xb, yb) in [
                ((c2[0], c2[1] + r2), (c1[0], c1[1] + r1)),
                ((c2[0], c2[1] - r2), (c1[0], c1[1] - r1)),
            ]:
                con = ConnectionPatch(
                    xyA=(xa, ya),
                    xyB=(xb, yb),
                    coordsA="data",
                    coordsB="data",
                    axesA=ax2,
                    axesB=ax1,
                    color="gray",
                    linestyle="--",
                    linewidth=1,
                )
                ax2.add_artist(con)
        return fig

    @staticmethod
    def create_daily_trendline_chart(
        daily_counts: pd.DataFrame,
        color_key: str,
        smoothed_series: pd.Series | None = None,
        trend_series: pd.Series | None = None,
    ) -> alt.Chart:
        """Build an Altair line chart for daily counts with optional smoothing and trend line."""
        color = COLOR_MAPPING.get(color_key, "#001F60")
        df = daily_counts.copy()
        if smoothed_series is not None:
            df = df.assign(Smoothed=smoothed_series.values)
        if trend_series is not None:
            df = df.assign(Trend=trend_series.values)

        top_3 = df.nlargest(3, "Count")
        base = alt.Chart(df).encode(
            x=alt.X("Date:N", axis=alt.Axis(labelAngle=45, title=None)),
            y=alt.Y("Count:Q", axis=alt.Axis(title="Article count")),
        )
        line = base.mark_line(color=color, strokeWidth=2)
        points = base.mark_circle(color=color, size=80, opacity=0.9)
        peak_labels = (
            alt.Chart(top_3)
            .mark_text(
                align="left", baseline="bottom", dx=5, dy=-10, fontSize=11, color="#64748b"
            )
            .encode(
                x="Date:N",
                y="Count:Q",
                text=alt.Text("Count:Q", format=".0f"),
                tooltip=[alt.Tooltip("Date:N"), alt.Tooltip("Count:Q")],
            )
        )
        layer = line + points + peak_labels

        if "Smoothed" in df.columns:
            smooth_base = alt.Chart(df).encode(
                x=alt.X("Date:N"),
                y=alt.Y("Smoothed:Q"),
                tooltip=[alt.Tooltip("Date:N"), alt.Tooltip("Smoothed:Q", format=".2f")],
            )
            layer = layer + smooth_base.mark_line(
                color="#f59e0b", strokeWidth=2.5, strokeDash=[4, 2]
            )

        if "Trend" in df.columns:
            trend_base = alt.Chart(df).encode(
                x=alt.X("Date:N"),
                y=alt.Y("Trend:Q"),
                tooltip=[alt.Tooltip("Date:N"), alt.Tooltip("Trend:Q", format=".2f")],
            )
            layer = layer + trend_base.mark_line(
                color="#dc2626", strokeWidth=2, strokeDash=[6, 3]
            )

        return (
            layer.properties(width=700, height=380)
            .configure_axis(grid=True, gridColor="#EAEAEA")
            .configure_view(strokeWidth=0)
            .configure_legend(orient="bottom")
            .interactive()
        )

    @staticmethod
    def create_publications_horizontal_bar(df: pd.DataFrame, color_key: str) -> alt.Chart:
        """Build a horizontal bar chart for publication/source volume."""
        color = COLOR_MAPPING.get(color_key, "#001F60")
        return (
            alt.Chart(df)
            .mark_bar()
            .encode(
                y=alt.Y("Source:N", sort="-x", title=None),
                x=alt.X("Volume:Q", axis=None),
                color=alt.value(color),
                tooltip=["Source", "Volume"],
            )
            .properties(width=600, height=400)
            .configure_axis(labelFontSize=12, titleFontSize=14)
        )

    @staticmethod
    def create_get_top_authors(df: pd.DataFrame, color_key: str) -> alt.Chart:
        """Build a horizontal bar chart for top authors/influencers."""
        color = COLOR_MAPPING.get(color_key, "#001F60")
        return (
            alt.Chart(df)
            .mark_bar()
            .encode(
                y=alt.Y("Influencer:N", sort="-x", title=None),
                x=alt.X("Volume:Q", axis=None),
                color=alt.value(color),
                tooltip=["Influencer", "Volume"],
            )
            .properties(width=600, height=400)
            .configure_axis(labelFontSize=12, titleFontSize=14)
        )

    @staticmethod
    def create_airlines_sentiment_overview(
        df: pd.DataFrame,
        keyword_order: list[str] | None = None,
    ) -> alt.Chart:
        """Build a 100% stacked bar chart of sentiment per keyword."""
        melted = df.melt(
            id_vars=["Keyword"],
            value_vars=["Positive", "Neutral", "Negative"],
            var_name="Sentiment",
            value_name="Count",
        )
        melted["Count"] = pd.to_numeric(melted["Count"])
        melted["Percentage"] = melted.groupby("Keyword")["Count"].transform(
            lambda x: x / x.sum() * 100
        )
        keyword_order = keyword_order or list(melted["Keyword"].unique())
        sentiment_order = ["Positive", "Neutral", "Negative"]
        return (
            alt.Chart(melted)
            .mark_bar()
            .encode(
                y=alt.Y("Keyword:N", title=None, sort=keyword_order),
                x=alt.X(
                    "Percentage:Q",
                    title=None,
                    stack="normalize",
                    axis=alt.Axis(format="%"),
                ),
                color=alt.Color(
                    "Sentiment:N",
                    scale=alt.Scale(
                        domain=sentiment_order,
                        range=PIE_SENTIMENT_COLORS,
                    ),
                ),
                order=alt.Order("Sentiment", sort="descending"),
                tooltip=[
                    alt.Tooltip("Keyword:N"),
                    alt.Tooltip("Sentiment:N"),
                    alt.Tooltip("Percentage:Q", format=".1f", title="Percentage"),
                    alt.Tooltip("Count:Q", title="Number of Articles"),
                ],
            )
            .properties(width=1000, height=400)
        )

    @staticmethod
    def create_prominence_score_chart_extra(df: pd.DataFrame) -> alt.Chart:
        """Build a bar chart of total prominence with average line overlay."""
        base_bars = alt.Chart(df).encode(
            x=alt.X("Keyword:N", sort=None, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Total Prominence:Q", title=None),
            color=alt.Color(
                "Keyword:N",
                scale=alt.Scale(range=["#ff0000", "#039482", "#001F60"]),
                legend=alt.Legend(title="Keywords"),
            ),
        )
        bars = base_bars.mark_bar().encode(
            tooltip=[
                alt.Tooltip("Keyword:N"),
                alt.Tooltip("Total Prominence:Q", format=".2f"),
                alt.Tooltip("Average Prominence:Q", format=".2f"),
            ]
        )
        base_line = alt.Chart(df).encode(
            x=alt.X("Keyword:N", sort=None),
            y=alt.Y("Average Prominence:Q", title=None, axis=alt.Axis(titleColor="red")),
        )
        line = base_line.mark_line(color="black")
        points = base_line.mark_circle(color="red", size=50)
        text = base_line.mark_text(
            align="center", baseline="bottom", dy=-5, color="red"
        ).encode(text=alt.Text("Average Prominence:Q", format=".2f"))
        return (
            alt.layer(bars, line + points + text)
            .resolve_scale(y="independent")
            .properties(width=600, height=400)
            .configure_axis(labelFontSize=12, titleFontSize=14)
        )
