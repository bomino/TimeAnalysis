# app/config/config_manager.py

import streamlit as st
from .settings import Config
from pathlib import Path
import yaml

class ConfigManager:
    def __init__(self):
        self.config_path = Path(__file__).parent / 'config.yaml'
        self.config = Config.load_from_yaml(self.config_path)
    
    def show_config_editor(self):
        """Display configuration editor in Streamlit"""
        st.sidebar.markdown("### ⚙️ Settings")
        
        with st.sidebar.expander("Analysis Settings"):
            # Time window settings
            self.config.analysis.min_months_for_seasonality = st.number_input(
                "Minimum months for seasonality",
                min_value=6,
                max_value=24,
                value=self.config.analysis.min_months_for_seasonality
            )
            
            self.config.analysis.anomaly_std_threshold = st.slider(
                "Anomaly threshold (std dev)",
                min_value=1.0,
                max_value=4.0,
                value=float(self.config.analysis.anomaly_std_threshold),
                step=0.1
            )
            
            self.config.analysis.correlation_strength_threshold = st.slider(
                "Correlation strength threshold",
                min_value=0.1,
                max_value=1.0,
                value=float(self.config.analysis.correlation_strength_threshold),
                step=0.1
            )
        
        with st.sidebar.expander("Visualization Settings"):
            self.config.visualization.default_chart_height = st.number_input(
                "Default chart height",
                min_value=200,
                max_value=800,
                value=self.config.visualization.default_chart_height
            )
            
            self.config.visualization.chart_template = st.selectbox(
                "Chart template",
                options=['plotly_white', 'plotly_dark', 'simple_white'],
                index=0
            )
            
            self.config.visualization.show_chart_legends = st.checkbox(
                "Show chart legends",
                value=self.config.visualization.show_chart_legends
            )
        
        with st.sidebar.expander("Export Settings"):
            self.config.export.default_filename_prefix = st.text_input(
                "Default filename prefix",
                value=self.config.export.default_filename_prefix
            )
            
            export_formats = st.multiselect(
                "Export formats",
                options=['excel', 'csv', 'json'],
                default=self.config.export.export_formats
            )
            if export_formats:
                self.config.export.export_formats = export_formats
        
        with st.sidebar.expander("App Settings"):
            self.config.app.app_title = st.text_input(
                "App title",
                value=self.config.app.app_title
            )
            
            self.config.app.theme_base = st.selectbox(
                "Theme",
                options=['light', 'dark'],
                index=0 if self.config.app.theme_base == 'light' else 1
            )
            
            self.config.app.show_welcome_message = st.checkbox(
                "Show welcome message",
                value=self.config.app.show_welcome_message
            )
        
        # Save button
        if st.sidebar.button("💾 Save Settings"):
            self.save_config()
            st.sidebar.success("Settings saved successfully!")
    
    def save_config(self):
        """Save current configuration to file"""
        self.config.save_to_yaml(self.config_path)
    
    def get_config(self):
        """Get current configuration"""
        return self.config