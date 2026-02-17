"""Excel file reading and dataset aggregation for media/sentiment analysis."""

import warnings
from typing import Any

import pandas as pd

from ..constants import (
    COLUMN_AVE,
    COLUMN_DATE,
    COLUMN_HEADLINE,
    COLUMN_HIT_SENTENCE,
    COLUMN_INFLUENCER,
    COLUMN_KEYWORDS,
    COLUMN_OPENING_TEXT,
    COLUMN_REACH,
    COLUMN_SENTIMENT,
    COLUMN_SOURCE,
    DATE_FORMAT_DISPLAY_PROMINENCE,
    DATE_FORMAT_DISPLAY_TREND,
    DATE_FORMAT_READ,
    DEFAULT_SHEET_NAME,
    SENTIMENT_VALUES,
)


class ExcelFileHandler:
    """Handles reading and querying an Excel dataset (e.g. media coverage)."""

    def __init__(self, file: str | Any, sheet_name: str = DEFAULT_SHEET_NAME) -> None:
        self.file = file
        self.sheet_name = sheet_name
        self.dataframe: pd.DataFrame | None = None

    def open_excel_file(self) -> pd.DataFrame:
        """Load the Excel sheet into the internal dataframe and return it."""
        try:
            self.dataframe = pd.read_excel(
                self.file, sheet_name=self.sheet_name, engine="openpyxl"
            )
            return self.dataframe
        except Exception as e:
            raise RuntimeError(f"Failed to read Excel file: {e!s}") from e

    def _ensure_loaded(self) -> None:
        if self.dataframe is None:
            self.open_excel_file()

    def normalize_keywords(
        self, keywords: str | list[str], *extra_keywords: str
    ) -> list[str]:
        """Normalize keyword(s) to a list of lowercase strings."""
        if isinstance(keywords, str):
            keywords = [keywords]
        out = list(keywords) + list(extra_keywords)
        return [k.lower() for k in out]

    def get_total_articles_keywords(
        self, keywords: str | list[str], *extra_keywords: str
    ) -> int:
        """Return total number of rows where Keywords contains any of the given keywords."""
        self._ensure_loaded()
        kws = self.normalize_keywords(keywords, *extra_keywords)
        return int(
            self.dataframe[COLUMN_KEYWORDS]
            .apply(lambda x: any(k in str(x).lower() for k in kws))
            .sum()
        )

    def count_mentions_headlines(
        self, keywords: str | list[str], *extra_keywords: str
    ) -> int:
        """Return count of rows where Headline contains any of the given keywords."""
        self._ensure_loaded()
        kws = self.normalize_keywords(keywords, *extra_keywords)
        return int(
            self.dataframe[COLUMN_HEADLINE]
            .apply(lambda x: any(k in str(x).lower() for k in kws))
            .sum()
        )

    def get_reach_sum(self, keywords: str | list[str], *extra_keywords: str) -> float:
        """Return sum of Reach for rows matching the given keywords."""
        self._ensure_loaded()
        kws = self.normalize_keywords(keywords, *extra_keywords)
        mask = self.dataframe[COLUMN_KEYWORDS].apply(
            lambda x: any(k in str(x).lower() for k in kws)
        )
        return float(self.dataframe.loc[mask, COLUMN_REACH].sum())

    def get_ave_sum(self, keywords: str | list[str], *extra_keywords: str) -> float:
        """Return sum of AVE for rows matching the given keywords."""
        self._ensure_loaded()
        kws = self.normalize_keywords(keywords, *extra_keywords)
        mask = self.dataframe[COLUMN_KEYWORDS].apply(
            lambda x: any(k in str(x).lower() for k in kws)
        )
        return float(self.dataframe.loc[mask, COLUMN_AVE].sum())

    def get_sentiment_counts(
        self, keywords: str | list[str], *extra_keywords: str
    ) -> dict[str, int]:
        """Return counts of Positive, Neutral, Negative for rows matching the keywords."""
        self._ensure_loaded()
        kws = self.normalize_keywords(keywords, *extra_keywords)
        mask = self.dataframe[COLUMN_KEYWORDS].apply(
            lambda x: any(k in str(x).lower() for k in kws)
        )
        filtered = self.dataframe[mask]
        return {
            "Positive": int((filtered[COLUMN_SENTIMENT] == "Positive").sum()),
            "Neutral": int((filtered[COLUMN_SENTIMENT] == "Neutral").sum()),
            "Negative": int((filtered[COLUMN_SENTIMENT] == "Negative").sum()),
        }

    def count_daily_trendline(
        self, keywords: str | list[str], *extra_keywords: str
    ) -> pd.DataFrame:
        """Return daily counts (Date, Count) for rows matching the keywords."""
        self._ensure_loaded()
        df_copy = self.dataframe.copy()
        df_copy[COLUMN_DATE] = pd.to_datetime(df_copy[COLUMN_DATE], format=DATE_FORMAT_READ)
        keyword_list = [keywords] if isinstance(keywords, str) else list(keywords)
        keyword_list.extend(extra_keywords)
        filtered = df_copy[
            df_copy[COLUMN_KEYWORDS].apply(
                lambda x: any(kw in str(x) for kw in keyword_list)
            )
        ]
        daily = (
            filtered.groupby(filtered[COLUMN_DATE].dt.date)
            .size()
            .reset_index(name="Count")
        )
        daily[COLUMN_DATE] = pd.to_datetime(daily[COLUMN_DATE]).dt.strftime(
            DATE_FORMAT_DISPLAY_TREND
        )
        daily = daily.sort_values(COLUMN_DATE)
        return daily[[COLUMN_DATE, "Count"]]

    def get_top_publications(
        self, keyword: str, *extra_keywords: str
    ) -> pd.DataFrame:
        """Return top 5 sources by volume and AVE for the given keyword(s)."""
        self._ensure_loaded()
        keyword_list = [keyword] + list(extra_keywords)
        filtered = self.dataframe[
            self.dataframe[COLUMN_KEYWORDS].apply(
                lambda x: any(kw in str(x) for kw in keyword_list)
            )
        ]
        volume_counts = (
            filtered.groupby(COLUMN_SOURCE).size().sort_values(ascending=False).head(5)
        )
        top_5 = volume_counts.index.tolist()
        ave_sums = (
            filtered[filtered[COLUMN_SOURCE].isin(top_5)]
            .groupby(COLUMN_SOURCE)[COLUMN_AVE]
            .sum()
            .round(2)
        )
        result = pd.DataFrame(
            {
                "Rank": range(1, len(top_5) + 1),
                "Source": top_5,
                "Volume": volume_counts.values,
                "AVE": ave_sums.reindex(top_5).values,
            }
        )
        result = result.sort_values("Volume", ascending=False).reset_index(drop=True)
        result["Rank"] = range(1, len(result) + 1)
        return result

    def get_top_authors(
        self, keywords: str | list[str], *extra_keywords: str
    ) -> pd.DataFrame:
        """Return top 5 influencers by volume and AVE for the given keyword(s)."""
        self._ensure_loaded()
        keyword_list = [keywords] if isinstance(keywords, str) else list(keywords)
        keyword_list.extend(extra_keywords)
        filtered = self.dataframe[
            self.dataframe[COLUMN_KEYWORDS].apply(
                lambda x: any(kw in str(x) for kw in keyword_list)
            )
        ]
        if filtered.empty:
            return pd.DataFrame(columns=["Rank", "Influencer", "Volume", "AVE"])
        volume_counts = (
            filtered.groupby(COLUMN_INFLUENCER)
            .size()
            .sort_values(ascending=False)
            .head(5)
        )
        top_5 = volume_counts.index.tolist()
        ave_sums = (
            filtered[filtered[COLUMN_INFLUENCER].isin(top_5)]
            .groupby(COLUMN_INFLUENCER)[COLUMN_AVE]
            .sum()
            .round(2)
        )
        result = pd.DataFrame(
            {
                "Rank": range(1, len(top_5) + 1),
                "Influencer": top_5,
                "Volume": volume_counts.values,
                "AVE": ave_sums.reindex(top_5).values,
            }
        )
        result = result.sort_values("Volume", ascending=False).reset_index(drop=True)
        result["Rank"] = range(1, len(result) + 1)
        return result

    def create_summary_dataframe(
        self, overview_keywords: list[str]
    ) -> pd.DataFrame:
        """Build a summary DataFrame of mention counts and sentiment for overview charts."""
        self._ensure_loaded()
        keywords = [kw for kw in overview_keywords if kw]
        sentiment_data = self.get_sentiment_counts(keywords[0]) if keywords else {}
        airline_mentions = {kw: self.get_total_articles_keywords(kw) for kw in keywords}
        metric_names = list(airline_mentions.keys()) + list(SENTIMENT_VALUES)
        values = list(airline_mentions.values()) + [
            sentiment_data.get("Positive", 0),
            sentiment_data.get("Neutral", 0),
            sentiment_data.get("Negative", 0),
        ]
        df = pd.DataFrame({"Metric": metric_names, "Value": values}).reset_index(drop=True)
        df["Metric"] = df["Metric"].str.ljust(25)
        return df

    def sentiment_overview(self, overview_keywords: list[str]) -> pd.DataFrame:
        """Return a DataFrame of sentiment counts per keyword."""
        self._ensure_loaded()
        keywords = [kw for kw in overview_keywords if kw]
        if not keywords:
            return pd.DataFrame(
                columns=["Keyword", "Positive", "Neutral", "Negative"]
            )
        results = []
        for kw in keywords:
            counts = self.get_sentiment_counts(kw)
            results.append(
                {
                    "Keyword": kw,
                    "Positive": counts.get("Positive", 0),
                    "Neutral": counts.get("Neutral", 0),
                    "Negative": counts.get("Negative", 0),
                }
            )
        summary = pd.DataFrame(results)
        for col in SENTIMENT_VALUES:
            summary[col] = summary[col].astype(int)
        return summary

    def prominence_score(
        self, keywords: str | list[str] | list[list[str]], *extra_keywords: Any
    ) -> pd.DataFrame:
        """Return rows with prominence scores per keyword set; original columns plus score columns."""
        self._ensure_loaded()
        df = self.dataframe.copy()
        if isinstance(keywords, str):
            keywords = [keywords]
        all_keywords = list(keywords) + list(extra_keywords)
        all_keywords = [
            k.lower() if isinstance(k, str) else [x.lower() for x in k]
            for k in all_keywords
            if k is not None
        ]
        if not all_keywords:
            return pd.DataFrame(columns=df.columns)

        def score_row(row: pd.Series, keyword_set: str | list[str]) -> float:
            headline = str(row[COLUMN_HEADLINE]).lower()
            opening = str(row[COLUMN_OPENING_TEXT]).lower()
            hit = str(row[COLUMN_HIT_SENTENCE]).lower()
            kset = [keyword_set] if isinstance(keyword_set, str) else keyword_set
            if any(k in headline for k in kset):
                return 1.0
            if any(k in opening for k in kset):
                return 0.7
            if any(k in hit for k in kset):
                return 0.1
            return 0.0

        for idx, kw in enumerate(all_keywords):
            df[str(idx + 1)] = df.apply(lambda row: score_row(row, kw), axis=1)
        score_cols = [str(i + 1) for i in range(len(all_keywords))]
        max_score = df[score_cols].max(axis=1)
        result_df = df[max_score > 0].copy()
        if result_df.empty:
            return pd.DataFrame(columns=df.columns)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result_df[COLUMN_DATE] = pd.to_datetime(result_df[COLUMN_DATE]).dt.strftime(
                DATE_FORMAT_DISPLAY_PROMINENCE
            )
        result_df = result_df.sort_values(by=score_cols, ascending=False).reset_index(
            drop=True
        )
        rename = {
            str(i + 1): kw if isinstance(kw, str) else f"Keyword {i + 1} Prominence Score"
            for i, kw in enumerate(all_keywords)
        }
        result_df = result_df.rename(columns=rename)
        return result_df

    def prominence_score_extra(
        self, keywords: str | list[str] | list[list[str]], *extra_keywords: Any
    ) -> pd.DataFrame:
        """Return total and average prominence per keyword set."""
        self._ensure_loaded()
        if isinstance(keywords, str):
            keywords = [keywords]
        all_keywords = list(keywords) + list(extra_keywords)
        all_keywords = [
            k.lower() if isinstance(k, str) else [x.lower() for x in k]
            for k in all_keywords
            if k is not None
        ]
        if not all_keywords:
            return pd.DataFrame(
                columns=["Keyword", "Total Prominence", "Average Prominence"]
            )

        def score(text_fields: tuple[Any, Any, Any], keyword_set: str | list[str]) -> float:
            kset = [keyword_set] if isinstance(keyword_set, str) else keyword_set
            headline, opening, hit = text_fields
            headline, opening, hit = str(headline).lower(), str(opening).lower(), str(hit).lower()
            if any(k in headline for k in kset):
                return 1.0
            if any(k in opening for k in kset):
                return 0.7
            if any(k in hit for k in kset):
                return 0.1
            return 0.0

        results = []
        for kw in all_keywords:
            scores = [
                score(
                    (
                        row[COLUMN_HEADLINE],
                        row[COLUMN_OPENING_TEXT],
                        row[COLUMN_HIT_SENTENCE],
                    ),
                    kw,
                )
                for _, row in self.dataframe.iterrows()
            ]
            total = sum(scores)
            non_zero = [s for s in scores if s > 0]
            avg = round(total / len(non_zero), 2) if non_zero else 0
            name = (kw[0] if isinstance(kw, list) else kw).title()
            results.append(
                {
                    "Keyword": name,
                    "Total Prominence": round(total, 2),
                    "Average Prominence": avg,
                }
            )
        return pd.DataFrame(results)
