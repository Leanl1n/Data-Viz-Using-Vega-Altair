import pandas as pd
import streamlit as st
from chart_creator import ChartCreator
from config_loader import get_keywords
from config_loader import get_sites_by_type

# Load keywords
keyword_list = get_keywords()

selected_keyword1 = keyword_list[0] if len(keyword_list) > 0 else None
selected_keyword2 = keyword_list[1] if len(keyword_list) > 1 else None     
selected_keyword3 = keyword_list[2] if len(keyword_list) > 2 else None
selected_keyword4 = keyword_list[3] if len(keyword_list) > 3 else None
selected_keyword5 = keyword_list[4] if len(keyword_list) > 4 else None
selected_keyword6 = keyword_list[5] if len(keyword_list) > 5 else None

site_list_print = get_sites_by_type("Print")
site_list_broadcast = get_sites_by_type("Broadcast")
site_list_blog = get_sites_by_type("Blog")
site_list_social_media = get_sites_by_type("Social Media")

print(site_list_social_media)

class ExcelFileHandler:
    def __init__(self, file, sheet_name):
        self.file = file
        self.sheet_name = sheet_name
        self.dataframe = None

    def open_excel_file(self):
        try:
            self.dataframe = pd.read_excel(self.file, sheet_name=self.sheet_name, engine='openpyxl')
            return self.dataframe
        except Exception as e:
            raise Exception(f"Failed to read Excel file: {str(e)}")
            
    def normalize_keywords(keywords, *extra_keywords):
        if isinstance(keywords, str):
            keywords = [keywords]
        keywords = list(keywords)  # In case it's a tuple
        keywords.extend(extra_keywords)
        return [k.lower() for k in keywords]
        
    # Total articles in Keyword column - Media Coverage
    def get_total_articles_keywords(self, keywords, *extra_keywords):
        if self.dataframe is None:
            self.open_excel_file()

        # Ensure keywords is a list
        if isinstance(keywords, str):
            keywords = [keywords]

        # Add extra keywords if provided
        keywords.extend(extra_keywords)

        # Case-insensitive check for multiple keywords
        return self.dataframe['Keywords'].apply(lambda x: any(k.lower() in x.lower() for k in keywords)).sum()
    
    # Total articles in Headline column - Headline Presence
    def count_mentions_headlines(self, keywords, *extra_keywords): 
        if self.dataframe is None:
            self.open_excel_file()

        # Ensure keywords is a list
        if isinstance(keywords, str):
            keywords = [keywords]

        # Add extra keywords if provided
        keywords.extend(extra_keywords)

        # Case-insensitive check for multiple keywords
        return self.dataframe['Headline'].apply(lambda x: any(k.lower() in x.lower() for k in keywords)).sum()

    # Total reach
    def get_reach_sum(self, keywords, *extra_keywords):
        if self.dataframe is None:
            self.open_excel_file()

        # Ensure keywords is a list
        if isinstance(keywords, str):
            keywords = [keywords]

        # Add extra keywords if provided
        keywords.extend(extra_keywords)

        # Filter dataframe for rows containing any of the keywords (case-insensitive)
        mask = self.dataframe['Keywords'].apply(lambda x: any(k.lower() in x.lower() for k in keywords))
        total = self.dataframe[mask]

        return total['Reach'].sum()
    
    # Total AVE
    def get_ave_sum(self, keywords, *extra_keywords):
        if self.dataframe is None:
            self.open_excel_file()

        # Ensure keywords is a list
        if isinstance(keywords, str):
            keywords = [keywords]

        # Add extra keywords if provided
        keywords.extend(extra_keywords)

        # Filter dataframe for rows containing any of the keywords (case-insensitive)
        mask = self.dataframe['Keywords'].apply(lambda x: any(k.lower() in x.lower() for k in keywords))
        total = self.dataframe[mask]

        return total['AVE'].sum()
    
    # Total sentiment counts
    def get_sentiment_counts(self, keywords, *extra_keywords):
        if self.dataframe is None:
            self.open_excel_file()

        # Ensure keywords is a list
        if isinstance(keywords, str):
            keywords = [keywords]

        # Add extra keywords if provided
        keywords.extend(extra_keywords)

        # Filter dataframe for rows containing any of the keywords (case-insensitive)
        mask = self.dataframe['Keywords'].apply(lambda x: any(k.lower() in x.lower() for k in keywords))
        filtered_rows = self.dataframe[mask]

        # Count sentiment occurrences
        positive = filtered_rows[filtered_rows['Sentiment'] == 'Positive'].shape[0]
        neutral = filtered_rows[filtered_rows['Sentiment'] == 'Neutral'].shape[0]
        negative = filtered_rows[filtered_rows['Sentiment'] == 'Negative'].shape[0]

        # Create sentiment pie chart
        sizes = [positive, neutral, negative]
        ChartCreator.create_sentiment_pie_chart(sizes)

        return {'Positive': positive, 'Neutral': neutral, 'Negative': negative}
    
    # Daily trendline
    def count_daily_trendline(self, keywords, *extra_keywords):
        if self.dataframe is None:
            self.open_excel_file()

        # Make a copy of the dataframe to avoid modifying the original
        df_copy = self.dataframe.copy()

        # Convert Date column to datetime format
        df_copy['Date'] = pd.to_datetime(df_copy['Date'], format='%d-%b-%Y %I:%M%p')

        # Combine all keywords into a list
        keyword_list = [keywords] + list(extra_keywords)

        # Filter the dataframe for rows where the Keywords column contains any of the provided keywords
        filtered_df = df_copy[df_copy['Keywords'].apply(lambda x: any(kw in str(x) for kw in keyword_list))]

        # Group by date and count occurrences
        daily_counts = (filtered_df.groupby(filtered_df['Date'].dt.date)
                        .size()
                        .reset_index(name='Count'))

        # Format the date as 'Month-Day'
        daily_counts['Date'] = pd.to_datetime(daily_counts['Date']).dt.strftime('%b-%d')

        # Sort by the original date
        daily_counts = daily_counts.sort_values('Date')

        return daily_counts[['Date', 'Count']]
    
    # Top 5 sources
    def get_top_publications(self, keyword, *extra_keywords):
        if self.dataframe is None:
            self.open_excel_file()

        # Combine all keywords into a list
        keyword_list = [keyword] + list(extra_keywords)

        # Filter rows where 'Keywords' contains any of the provided keywords (No regex)
        filtered_df = self.dataframe[self.dataframe['Keywords'].apply(lambda x: any(kw in str(x) for kw in keyword_list))]

        # Get top 5 sources by volume (count)
        volume_counts = (filtered_df.groupby('Source').size()
                        .sort_values(ascending=False)
                        .head(5))

        top_5_sources = volume_counts.index.tolist()

        # Get AVE sums for the top 5 sources
        ave_sums = (filtered_df[filtered_df['Source'].isin(top_5_sources)]
                    .groupby('Source')['AVE']
                    .sum()
                    .round(2))

        # Create DataFrame with rankings
        result_df = pd.DataFrame({
            'Rank': range(1, len(top_5_sources) + 1),  # Rank dynamically based on actual results
            'Source': top_5_sources,
            'Volume': volume_counts.values,
            'AVE': ave_sums[top_5_sources].values
        })

        # Ensure sorting by Volume (descending) before returning
        result_df = result_df.sort_values('Volume', ascending=False).reset_index(drop=True)
        result_df['Rank'] = range(1, len(result_df) + 1)  # Reset rank after sorting

        return result_df
    
    # Top 5 authors
    def get_top_authors(self, keywords, *extra_keywords):
        if self.dataframe is None:
            self.open_excel_file()

        # Combine primary and extra keywords into a list
        keyword_list = [keywords] + list(extra_keywords)

        # Filter rows that contain at least one of the keywords
        keyword_df = self.dataframe[self.dataframe['Keywords'].apply(lambda x: any(kw in str(x) for kw in keyword_list))]

        if keyword_df.empty:
            return pd.DataFrame(columns=['Rank', 'Influencer', 'Volume', 'AVE'])

        # Get top 5 influencers by volume (count)
        volume_counts = (keyword_df.groupby('Influencer').size()
                        .sort_values(ascending=False)
                        .head(5))

        top_5_influencers = volume_counts.index.tolist()

        # Get AVE sums for these top 5 influencers
        ave_sums = (keyword_df[keyword_df['Influencer'].isin(top_5_influencers)]
                    .groupby('Influencer')['AVE']
                    .sum()
                    .round(2))

        # Create DataFrame
        result_df = pd.DataFrame({
            'Rank': range(1, len(top_5_influencers) + 1),
            'Influencer': top_5_influencers,
            'Volume': volume_counts.values,
            'AVE': ave_sums.reindex(top_5_influencers).values
        })

        # Sort by Volume
        result_df = result_df.sort_values('Volume', ascending=False).reset_index(drop=True)
        result_df['Rank'] = range(1, len(result_df) + 1)  # Reassign ranking

        return result_df

    # Pie to Pie chart dataframe
    def create_summary_dataframe(self):
        if self.dataframe is None:
            self.open_excel_file()
        
        # Select only non-empty keywords - excluded aliases
        keywords = [kw for kw in [selected_keyword1, selected_keyword3, selected_keyword4] if kw]

        # Get sentiment data and mention counts dynamically
        sentiment_data = self.get_sentiment_counts(selected_keyword1)
        airline_mentions = {kw: self.get_total_articles_keywords(kw) for kw in keywords}

        # Build metric names
        metric_names = list(airline_mentions.keys()) + ['Positive', 'Neutral', 'Negative']

        # Get mention values
        values = list(airline_mentions.values())

        # Add sentiment counts directly from the dictionary
        values += [
            sentiment_data['Positive'],
            sentiment_data['Neutral'],
            sentiment_data['Negative']
        ]

        # Create DataFrame
        summary_data = {'Metric': metric_names, 'Value': values}
        df = pd.DataFrame(summary_data).reset_index(drop=True)

        # Align metric names visually
        df['Metric'] = df['Metric'].str.ljust(25)

        # Create pie charts
        ChartCreator.create_side_by_side_pie_charts(values[:len(airline_mentions)], values)

        return df

    # Sentiment Overview
    def sentiment_overview(self):
        if self.dataframe is None:
            self.open_excel_file()

        # Select only non-empty keywords
        keywords = [kw for kw in [selected_keyword1, selected_keyword3, selected_keyword4] if kw]

        if not keywords:
            return pd.DataFrame(columns=['Keyword', 'Positive', 'Neutral', 'Negative'])

        results = []

        # Get sentiment counts for each selected keyword
        for keyword in keywords:
            sentiment_data = self.get_sentiment_counts(keyword)
            
            # Use individual keyword instead of the full list
            results.append({
                'Keyword': keyword,  # Changed from keywords to keyword
                'Positive': sentiment_data.get('Positive', 0),
                'Neutral': sentiment_data.get('Neutral', 0),
                'Negative': sentiment_data.get('Negative', 0)
            })

        # Create summary DataFrame
        summary_df = pd.DataFrame(results)
        
        # Ensure numeric columns are integers
        for col in ['Positive', 'Neutral', 'Negative']:
            summary_df[col] = summary_df[col].astype(int)

        return summary_df

    # Prominence Score
    def prominence_score(self, keywords, *extra_keywords):
        """
        Calculate prominence scores and return as DataFrame with all original columns plus scores
        Args:
            keywords: Primary keyword or list of keywords
            *extra_keywords: Additional keywords to include in the analysis
        Returns:
            DataFrame with all original columns and prominence scores for each keyword
        """
        if self.dataframe is None:
            self.open_excel_file()

        # Create a copy of dataframe
        df = self.dataframe.copy()
        
        # Ensure keywords is a list 
        if isinstance(keywords, str):
            keywords = [keywords]
        
        # Add extra keywords if provided
        all_keywords = keywords + list(extra_keywords)
        
        # Filter out None values and convert all keywords to lowercase
        all_keywords = [k.lower() if isinstance(k, str) else [kw.lower() for kw in k] 
                    for k in all_keywords if k is not None]
        
        if not all_keywords:
            return pd.DataFrame(columns=df.columns)
        
        def calculate_keyword_score(row, keyword_set):
            # Convert text fields to lowercase strings for comparison
            headline = str(row['Headline']).lower()
            opening_text = str(row['Opening Text']).lower()
            hit_sentence = str(row['Hit Sentence']).lower()
            
            # Handle both string and list keywords
            if isinstance(keyword_set, str):
                keyword_set = [keyword_set]
            
            # Calculate score for current keyword set
            if any(keyword.lower() in headline for keyword in keyword_set):
                return 1.0
            elif any(keyword.lower() in opening_text for keyword in keyword_set):
                return 0.7
            elif any(keyword.lower() in hit_sentence for keyword in keyword_set):
                return 0.1
            return 0.0
        
        # Calculate scores for each keyword
        for idx, keyword in enumerate(all_keywords):
            column_name = str(idx + 1)  # Just use numbers for temporary column names
            df[column_name] = df.apply(lambda row: calculate_keyword_score(row, keyword), axis=1)
        
        # Calculate maximum score across all keywords for filtering
        score_columns = [str(i+1) for i in range(len(all_keywords))]
        max_score = df[score_columns].max(axis=1)
        
        # Filter out rows with zero scores while keeping all columns
        result_df = df[max_score > 0].copy()
        
        if result_df.empty:
            return pd.DataFrame(columns=df.columns)
        
        # Format date column
        result_df['Date'] = pd.to_datetime(result_df['Date']).dt.strftime('%Y-%m-%d')
        
        # Sort by maximum score descending
        result_df = result_df.sort_values(by=score_columns, ascending=False).reset_index(drop=True)
        
        # Rename score columns to keyword names
        rename_dict = {str(idx + 1): kw if isinstance(kw, str) else f"Keyword {idx + 1} Prominence Score"
                    for idx, kw in enumerate(all_keywords)}
        result_df = result_df.rename(columns=rename_dict)
        
        return result_df
    
    def prominence_score_extra(self, keywords, *extra_keywords):
        """
        Calculate total prominence scores and average per article for each keyword
        Args:
            keywords: Primary keyword or list of keywords
            *extra_keywords: Additional keywords to include in the analysis
        Returns:
            DataFrame with keywords, their total prominence scores, and average per article
        """
        if self.dataframe is None:
            self.open_excel_file()

        # Ensure keywords is a list 
        if isinstance(keywords, str):
            keywords = [keywords]
        
        # Add extra keywords
        all_keywords = keywords + list(extra_keywords)
        
        # Filter out None values and convert to lowercase
        all_keywords = [k.lower() if isinstance(k, str) else [kw.lower() for kw in k] 
                    for k in all_keywords if k is not None]
        
        if not all_keywords:
            return pd.DataFrame(columns=['Keyword', 'Total Prominence', 'Average Prominence'])

        def calculate_keyword_score(text_fields, keyword_set):
            if isinstance(keyword_set, str):
                keyword_set = [keyword_set]
            
            headline, opening_text, hit_sentence = text_fields
            
            if any(keyword.lower() in str(headline).lower() for keyword in keyword_set):
                return 1.0
            elif any(keyword.lower() in str(opening_text).lower() for keyword in keyword_set):
                return 0.7
            elif any(keyword.lower() in str(hit_sentence).lower() for keyword in keyword_set):
                return 0.1
            return 0.0

        results = []
        for keyword in all_keywords:
            # Calculate scores for each article
            scores = [calculate_keyword_score(
                (row['Headline'], row['Opening Text'], row['Hit Sentence']), 
                keyword) for _, row in self.dataframe.iterrows()]
            
            # Calculate total and filter non-zero scores for average
            total_score = sum(scores)
            non_zero_scores = [s for s in scores if s > 0]
            avg_score = round(total_score / len(non_zero_scores), 2) if non_zero_scores else 0
            
            keyword_name = (keyword[0] if isinstance(keyword, list) else keyword).title()
            results.append({
                'Keyword': keyword_name, 
                'Total Prominence': round(total_score, 2),
                'Average Prominence': avg_score
            })

        return pd.DataFrame(results)
