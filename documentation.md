
# **Time Analysis Dashboard**

## **Overview**
The Time Analysis Dashboard is an interactive application designed to analyze transaction data and provide insights into time-based trends, seasonal patterns, growth metrics, and more. Built using Streamlit, this dashboard empowers users with advanced visualizations, anomaly detection, and correlation analysis to support data-driven decision-making.

---

## **Features**
### **1. Interactive Analysis**
- **Growth Metrics**: Year-over-Year (YoY), Month-over-Month (MoM), Quarterly Growth.
- **Time Patterns**: Seasonal trends, day-of-week analysis, peak spending periods.
- **Advanced Insights**: Anomalies, correlations, lead times.

### **2. Dynamic Configuration**
- Customize analysis settings (e.g., thresholds for anomalies, chart properties).
- Save settings persistently using `config.yaml`.

### **3. Visualization**
- Visualizations powered by Plotly for interactivity.
- Heatmaps, line charts, bar charts, and more.

### **4. Export Options**
- Download analysis results in Excel, CSV, or JSON formats.

### **5. User-Friendly Interface**
- Sidebar for configuration and file uploads.
- Tabs for organized analysis.

---

## **Setup Instructions**

### **1. Prerequisites**
Ensure you have:
- Python 3.8 or later
- A working terminal or code editor
- Internet access to install dependencies

### **2. Install Dependencies**
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### **3. Run the Application**
Start the app by running:
```bash
streamlit run app.py
```

This will launch the dashboard in your default web browser at `http://localhost:8501`.

---

## **File Structure**
```
📁 project-root
├── app.py                 # Main Streamlit application
├── config/
│   ├── config_manager.py  # Configuration management
│   ├── config.yaml        # Default configuration file
│   └── settings.py        # Data classes for structured settings
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## **How to Use the Dashboard**

### **1. Upload Data**
- Use the sidebar to upload a CSV file.
- Required columns:
  - `transaction_date` (in `YYYY-MM-DD` format)
  - `Total Spend ($)` (numeric)
  - `Quantity Purchased` (numeric)

### **2. Explore Features**
- **Tabs for Insights**:
  - **Growth Analysis**: YoY, MoM, Quarterly trends, moving averages.
  - **Time Patterns**: Seasonal decomposition, day-of-week analysis.
  - **Advanced Insights**: Anomalies, lead time efficiency, correlations.
- **Download Results**:
  - Export analysis as Excel, CSV, or JSON.

### **3. Customize Settings**
- Use the sidebar to adjust parameters such as:
  - Anomaly detection thresholds.
  - Seasonal analysis settings.
  - Chart appearance.

---

## **Configuration**
Edit `config/config.yaml` or use the Settings Editor in the app. Key parameters include:

### **Analysis Settings**
```yaml
analysis:
  anomaly_detection_window: 7          # Rolling window for anomaly detection
  anomaly_std_threshold: 2.0           # Anomalies beyond 2 standard deviations
  min_months_for_seasonality: 12       # Minimum months required for seasonality
```

### **Visualization Settings**
```yaml
visualization:
  chart_template: plotly_white         # Chart template (e.g., plotly_white, plotly_dark)
  default_chart_height: 400            # Default chart height
  color_palette:                       # Custom colors for charts
    - '#1f77b4'
    - '#ff7f0e'
```

---

## **Known Issues**
- Non-UTF-8 encoded CSV files may cause errors. Ensure the file is saved with UTF-8 encoding.
- Missing required columns will result in an error message.

---

## **Future Enhancements**
- **Real-Time Data Integration**: Support for live data feeds.
- **Expanded Analysis**: Add more advanced statistical models.
- **Multi-language Support**: Localized versions of the dashboard.

---

## **Contributing**
Contributions are welcome! Please fork the repository and submit a pull request with detailed information about your changes.

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## **Contact**
For questions or feedback, please reach out to:
- **Email**: [\[Your Email\]](Bomino@mlawali.com)
- **GitHub**: [\[Your GitHub Profile URL\]](https://github.com/bomino)
