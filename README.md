# Customer Cohort and Churn Analytics

Python-based retention and churn analysis using the IBM Telco Customer Churn dataset.

## 🚀 Live Project Dashboard

**[Click Here to Explore the Interactive Dashboard](https://pandeyanjali1009.github.io/customer-cohort-churn-analytics/)**

Explore the complete project through the interactive dashboard, including:
- Customer Churn Analysis Report
- Interactive Cohort Retention Heatmap
- 8 Interactive Data Visualizations
- Key Findings and Business Recommendations

## Scope
- Baseline churn and retention rate
- Tenure cohorts (0–12 through 61–72 months)
- Contract, payment method, monthly charge and service-tier segmentation
- Service-count analysis
- Tenure-band retention matrix and heatmap
- High-risk segment analysis, including Fiber Optic customers without Tech Support
- Interactive Plotly charts, CSV summaries and a strategic recommendations report

## Tools
Python 3.11, Pandas, NumPy and Plotly. Power BI is not used.

## Windows PowerShell setup

Run these commands from the project root in Cursor:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python download_data.py
python src/analyze_churn.py
```

If activation is blocked in this terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If automatic download fails, download the CSV from:
https://www.datheon.in/datasets/telco_customer_churn.csv

Save it as `data/telco_customer_churn.csv`.

## Outputs
The analysis generates baseline and segment CSV files, `cohort_retention_matrix.csv`,
`high_risk_segment_combinations.csv`, a cleaned dataset, a Markdown report, and
interactive HTML charts in `outputs/charts/`.

## Important methodology note
The supplied dataset is a cross-sectional snapshot with current tenure and churn
status, not monthly historical snapshots or customer signup dates. The matrix is
therefore a **tenure-band retention matrix**, not a true acquisition-month cohort
retention curve. Segment churn rates are descriptive associations, not proof of
causation. "Churn probability" here means the observed churn proportion within a
segment; no individual machine-learning prediction is claimed.
