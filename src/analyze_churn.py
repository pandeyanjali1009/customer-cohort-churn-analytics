from pathlib import Path
import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "telco_customer_churn.csv"
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"

def segment_summary(df, cols):
    x = (df.groupby(cols, dropna=False)
         .agg(Customers=("Churn", "size"), Churned=("ChurnFlag", "sum"),
              Churn_Rate=("ChurnFlag", "mean"))
         .reset_index())
    x["Retention_Rate"] = (1 - x["Churn_Rate"]) * 100
    x["Churn_Rate"] = x["Churn_Rate"] * 100
    return x.sort_values("Customers", ascending=False)

def save_chart(fig, name):
    fig.write_html(CHARTS / name, include_plotlyjs="cdn")

def main():
    OUT.mkdir(exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)
    if not DATA.exists():
        raise FileNotFoundError("Dataset missing. Run `python download_data.py` from the project root.")

    df = pd.read_csv(DATA)
    df.columns = df.columns.str.strip()
    print("Raw dataset shape:", df.shape)
    required = ["customerID", "tenure", "Contract", "PaymentMethod", "MonthlyCharges", "Churn"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype("string").str.strip()
    df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce")
    df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors="coerce")
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["customerID", "tenure", "MonthlyCharges", "Churn"])
    df = df.drop_duplicates(subset=["customerID"])
    df = df[df["Churn"].isin(["Yes", "No"])].copy()
    removed = before - len(df)

    df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)
    df["RetentionFlag"] = (df["Churn"] == "No").astype(int)
    labels = ["0-12", "13-24", "25-36", "37-48", "49-60", "61-72"]
    df["TenureCohort"] = pd.cut(
        df["tenure"], bins=[-1, 12, 24, 36, 48, 60, 72],
        labels=labels, include_lowest=True
    ).astype("string")
    df["MonthlyChargeBand"] = pd.qcut(
        df["MonthlyCharges"], q=4, duplicates="drop"
    ).astype("string")

    service_cols = [c for c in [
        "PhoneService", "MultipleLines", "OnlineSecurity", "OnlineBackup",
        "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"
    ] if c in df.columns]
    df["ServiceCount"] = sum(
        (df[c].eq("Yes").astype(int) for c in service_cols),
        start=pd.Series(0, index=df.index, dtype="int64")
    )

    n = len(df)
    churned = int(df["ChurnFlag"].sum())
    retained = n - churned
    churn_rate = df["ChurnFlag"].mean() * 100
    pd.DataFrame([{
        "Total_Customers": n, "Churned_Customers": churned,
        "Retained_Customers": retained, "Churn_Rate_Percent": round(churn_rate, 2),
        "Retention_Rate_Percent": round(100 - churn_rate, 2),
        "Rows_Removed_During_Cleaning": removed
    }]).to_csv(OUT / "baseline_churn_summary.csv", index=False)

    specs = {
        "churn_by_tenure_cohort.csv": ["TenureCohort"],
        "churn_by_contract.csv": ["Contract"],
        "churn_by_payment_method.csv": ["PaymentMethod"],
        "churn_by_monthly_charge_band.csv": ["MonthlyChargeBand"],
        "churn_by_internet_service.csv": ["InternetService"],
        "churn_by_service_count.csv": ["ServiceCount"],
    }
    tables = {}
    for filename, cols in specs.items():
        if all(c in df.columns for c in cols):
            tables[filename] = segment_summary(df, cols)
            tables[filename].to_csv(OUT / filename, index=False)

    # Tenure-band retention matrix by contract type.
    matrix = (df.pivot_table(index="TenureCohort", columns="Contract",
                             values="RetentionFlag", aggfunc="mean", observed=False) * 100)
    matrix = matrix.reindex(labels).round(2)
    matrix.index.name = "Tenure_Cohort"
    matrix.to_csv(OUT / "cohort_retention_matrix.csv")

    # Inspect the example risk segment requested in the brief.
    risk = df[(df.get("InternetService") == "Fiber optic") &
              (df.get("TechSupport") == "No")]
    risk_rate = risk["ChurnFlag"].mean() * 100 if len(risk) else float("nan")
    pd.DataFrame([{
        "Segment": "Fiber optic + no tech support",
        "Customers": len(risk),
        "Churned": int(risk["ChurnFlag"].sum()) if len(risk) else 0,
        "Churn_Rate_Percent": round(risk_rate, 2) if len(risk) else None
    }]).to_csv(OUT / "example_high_risk_segment.csv", index=False)

    combo_cols = [c for c in ["Contract", "InternetService", "TechSupport", "PaymentMethod"] if c in df.columns]
    combo = (df.groupby(combo_cols, dropna=False)
             .agg(Customers=("Churn", "size"), Churned=("ChurnFlag", "sum"),
                  Churn_Rate=("ChurnFlag", "mean")).reset_index())
    combo = combo[combo["Customers"] >= max(20, int(n * .005))].copy()
    combo["Churn_Rate_Percent"] = (combo["Churn_Rate"] * 100).round(2)
    combo.sort_values(["Churn_Rate", "Customers"], ascending=[False, False]).drop(
        columns="Churn_Rate"
    ).to_csv(OUT / "high_risk_segment_combinations.csv", index=False)

    # Interactive charts.
    fig = px.pie(names=["Retained", "Churned"], values=[retained, churned],
                 title="Customer Retention vs Churn", hole=.45)
    save_chart(fig, "01_retention_vs_churn.html")

    t = tables["churn_by_tenure_cohort.csv"].sort_values("TenureCohort")
    fig = px.bar(t, x="TenureCohort", y="Churn_Rate", text="Churn_Rate",
                 title="Churn Rate by Tenure Cohort")
    save_chart(fig, "02_churn_by_tenure.html")
    fig = px.line(t, x="TenureCohort", y="Retention_Rate", markers=True,
                  title="Observed Retention by Tenure Band")
    fig.update_yaxes(range=[0, 100])
    save_chart(fig, "03_retention_by_tenure.html")

    fig = px.imshow(matrix, text_auto=".1f", aspect="auto",
                    color_continuous_scale="RdYlGn", zmin=0, zmax=100,
                    title="Tenure Cohort × Contract Retention Heatmap",
                    labels={"x": "Contract", "y": "Tenure cohort (months)", "color": "Retention %"})
    save_chart(fig, "04_cohort_contract_heatmap.html")

    chart_specs = [
        ("churn_by_contract.csv", "Contract", "Churn by Contract", "05_churn_by_contract.html"),
        ("churn_by_payment_method.csv", "PaymentMethod", "Churn by Payment Method", "06_churn_by_payment.html"),
        ("churn_by_internet_service.csv", "InternetService", "Churn by Service Tier", "07_churn_by_service_tier.html"),
        ("churn_by_service_count.csv", "ServiceCount", "Churn by Service Count", "08_churn_by_service_count.html"),
        ("churn_by_monthly_charge_band.csv", "MonthlyChargeBand", "Churn by Monthly Charges", "09_churn_by_monthly_charges.html"),
    ]
    for csv_name, col, title, html in chart_specs:
        if csv_name in tables:
            fig = px.bar(tables[csv_name], x=col, y="Churn_Rate", text="Churn_Rate", title=title)
            save_chart(fig, html)

    lines = [
        "# Customer Cohort and Churn Analytics Report", "",
        "## Baseline",
        f"- Customers after cleaning: **{n:,}**",
        f"- Churned customers: **{churned:,}**",
        f"- Retained customers: **{retained:,}**",
        f"- Overall churn rate: **{churn_rate:.2f}%**",
        f"- Rows removed during cleaning/deduplication: **{removed:,}**", "",
        "## Highest-churn segment within each cut"
    ]
    for filename, col in [
        ("churn_by_tenure_cohort.csv", "TenureCohort"),
        ("churn_by_contract.csv", "Contract"),
        ("churn_by_payment_method.csv", "PaymentMethod"),
        ("churn_by_monthly_charge_band.csv", "MonthlyChargeBand"),
        ("churn_by_internet_service.csv", "InternetService"),
        ("churn_by_service_count.csv", "ServiceCount")
    ]:
        if filename in tables and len(tables[filename]):
            top = tables[filename].sort_values("Churn_Rate", ascending=False).iloc[0]
            lines.append(f"- **{col} = {top[col]}**: {top['Churn_Rate']:.2f}% churn across {int(top['Customers']):,} customers.")
    if len(risk):
        lines.append(f"- **Fiber optic + no tech support**: {risk_rate:.2f}% churn across {len(risk):,} customers.")

    lines += [
        "", "## Strategic retention recommendations",
        "1. Prioritize new customers with onboarding check-ins and proactive issue resolution.",
        "2. Test suitable annual-plan incentives for month-to-month customers; avoid blanket discounts.",
        "3. Offer targeted technical-support outreach where fiber customers without support show elevated churn.",
        "4. Investigate payment friction for payment methods with above-average churn.",
        "5. Review high-monthly-charge segments for plan fit, perceived value and service quality.",
        "6. Track segment churn over time and evaluate retention interventions before scaling them.",
        "", "## Method and limitations",
        "- Segment churn probability is the observed churn proportion within that segment, not an individual predictive-model score.",
        "- Retention rate is calculated as 100% minus the observed churn rate.",
        "- The supplied data is a cross-sectional snapshot with current tenure and churn status; it does not include monthly historical snapshots or signup dates.",
        "- Therefore, this is a tenure-band retention matrix, not a true acquisition-month cohort retention curve.",
        "- Segment relationships are descriptive and do not prove causation.",
        "- Monthly charge bands are dataset-specific quartiles.",
        "", "## Outputs",
        "- Baseline and segment CSV summaries",
        "- Tenure-band cohort retention matrix",
        "- High-risk segment CSVs",
        "- Interactive Plotly HTML charts in `outputs/charts/`",
    ]
    (OUT / "churn_analysis_report.md").write_text("\n".join(lines), encoding="utf-8")
    df.to_csv(OUT / "telco_customer_churn_cleaned.csv", index=False)

    print("\n=== ANALYSIS COMPLETE ===")
    print(f"Customers: {n:,} | Churned: {churned:,} | Churn rate: {churn_rate:.2f}%")
    print("Review the outputs/ folder and open the HTML charts in a browser.")

if __name__ == "__main__":
    main()
