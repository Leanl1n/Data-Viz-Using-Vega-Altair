import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
from config_loader import get_keywords

# Load keywords
keyword_list = get_keywords()

selected_keyword1 = keyword_list[0] if len(keyword_list) > 0 else None
selected_keyword2 = keyword_list[1] if len(keyword_list) > 1 else None     
selected_keyword3 = keyword_list[2] if len(keyword_list) > 2 else None
selected_keyword4 = keyword_list[3] if len(keyword_list) > 3 else None
selected_keyword5 = keyword_list[4] if len(keyword_list) > 4 else None
selected_keyword6 = keyword_list[5] if len(keyword_list) > 5 else None

color_mapping = {
        "selected_keyword1_color": "#001F60",
        "selected_keyword3_color": "#039482",
        "selected_keyword4_color": "#ff0000"
    }

class ChartCreator:
    @staticmethod
    def create_airline_mentions_pie_chart(sizes, labels=[selected_keyword1, selected_keyword3, selected_keyword4]):
        # Create DataFrame for the pie chart
        df = pd.DataFrame({
            'category': labels,
            'value': sizes,
            'color': ['#001F60', '#FFD700', '#EE2A29']
        })
        
        return alt.Chart(df).mark_arc().encode(
            theta=alt.Theta(field='value', type='quantitative'),
            color=alt.Color('category:N', 
                          scale=alt.Scale(
                              domain=labels,
                              range=['#001F60', '#FFD700', '#EE2A29']
                          ),
                          legend=alt.Legend(
                              title='Airlines',
                              orient='right',
                              labelLimit=200
                          )),
            tooltip=['category', 'value']
        ).properties(
            width=300,
            height=300,
        )

    @staticmethod
    def create_sentiment_pie_chart(sizes, labels=['Positive', 'Neutral', 'Negative']):
        df = pd.DataFrame({
            'sentiment': labels,
            'value': sizes,
            'color': ['#2ecc71', '#95a5a6', '#e74c3c']
        })
        
        return alt.Chart(df).mark_arc().encode(
            theta=alt.Theta(field='value', type='quantitative'),
            color=alt.Color('sentiment:N',
                          scale=alt.Scale(
                              domain=labels,
                              range=['#2ecc71', '#95a5a6', '#e74c3c']
                          ),
                          legend=alt.Legend(
                              title='Sentiment',
                              orient='right',
                              labelLimit=200
                          )),
            tooltip=['sentiment', 'value']
        ).properties(
            width=300,
            height=300,
        )
    
    @staticmethod
    def create_side_by_side_pie_charts(airlines_data, sentiment_data):
        # Create figure and subplots
        fig = plt.figure(figsize=(12, 6))
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        fig.subplots_adjust(wspace=0)
        
        # Airlines Pie Chart
        airline_labels = [selected_keyword1, selected_keyword3, selected_keyword4]
        airline_colors = ['#001F60', '#FFD700', '#EE2A29']
        
        # Calculate start angle to position the first wedge properly
        angle = -180 * airlines_data[0] / sum(airlines_data[:3])
        
        wedges1, texts1, autotexts1 = ax1.pie(
            airlines_data[:3],
            labels=airline_labels,
            colors=airline_colors, 
            autopct='%1.1f%%',
            startangle=angle,
            pctdistance=0.85,
            explode=[0, 0, 0],
            textprops={'color': 'black', 'size': 8}
        )
        
        # Sentiment Pie Chart
        sentiment_labels = ['Positive', 'Neutral', 'Negative']
        sentiment_colors = ['#3b7d23', '#7f7f7f', '#c00000']
        
        wedges2, texts2, autotexts2 = ax2.pie(
            sentiment_data[3:6],
            labels=sentiment_labels,
            colors=sentiment_colors, 
            autopct='%1.1f%%',
            startangle=angle,
            pctdistance=0.85,
            radius=0.8,
            textprops={'color': 'black', 'size': 8}
        )
        
        # Add connecting lines between charts
        theta1, theta2 = wedges1[0].theta1, wedges1[0].theta2
        center1, r1 = wedges1[0].center, wedges1[0].r
        center2, r2 = wedges2[0].center, wedges2[0].r
        
        # Calculate connection points
        x1_top = center1[0] 
        y1_top = center1[1] + r1  
        x1_bottom = center1[0]  
        y1_bottom = center1[1] - r1 
        
        x2_top = center2[0]
        y2_top = center2[1] + r2
        x2_bottom = center2[0]
        y2_bottom = center2[1] - r2
        
        # Add connecting lines
        con1 = ConnectionPatch(
            xyA=(x2_top, y2_top), 
            xyB=(x1_top, y1_top),
            coordsA="data", 
            coordsB="data", 
            axesA=ax2, 
            axesB=ax1,
            color="gray", 
            linestyle="--",
            linewidth=1
        )
        
        con2 = ConnectionPatch(
            xyA=(x2_bottom, y2_bottom), 
            xyB=(x1_bottom, y1_bottom),
            coordsA="data", 
            coordsB="data", 
            axesA=ax2, 
            axesB=ax1,
            color="gray", 
            linestyle="--",
            linewidth=1
        )
        
        ax2.add_artist(con1)
        ax2.add_artist(con2)
        
        return fig

    @staticmethod
    def create_daily_trendline_chart(daily_counts, color_key):
        # Get color based on airline name, defaulting to blue if not found
        color = color_mapping.get(color_key, "#001F60")
        # Create a copy of the DataFrame to avoid modifying the original
        df = daily_counts.copy()
        
        # Find top 3 peaks
        top_3_peaks = df.nlargest(3, 'Count')
        
        # Create base chart
        base = alt.Chart(df).encode(
            x=alt.X(
                'Date:N',  # Use nominal type for categorical data
                axis=alt.Axis(
                    labelAngle=45,
                    title=None
                )
            ),
            y=alt.Y(
                'Count:Q',  # Use quantitative type for numeric data
                axis=alt.Axis(title=None)
            )
        )
        
        # Create line chart with points
        line = base.mark_line(
            color=color,
            strokeWidth=2
        )
        
        points = base.mark_circle(
            color='#001F60',
            size=100
        )
        
        # Add peak annotations
        peak_labels = alt.Chart(top_3_peaks).mark_text(
            align='left',
            baseline='bottom',
            dx=5,
            dy=-10,
            fontSize=12,
            color='red'
        ).encode(
            x='Date:N',
            y='Count:Q',
            text=alt.Text('Count:Q', format='.0f')
        )
        
        # Combine all chart elements
        chart = (line + points + peak_labels).properties(
            width=600,
            height=400,
        ).configure_axis(
            grid=True,
            gridColor='#EAEAEA'
        ).configure_view(
            strokeWidth=0
        ).interactive()
        
        return chart
    
    @staticmethod
    def create_publications_horizontal_bar(df, color_key):
        # Get color based on airline name, defaulting to blue if not found
        color = color_mapping.get(color_key, "#001F60")

        # Create the chart
        chart = alt.Chart(df).mark_bar().encode(
            y=alt.Y('Source:N', sort='-x', title=None),
            x=alt.X('Volume:Q', axis=None),
            color=alt.value(color),
            tooltip=['Source', 'Volume']
        ).properties(
            width=600,
            height=400,
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        )
        
        return chart
    
    @staticmethod
    def create_get_top_authors(df, color_key):
        # Get color based on airline name, defaulting to blue if not found
        color = color_mapping.get(color_key, "#001F60")
        chart = alt.Chart(df).mark_bar().encode(
            y=alt.Y('Influencer:N', sort='-x', title=None),
            x=alt.X('Volume:Q', axis=None),
            color=alt.value(color),
            tooltip=['Influencer', 'Volume']
        ).properties(
            width=600,
            height=400,
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        )
        return chart
        
    @staticmethod
    def create_airlines_sentiment_overview(df):
        # Melt the DataFrame to convert sentiment columns to rows
        melted_df = df.melt(
            id_vars=['Keyword'],  # Changed from 'Airline' to 'Keyword'
            value_vars=['Positive', 'Neutral', 'Negative'],
            var_name='Sentiment',
            value_name='Count'
        )
        
        # Convert Count to numeric type
        melted_df['Count'] = pd.to_numeric(melted_df['Count'])
        
        # Calculate percentages within each keyword
        melted_df['Percentage'] = melted_df.groupby('Keyword')['Count'].transform(
            lambda x: x / x.sum() * 100
        )
        
        # Define orders with correct spelling
        keyword_order = [selected_keyword1, selected_keyword3, selected_keyword4]
        sentiment_order = ['Positive', 'Neutral', 'Negative']
        
        # Create the 100% stacked bar chart
        chart = alt.Chart(melted_df).mark_bar().encode(
            y=alt.Y('Keyword:N',  # Changed from 'Airline' to 'Keyword'
                    title=None,
                    sort=keyword_order),
            x=alt.X('Percentage:Q',
                    title=None,
                    stack='normalize',
                    axis=alt.Axis(format='%')),
            color=alt.Color('Sentiment:N', 
                        scale=alt.Scale(
                            domain=sentiment_order,
                            range=['#2ecc71', '#95a5a6', '#e74c3c']
                        )),
            order=alt.Order(
                'Sentiment',
                sort='descending'
            ),
            tooltip=[
                alt.Tooltip('Keyword:N'),  # Changed from 'Airline' to 'Keyword'
                alt.Tooltip('Sentiment:N'),
                alt.Tooltip('Percentage:Q', format='.1f', title='Percentage'),
                alt.Tooltip('Count:Q', title='Number of Articles')
            ]
        ).properties(
            width=1000,
            height=400,
        )
        
        return chart

    @staticmethod
    def create_prominence_score_chart_extra(df):
        """Create a bar chart showing prominence scores with average line using Altair"""
        # Create the base encoding for bars
        base_bars = alt.Chart(df).encode(
            x=alt.X('Keyword:N', sort=None, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Total Prominence:Q', 
                    title=None),
            # Add color encoding for bars
            color=alt.Color('Keyword:N',
                           scale=alt.Scale(
                               range=['#ff0000', '#039482', '#001F60']
                           ),
                           legend=alt.Legend(title='Keywords'))
        )

        # Create bars with dynamic colors
        bars = base_bars.mark_bar().encode(
            tooltip=[
                alt.Tooltip('Keyword:N'),
                alt.Tooltip('Total Prominence:Q', format='.2f'),
                alt.Tooltip('Average Prominence:Q', format='.2f')
            ]
        )

        # Create separate encoding for line
        base_line = alt.Chart(df).encode(
            x=alt.X('Keyword:N', sort=None),
            y=alt.Y('Average Prominence:Q',
                title=None,
                axis=alt.Axis(titleColor='red'))
        )

        # Create line
        line = base_line.mark_line(
            color='black'
        )

        # Create points for the line
        points = base_line.mark_circle(
            color='red',
            size=50
        )

        # Create text labels
        text = base_line.mark_text(
            align='center',
            baseline='bottom',
            dy=-5,
            color='red'
        ).encode(
            text=alt.Text('Average Prominence:Q', format='.2f')
        )

        # Layer the bars and line charts with different scales
        chart = alt.layer(bars, line + points + text).resolve_scale(
            y='independent'
        ).properties(
            width=600,
            height=400,
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        )

        return chart
