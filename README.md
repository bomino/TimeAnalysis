
# **Time Analysis Dashboard**

The Time Analysis Dashboard is an interactive application designed to analyze transaction data and provide insights into time-based trends, seasonal patterns, growth metrics, and more. Built using Streamlit, this dashboard empowers users with advanced visualizations, anomaly detection, and correlation analysis to support data-driven decision-making.

---

## **Features**
- **Interactive Analysis**: Year-over-Year (YoY), Month-over-Month (MoM), and Quarterly Growth.
- **Time Patterns**: Seasonal trends, day-of-week analysis, peak spending periods.
- **Advanced Insights**: Anomalies, correlations, lead times.
- **Dynamic Configuration**: Easily customize settings via the app or config file.
- **Export Options**: Download analysis results in Excel, CSV, or JSON formats.
- **Visualizations**: Heatmaps, line charts, bar charts, and more powered by Plotly.

---

## **Setup Instructions**

### **1. Prerequisites**
- Python 3.8 or later
- A terminal or code editor (e.g., Visual Studio Code)
- Internet access to install dependencies

### **2. Install Dependencies**
```bash
git clone <repository-url>
cd <repository-directory>
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
pip install -r requirements.txt
```

### **3. Run the Application**
```bash
streamlit run app.py
```
Access the app in your browser at `http://localhost:8501`.

---

## **Usage**

### **Upload Data**
- Use the sidebar to upload a CSV file.
- Required columns:
  - `transaction_date` (in `YYYY-MM-DD` format)
  - `Total Spend ($)` (numeric)
  - `Quantity Purchased` (numeric)

### **Explore Features**
- Tabs for:
  - **Growth Analysis**: YoY, MoM, Quarterly trends, moving averages.
  - **Time Patterns**: Seasonal decomposition, day-of-week analysis.
  - **Advanced Insights**: Anomalies, lead time efficiency, correlations.
- Download results in Excel, CSV, or JSON formats.

### **Customize Settings**
- Modify `config/config.yaml` for:
  - Analysis thresholds.
  - Chart appearance.
  - Export preferences.

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

## **Known Issues**
- Ensure the uploaded CSV file is UTF-8 encoded.
- Missing required columns will cause errors.

---

## **Contributing**
Contributions are welcome! Fork the repository and submit a pull request.

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## **Contact**
For questions or feedback, reach out via:
- **Email**: [\[Your Email\]](Bomino@mlawali.com)
- **GitHub**: [\[Your GitHub Profile URL\]](https://github.com/bomino)
