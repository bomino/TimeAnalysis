# app/main.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import json
from statsmodels.tsa.seasonal import seasonal_decompose
import io
import base64
from config.config_manager import ConfigManager


    # Initialize configuration
config_manager = ConfigManager()
config = config_manager.get_config()
    
    # Set page config from settings
st.set_page_config(
        page_title=config.app.app_title,
        page_icon=config.app.app_icon,
        layout=config.app.layout,
        initial_sidebar_state=config.app.sidebar_state
    )



# Custom CSS for styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
    }
    .reportTitle {
        font-size: 24px;
        font-weight: bold;
        color: #1f1f1f;
    }
    .stAlert > div {
        padding: 0.5rem 0.5rem;
        margin-bottom: 1rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)



class TimeAnalyzer:
    def __init__(self, df,config=None):

        """
        Initialize TimeAnalyzer with data and configuration
        
        Parameters:
        -----------
        df : pandas.DataFrame
            Input dataframe containing transaction data
        config : Config object
            Configuration settings for analysis
        """
        self.df = df
        self.df['transaction_date'] = pd.to_datetime(self.df['transaction_date'])
        self.config = config
        self.prepare_data()


    def prepare_data(self):
        """Prepare data with additional time-based columns"""
        self.df['year'] = self.df['transaction_date'].dt.year
        self.df['month'] = self.df['transaction_date'].dt.month
        self.df['quarter'] = self.df['transaction_date'].dt.quarter
        self.df['month_year'] = self.df['transaction_date'].dt.strftime('%Y-%m')
        self.df['day_of_week'] = self.df['transaction_date'].dt.day_name()

    def analyze_seasonality(self):
            """Analyze seasonal patterns in the data"""
            try:
                # Monthly aggregation for seasonal analysis
                monthly_spend = self.df.groupby('month_year')['Total Spend ($)'].sum()

                # Get minimum months from config or use default
                min_months = (self.config.analysis.min_months_for_seasonality 
                        if self.config else 12)
                
                if len(monthly_spend) >= min_months:
                    # Perform seasonal decomposition
                    decomposition = seasonal_decompose(monthly_spend, period=12)
                    
                    # Extract components
                    seasonal = decomposition.seasonal
                    trend = decomposition.trend
                    residual = decomposition.resid
                    
                    # Calculate seasonal strength
                    total_variance = float(residual.var() + seasonal.var())
                    seasonal_strength = float((seasonal.var() / total_variance * 100).round(2))
                    
                    # Calculate monthly seasonal factors
                    seasonal_factors = seasonal.groupby(seasonal.index.str[5:7]).mean()
                    
                    # Identify peak and trough seasons
                    peak_month = seasonal_factors.idxmax()
                    trough_month = seasonal_factors.idxmin()
                    
                    return {
                        'has_seasonality': True,
                        'seasonal_strength': seasonal_strength,
                        'peak_month': peak_month,
                        'trough_month': trough_month,
                        'seasonal_factors': {str(k): float(v) for k, v in seasonal_factors.to_dict().items()},
                        'components': {
                            'seasonal': {str(k): float(v) for k, v in seasonal.to_dict().items()},
                            'trend': {str(k): float(v) for k, v in trend.to_dict().items()},
                            'residual': {str(k): float(v) for k, v in residual.to_dict().items()}
                        }
                    }
                else:
                    return {
                        'has_seasonality': False,
                        'message': "Insufficient data for seasonal analysis (need at least {min_months} months)"
                    }
            except Exception as e:
                print(f"Error in seasonal analysis: {str(e)}")
                return {
                    'has_seasonality': False,
                    'message': f"Error in seasonal analysis: {str(e)}"
            }


    def enhanced_time_analysis(self):
        """Enhanced time-based analysis of transactions"""
        try:
            # Basic Analysis
            yearly_spend = self.df.groupby('year')['Total Spend ($)'].sum()
            yoy_growth = yearly_spend.pct_change() * 100
            
            quarterly_spend = self.df.groupby(['year', 'quarter'])['Total Spend ($)'].sum()
            qoq_growth = quarterly_spend.pct_change() * 100
            
            monthly_spend = self.df.groupby('month_year')['Total Spend ($)'].sum()
            mom_growth = monthly_spend.pct_change() * 100
            
            moving_averages = {
                'ma3': monthly_spend.rolling(window=3).mean(),
                'ma6': monthly_spend.rolling(window=6).mean()
            }
            
            peak_months = (
                self.df.groupby('month_year')['Total Spend ($)']
                .sum()
                .nlargest(5)
                .to_frame()
                .reset_index()
            )
            
            # Day of Week Analysis
            dow_stats = pd.DataFrame({
                'Total Spend': self.df.groupby('day_of_week')['Total Spend ($)'].sum(),
                'Average Spend': self.df.groupby('day_of_week')['Total Spend ($)'].mean(),
                'Transaction Count': self.df.groupby('day_of_week')['Total Spend ($)'].count(),
                'Total Quantity': self.df.groupby('day_of_week')['Quantity Purchased'].sum()
            }).round(2)

            # Advanced Analysis
            trend_metrics = self.calculate_trend_metrics()
            anomalies = self.detect_anomalies()
            purchase_patterns = self.analyze_purchase_patterns()
            correlations = self.analyze_correlations()
            seasonality = self.analyze_seasonality()

            return {
                'yearly_growth': {str(k): float(v) for k, v in yoy_growth.to_dict().items()},
                'quarterly_growth': {f"{k[0]}-Q{k[1]}": v for k, v in qoq_growth.to_dict().items()},
                'monthly_growth': {str(k): float(v) for k, v in mom_growth.to_dict().items()},
                'moving_average_3m': {str(k): float(v) for k, v in moving_averages['ma3'].to_dict().items()},
                'moving_average_6m': {str(k): float(v) for k, v in moving_averages['ma6'].to_dict().items()},
                'peak_months': peak_months.to_dict('records'),
                'day_of_week_stats': {k: {str(i): float(j) for i, j in v.items()} for k, v in dow_stats.to_dict().items()},
                'raw_monthly_spend': {str(k): float(v) for k, v in monthly_spend.to_dict().items()},
                'trend_analysis': trend_metrics,
                'anomalies': anomalies,
                'purchase_patterns': purchase_patterns,
                'correlations': correlations,
                'seasonality_metrics': seasonality
            }
        except Exception as e:
            st.error(f"Error in analysis: {str(e)}")
            return None

 
        
        # 1. Trend Analysis
    def calculate_trend_metrics(self):
        """Calculate trend-related metrics"""
        try:
            monthly_spend = self.df.groupby('month_year')['Total Spend ($)'].sum()
            
            # Calculate trend direction and strength
            trend_changes = monthly_spend.pct_change()
            trend_direction = 'Upward' if trend_changes.mean() > 0 else 'Downward'
            trend_strength = abs(trend_changes.mean()) * 100
            
            # Identify acceleration/deceleration
            acceleration = trend_changes.pct_change()
            is_accelerating = bool(acceleration.mean() > 0)  # Convert numpy.bool_ to Python bool
            
            return {
                'direction': str(trend_direction),
                'strength': float(trend_strength),
                'is_accelerating': is_accelerating,
                'acceleration_rate': float(acceleration.mean() * 100)
            }
        except Exception as e:
            print(f"Error in trend metrics: {str(e)}")
            return {
                'direction': 'Unknown',
                'strength': 0.0,
                'is_accelerating': False,
                'acceleration_rate': 0.0
            }

        # 2. Anomaly Detection
    def detect_anomalies(self):
        """Detect anomalies in spending patterns"""
        try:
            daily_spend = self.df.groupby('transaction_date')['Total Spend ($)'].sum()

            # Get anomaly threshold from config or use default
            threshold = (self.config.analysis.anomaly_std_threshold 
                       if self.config else 2.0)
            window = (self.config.analysis.anomaly_detection_window 
                     if self.config else 7)
            
            # Calculate rolling statistics
            rolling_mean = daily_spend.rolling(window=window, min_periods=1).mean()
            rolling_std = daily_spend.rolling(window=window, min_periods=1).std()
            
            # Define anomalies as values outside threshold standard deviations
            anomalies = daily_spend[abs(daily_spend - rolling_mean) > (threshold * rolling_std)]
            
            return {
                'anomalies': {str(k): float(v) for k, v in anomalies.to_dict().items()},
                'anomaly_dates': [d.strftime('%Y-%m-%d') for d in anomalies.index],
                'total_anomalies': int(len(anomalies))
            }
        except Exception as e:
            print(f"Error in anomaly detection: {str(e)}")
            return {
                'anomalies': {},
                'anomaly_dates': [],
                'total_anomalies': 0
            }
        

        # 3. Customer Purchase Patterns
    def analyze_purchase_patterns(self):
        """Analyze customer purchase patterns"""
        try:
            # Average order value trends
            monthly_aov = (self.df.groupby('month_year')['Total Spend ($)'].sum() /
               self.df.groupby('month_year').size()).round(2)
 
            
            # Purchase frequency
            customer_frequency = self.df.groupby('month_year').size()
            
            # Basket size analysis
            basket_size = self.df.groupby('month_year')['Quantity Purchased'].mean().round(2)
            
            return {
                'monthly_aov': {str(k): float(v) for k, v in monthly_aov.to_dict().items()},
                'purchase_frequency': {str(k): int(v) for k, v in customer_frequency.to_dict().items()},
                'basket_size': {str(k): float(v) for k, v in basket_size.to_dict().items()}
            }
        except Exception as e:
            print(f"Error in purchase pattern analysis: {str(e)}")
            return {
                'monthly_aov': {},
                'purchase_frequency': {},
                'basket_size': {}
            }

        # 4. Lead Time Analysis
    def analyze_lead_times(self):
            # Monthly average lead times
            monthly_lead_times = self.df.groupby('month_year')['Lead Time (Days)'].mean().round(2)
            
            # Lead time distribution
            lead_time_distribution = self.df['Lead Time (Days)'].value_counts().sort_index()
            
            # Lead time efficiency
            lead_time_efficiency = (
                self.df.groupby('month_year')
                .apply(lambda x: (x['Lead Time (Days)'] <= x['Lead Time (Days)'].median()).mean() * 100)
                .round(2)
            )
            
            return {
                'monthly_lead_times': monthly_lead_times.to_dict(),
                'lead_time_distribution': lead_time_distribution.to_dict(),
                'lead_time_efficiency': lead_time_efficiency.to_dict()
            }

    # 5. Correlation Analysis
    def analyze_correlations(self):
        """Analyze correlations between metrics"""
        try:
            correlations = {
                'spend_quantity': float(self.df['Total Spend ($)'].corr(self.df['Quantity Purchased'])),
                'spend_leadtime': float(self.df['Total Spend ($)'].corr(self.df['Lead Time (Days)'])),
                'quantity_leadtime': float(self.df['Quantity Purchased'].corr(self.df['Lead Time (Days)']))
            }
            return correlations
        except Exception as e:
            print(f"Error in correlation analysis: {str(e)}")
            return {
                'spend_quantity': 0.0,
                'spend_leadtime': 0.0,
                'quantity_leadtime': 0.0
            }

        
        

def create_advanced_visualizations(results):
    """Create visualizations for advanced analysis"""
    
    def create_anomaly_chart(anomalies, monthly_spend):
        """Create anomaly detection chart"""
        fig = go.Figure()
        
        # Add regular spending line
        fig.add_trace(go.Scatter(
            x=list(monthly_spend.keys()),
            y=list(monthly_spend.values()),
            name="Regular Spend",
            line=dict(color="blue")
        ))
        
        # Add anomalies as points
        if anomalies:
            fig.add_trace(go.Scatter(
                x=list(anomalies.keys()),
                y=list(anomalies.values()),
                mode='markers',
                name="Anomalies",
                marker=dict(color="red", size=10)
            ))
        
        fig.update_layout(
            title="Spending Pattern with Anomalies",
            xaxis_title="Date",
            yaxis_title="Total Spend ($)",
            template="plotly_white",
            height=400
        )
        return fig

    def create_lead_time_chart(lead_time_data):
        """Create lead time analysis chart"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Monthly Average Lead Times", "Lead Time Efficiency")
        )
        
        # Monthly average lead times
        fig.add_trace(
            go.Scatter(
                x=list(lead_time_data['monthly_lead_times'].keys()),
                y=list(lead_time_data['monthly_lead_times'].values()),
                name="Avg Lead Time"
            ),
            row=1, col=1
        )
        
        # Lead time efficiency
        fig.add_trace(
            go.Bar(
                x=list(lead_time_data['lead_time_efficiency'].keys()),
                y=list(lead_time_data['lead_time_efficiency'].values()),
                name="Efficiency %"
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=700, showlegend=True)
        return fig

    def create_purchase_patterns_chart(patterns):
        """Create purchase patterns visualization"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Average Order Value",
                "Purchase Frequency",
                "Average Basket Size",
                "Trend Analysis"
            )
        )
        
        # Average Order Value
        fig.add_trace(
            go.Scatter(
                x=list(patterns['monthly_aov'].keys()),
                y=list(patterns['monthly_aov'].values()),
                name="AOV"
            ),
            row=1, col=1
        )
        
        # Purchase Frequency
        fig.add_trace(
            go.Bar(
                x=list(patterns['purchase_frequency'].keys()),
                y=list(patterns['purchase_frequency'].values()),
                name="Frequency"
            ),
            row=1, col=2
        )
        
        # Basket Size
        fig.add_trace(
            go.Scatter(
                x=list(patterns['basket_size'].keys()),
                y=list(patterns['basket_size'].values()),
                name="Basket Size"
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=800, showlegend=True)
        return fig

    def create_correlation_heatmap(correlations):
        """Create correlation heatmap"""
        # Reshape correlation data for heatmap
        corr_matrix = pd.DataFrame([
            ['Spend', 'Quantity', correlations['spend_quantity']],
            ['Spend', 'Lead Time', correlations['spend_leadtime']],
            ['Quantity', 'Lead Time', correlations['quantity_leadtime']]
        ])
        
        fig = px.imshow(
            corr_matrix,
            labels=dict(x="Metric 1", y="Metric 2", color="Correlation"),
            color_continuous_scale="RdBu",
            aspect="auto"
        )
        
        fig.update_layout(
            title="Correlation Analysis",
            height=400
        )
        return fig

    return {
        'anomaly_chart': create_anomaly_chart(
            results['anomalies']['anomalies'],
            results['raw_monthly_spend']
        ),
        'lead_time_chart': create_lead_time_chart(results['lead_time_analysis']),
        'purchase_patterns': create_purchase_patterns_chart(results['purchase_patterns']),
        'correlation_heatmap': create_correlation_heatmap(results['correlations'])
    }


def create_growth_chart(data, title):
    """Create an interactive line chart for growth metrics"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(data.keys()),
        y=list(data.values()),
        mode='lines+markers',
        name=title,
        line=dict(width=3)
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Period",
        yaxis_title="Growth (%)",
        template=config.visualization.chart_template,
        height=config.visualization.default_chart_height,
        showlegend=config.visualization.show_chart_legends
    )
    return fig

def create_dow_heatmap(data):
    """Create a heatmap for day of week analysis"""
    df = pd.DataFrame(data)
    fig = px.imshow(
        df,
        labels=dict(x="Metric", y="Day of Week", color="Value"),
        aspect="auto",
        color_continuous_scale=config.visualization.heatmap_colorscale
    )
    fig.update_layout(
        title="Day of Week Analysis Heatmap",
        height=config.visualization.default_chart_height,
        template=config.visualization.chart_template
    )
    return fig

def create_monthly_spend_chart(monthly_spend):
    """Create a bar chart for monthly spending"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(monthly_spend.keys()),
        y=list(monthly_spend.values()),
        name="Monthly Spend",
        marker_color=config.visualization.color_palette[0]
    ))
    fig.update_layout(
        title="Monthly Spending Pattern",
        xaxis_title="Month",
        yaxis_title="Total Spend ($)",
        
        template=config.visualization.chart_template,
        height=config.visualization.default_chart_height,
        showlegend=config.visualization.show_chart_legends
    )
    return fig


def convert_df_to_csv(df):
    """Convert DataFrame to CSV format for download"""
    return df.to_csv(index=True).encode('utf-8')

def convert_df_to_excel(df_dict):
    """Convert dictionary of DataFrames to Excel format for download"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name)
    return output.getvalue()

def prepare_analysis_for_excel(results):
    """Prepare analysis results as a dictionary of DataFrames for Excel export"""
    excel_dict = {}
    
    # Yearly Growth
    yearly_growth_df = pd.DataFrame(results['yearly_growth'].items(), 
                                  columns=['Year', 'Growth (%)'])
    excel_dict['Yearly Growth'] = yearly_growth_df
    
    # Monthly Growth
    monthly_growth_df = pd.DataFrame(results['monthly_growth'].items(), 
                                   columns=['Month', 'Growth (%)'])
    excel_dict['Monthly Growth'] = monthly_growth_df
    
    # Quarterly Growth
    quarterly_growth_df = pd.DataFrame(results['quarterly_growth'].items(), 
                                     columns=['Quarter', 'Growth (%)'])
    excel_dict['Quarterly Growth'] = quarterly_growth_df
    
    # Peak Months
    peak_months_df = pd.DataFrame(results['peak_months'])
    excel_dict['Peak Months'] = peak_months_df
    
    # Day of Week Stats
    dow_stats_df = pd.DataFrame(results['day_of_week_stats'])
    excel_dict['Day of Week Analysis'] = dow_stats_df
    
    # Moving Averages
    ma_df = pd.DataFrame({
        'Month': results['moving_average_3m'].keys(),
        '3-Month MA': results['moving_average_3m'].values(),
        '6-Month MA': results['moving_average_6m'].values()
    })
    excel_dict['Moving Averages'] = ma_df
    
    # Monthly Spend
    monthly_spend_df = pd.DataFrame(list(results['raw_monthly_spend'].items()),
                                  columns=['Month', 'Total Spend'])
    excel_dict['Monthly Spend'] = monthly_spend_df
    
    # Seasonality Metrics (if available)
    if results['seasonality_metrics']:
        seasonal_df = pd.DataFrame({
            'Metric': ['Seasonal Strength'],
            'Value': [results['seasonality_metrics']['seasonal_strength']]
        })
        excel_dict['Seasonality'] = seasonal_df
    
    return excel_dict

def show_download_section(results):
    """Display download options and handle downloads"""
    st.markdown("### 📥 Download Analysis Results")
    st.markdown("""
        Choose your preferred format:
        - **Excel**: Complete report with all analyses in separate sheets
        - **CSV**: Individual CSV files for each analysis
        - **JSON**: Raw data in JSON format
    """)
    
    # Prepare data for different formats
    excel_dict = prepare_analysis_for_excel(results)
    
    # Excel download
    excel_data = convert_df_to_excel(excel_dict)
    
    # JSON string
    json_str = json.dumps(results, indent=2)
    
    # Create download buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📥 Download Excel Report",
            data=excel_data,
            file_name="time_analysis_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        for sheet_name, df in excel_dict.items():
            csv_data = convert_df_to_csv(df)
            st.download_button(
                label=f"📥 Download {sheet_name} (CSV)",
                data=csv_data,
                file_name=f"time_analysis_{sheet_name.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
    
    with col3:
        st.download_button(
            label="📥 Download JSON Report",
            data=json_str,
            file_name="time_analysis_results.json",
            mime="application/json"
        )

def main():

    
    # Show configuration editor in sidebar
    config_manager.show_config_editor()
    

    st.title("📊 Advanced Time Analysis Dashboard")
    
    # File upload section
    st.sidebar.header("📁 Upload Data")
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Load and analyze data
            df = pd.read_csv(uploaded_file)
            
            # Verify required columns
            required_columns = ['transaction_date', 'Total Spend ($)', 'Quantity Purchased']
            if not all(col in df.columns for col in required_columns):
                st.error("""
                    Missing required columns. Please ensure your CSV contains:
                    - transaction_date
                    - Total Spend ($)
                    - Quantity Purchased
                """)
                return
                
        # Initialize analyzer with configuration settings
            analyzer = TimeAnalyzer(df, config)
            
            # Run analysis
            with st.spinner('Analyzing data...'):
                results = analyzer.enhanced_time_analysis()
            
            if results:
                # Create tabs for different analyses
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📈 Growth Analysis", 
                    "📊 Patterns", 
                    "📑 Summary", 
                    "🔍 Advanced Insights"
                ])
                
                with tab1:
                    # Apply visualization settings from config
                    chart_height = config.visualization.default_chart_height
                    chart_template = config.visualization.chart_template
                    show_legends = config.visualization.show_chart_legends

                    st.header("Growth Metrics")
                    
                    # Show total metrics
                    total_spend = df['Total Spend ($)'].sum()
                    total_transactions = len(df)
                    avg_spend = df['Total Spend ($)'].mean()
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Spend", f"${total_spend:,.2f}")
                    col2.metric("Total Transactions", f"{total_transactions:,}")
                    col3.metric("Average Spend", f"${avg_spend:.2f}")
                    
                    st.markdown("---")
                    
                    # Growth charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.plotly_chart(
                            create_growth_chart(
                                results['yearly_growth'],
                                "Year-over-Year Growth"
                            ),
                            use_container_width=True
                        )
                    
                    with col2:
                        st.plotly_chart(
                            create_growth_chart(
                                results['monthly_growth'],
                                "Month-over-Month Growth"
                            ),
                            use_container_width=True
                        )
                    
                    # Monthly spend pattern
                    st.plotly_chart(
                        create_monthly_spend_chart(results['raw_monthly_spend']),
                        use_container_width=True
                    )
                
                with tab2:
                    st.header("Time Patterns")
                    
                    # Day of Week Analysis
                    st.plotly_chart(
                        create_dow_heatmap(results['day_of_week_stats']),
                        use_container_width=True
                    )
                    
                    # Show day of week stats in table format
                    st.markdown("### Daily Transaction Patterns")
                    dow_df = pd.DataFrame(results['day_of_week_stats'])
                    st.dataframe(dow_df)
                    
                    # Seasonal Analysis
                    if results['seasonality_metrics']:
                        st.markdown("### Seasonal Analysis")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(
                                "Seasonal Strength",
                                f"{results['seasonality_metrics']['seasonal_strength']:.1f}%"
                            )
                
                with tab3:
                    st.header("Analysis Summary")
                    
                    # Peak Months
                    st.subheader("Top 5 Peak Spending Periods")
                    peak_df = pd.DataFrame(results['peak_months'])
                    st.dataframe(peak_df)
                    
                    # Moving Averages
                    st.subheader("Moving Averages")
                    ma_df = pd.DataFrame({
                        'Month': results['moving_average_3m'].keys(),
                        '3-Month MA': results['moving_average_3m'].values(),
                        '6-Month MA': results['moving_average_6m'].values()
                    })
                    st.dataframe(ma_df)
                    
                    # Downloads section
                    st.markdown("---")
                    show_download_section(results)


                # In tab4
                with tab4:
                    st.header("Advanced Insights")
                    
                    # Trend Analysis
                    st.subheader("📈 Trend Analysis")
                    trend = results['trend_analysis']
                    col1, col2, col3 = st.columns(3)
                    col1.metric(
                        "Trend Direction",
                        trend['direction'],
                        delta="Accelerating" if trend['is_accelerating'] else "Decelerating"
                    )
                    col2.metric(
                        "Trend Strength",
                        f"{trend['strength']:.1f}%"
                    )
                    col3.metric(
                        "Rate of Change",
                        f"{trend['acceleration_rate']:.1f}%"
                    )
                    
                    # Anomalies
                    st.subheader("🔍 Anomaly Detection")
                    anomalies = results['anomalies']
                    col1, col2 = st.columns(2)
                    col1.metric("Total Anomalies Detected", anomalies['total_anomalies'])
                    if anomalies['total_anomalies'] > 0:
                        with col2.expander("View Anomaly Dates"):
                            st.write(anomalies['anomaly_dates'])
                    
                    # Purchase Patterns
                    st.subheader("🛒 Purchase Patterns")
                    patterns = results['purchase_patterns']
                    col1, col2, col3 = st.columns(3)
                    
                    # Latest values
                    latest_aov = list(patterns['monthly_aov'].values())[-1]
                    latest_freq = list(patterns['purchase_frequency'].values())[-1]
                    latest_basket = list(patterns['basket_size'].values())[-1]
                    
                    col1.metric("Average Order Value", f"${latest_aov:,.2f}")
                    col2.metric("Monthly Transactions", latest_freq)
                    col3.metric("Average Basket Size", f"{latest_basket:.1f} items")
                    
                    # Correlation Analysis
                    st.subheader("🔗 Correlation Analysis")
                    corr = results['correlations']
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric(
                        "Spend vs Quantity",
                        f"{corr['spend_quantity']:.2f}",
                        delta="Strong" if abs(corr['spend_quantity']) > 0.7 else "Moderate"
                    )
                    col2.metric(
                        "Spend vs Lead Time",
                        f"{corr['spend_leadtime']:.2f}",
                        delta="Strong" if abs(corr['spend_leadtime']) > 0.7 else "Moderate"
                    )
                    col3.metric(
                        "Quantity vs Lead Time",
                        f"{corr['quantity_leadtime']:.2f}",
                        delta="Strong" if abs(corr['quantity_leadtime']) > 0.7 else "Moderate"
                    )
                    
                    # Key Insights
                    st.subheader("🎯 Key Insights")
                    insights = []
                    
                    # Trend insights
                    insights.append(
                        f"📈 The overall trend is {trend['direction'].lower()} "
                        f"with {trend['strength']:.1f}% strength and is "
                        f"{'accelerating' if trend['is_accelerating'] else 'decelerating'}."
                    )
                    
                    # Anomaly insights
                    if anomalies['total_anomalies'] > 0:
                        insights.append(
                            f"🔍 Detected {anomalies['total_anomalies']} anomalies in spending patterns."
                        )
                    
                    # Correlation insights
                    for metric, value in corr.items():
                        if abs(value) > 0.7:
                            relationship = "strong positive" if value > 0 else "strong negative"
                            metrics = metric.replace('_', ' vs ')
                            insights.append(f"🔗 Found {relationship} correlation between {metrics}.")
                    
                    for insight in insights:
                        st.markdown(insight)   

        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.info("""
                Please ensure your CSV file:
                1. Contains the required columns
                2. Has proper date format (YYYY-MM-DD)
                3. Has numeric values for spend and quantity
            """)
    
    else:
        if config.app.show_welcome_message:
            st.markdown("""
                ### 👋 Welcome to the **Time Analysis Dashboard!**

                ### Overview
                The **Time Analysis Dashboard** is an interactive tool designed to analyze transaction data and provide insights into:
                - Growth metrics (Year-over-Year, Month-over-Month)
                - Seasonal trends and time-based patterns
                - Anomalies and correlations

                ### Key Features
                - **Data Analysis**:
                - Year-over-Year Growth Analysis
                - Monthly Patterns
                - Day of Week Analysis
                - Seasonal Decomposition
                - **Visualizations**:
                - Heatmaps, trend lines, and bar charts powered by Plotly
                - **Customizations**:
                - Tailor thresholds, templates, and parameters via a simple interface
                - **Reporting**:
                - Downloadable Reports in Excel, CSV, or JSON formats

                ### Built With
                - Python (Streamlit, Pandas, Plotly)
                - Statsmodels for seasonal decomposition
                - Open-source libraries for data analysis

                ### Contact
                For questions or feedback, reach out via:
                - **Email**: Bomino@mlawali.com
                - **GitHub**: [https://github.com/bomino](https://github.com/bomino)

                ### Getting Started
                This tool helps you analyze your transaction data over time. To get started:
                
                1. Upload your CSV file using the sidebar
                2. Wait for the analysis to complete
                3. Explore different visualizations in the tabs
                4. Download the complete analysis results
                
                ### Required CSV Format
                Your file should follow this structure:
                ```csv
                transaction_date,Total Spend ($),Quantity Purchased
                2023-01-01,1000.50,5
                2023-01-02,750.25,3
                ```
            """)




if __name__ == "__main__":
    main()        