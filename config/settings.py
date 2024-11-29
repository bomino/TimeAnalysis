# app/config/settings.py

from dataclasses import dataclass, field
from typing import Dict, List
import yaml
import os
from pathlib import Path
from functools import partial

def default_moving_windows() -> List[int]:
    return [3, 6]

def default_color_palette() -> List[str]:
    return ['blue', 'green', 'red', 'purple', 'orange']

def default_export_formats() -> List[str]:
    return ['excel', 'csv', 'json']

def default_excel_sheets() -> Dict[str, str]:
    return {
        'yearly_growth': 'Yearly Growth',
        'monthly_growth': 'Monthly Growth',
        'seasonality': 'Seasonal Analysis',
        'dow_analysis': 'Day of Week Analysis',
        'anomalies': 'Anomaly Detection'
    }

@dataclass
class AnalysisSettings:
    # Time window settings
    min_months_for_seasonality: int = 12
    moving_average_windows: List[int] = field(default_factory=default_moving_windows)
    top_peak_months: int = 5
    
    # Anomaly detection settings
    anomaly_detection_window: int = 7
    anomaly_std_threshold: float = 2.0
    
    # Trend analysis settings
    trend_significance_threshold: float = 0.05
    correlation_strength_threshold: float = 0.7

@dataclass
class VisualizationSettings:
    # Chart settings
    default_chart_height: int = 400
    color_palette: List[str] = field(default_factory=default_color_palette)
    chart_template: str = 'plotly_white'
    
    # Heatmap settings
    heatmap_colorscale: str = 'Viridis'
    
    # Layout settings
    show_chart_legends: bool = True
    chart_animation: bool = True

@dataclass
class ExportSettings:
    # File export settings
    excel_sheet_names: Dict[str, str] = field(default_factory=default_excel_sheets)
    default_filename_prefix: str = 'time_analysis'
    export_formats: List[str] = field(default_factory=default_export_formats)

@dataclass
class AppSettings:
    # App display settings
    app_title: str = "Time Analysis Dashboard"
    app_icon: str = "📊"
    sidebar_state: str = "expanded"
    layout: str = "wide"
    theme_base: str = "light"
    
    # Page sections
    show_welcome_message: bool = True
    show_sample_data: bool = True
    enable_dark_mode: bool = True

@dataclass
class Config:
    analysis: AnalysisSettings = field(default_factory=AnalysisSettings)
    visualization: VisualizationSettings = field(default_factory=VisualizationSettings)
    export: ExportSettings = field(default_factory=ExportSettings)
    app: AppSettings = field(default_factory=AppSettings)

    @classmethod
    def load_from_yaml(cls, config_path: str = None):
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent / 'config.yaml'
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
                return cls(
                    analysis=AnalysisSettings(**config_dict.get('analysis', {})),
                    visualization=VisualizationSettings(**config_dict.get('visualization', {})),
                    export=ExportSettings(**config_dict.get('export', {})),
                    app=AppSettings(**config_dict.get('app', {}))
                )
        return cls()
    
    def save_to_yaml(self, config_path: str = None):
        """Save current configuration to YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent / 'config.yaml'
        
        config_dict = {
            'analysis': {
                k: v for k, v in self.analysis.__dict__.items()
            },
            'visualization': {
                k: v for k, v in self.visualization.__dict__.items()
            },
            'export': {
                k: v for k, v in self.export.__dict__.items()
            },
            'app': {
                k: v for k, v in self.app.__dict__.items()
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)

# Create default configuration file if it doesn't exist
if not os.path.exists(Path(__file__).parent / 'config.yaml'):
    Config().save_to_yaml()