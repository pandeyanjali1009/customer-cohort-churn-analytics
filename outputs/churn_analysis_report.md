# Customer Cohort and Churn Analytics Report

## Baseline
- Customers after cleaning: **7,043**
- Churned customers: **1,869**
- Retained customers: **5,174**
- Overall churn rate: **26.54%**
- Rows removed during cleaning/deduplication: **0**

## Highest-churn segment within each cut
- **TenureCohort = 0-12**: 47.44% churn across 2,186 customers.
- **Contract = Month-to-month**: 42.71% churn across 3,875 customers.
- **PaymentMethod = Electronic check**: 45.29% churn across 2,365 customers.
- **MonthlyChargeBand = (70.35, 89.85]**: 37.51% churn across 1,757 customers.
- **InternetService = Fiber optic**: 41.89% churn across 3,096 customers.
- **ServiceCount = 0.0**: 43.75% churn across 80 customers.
- **Fiber optic + no tech support**: 49.37% churn across 2,230 customers.

## Strategic retention recommendations
1. Prioritize new customers with onboarding check-ins and proactive issue resolution.
2. Test suitable annual-plan incentives for month-to-month customers; avoid blanket discounts.
3. Offer targeted technical-support outreach where fiber customers without support show elevated churn.
4. Investigate payment friction for payment methods with above-average churn.
5. Review high-monthly-charge segments for plan fit, perceived value and service quality.
6. Track segment churn over time and evaluate retention interventions before scaling them.

## Method and limitations
- Segment churn probability is the observed churn proportion within that segment, not an individual predictive-model score.
- Retention rate is calculated as 100% minus the observed churn rate.
- The supplied data is a cross-sectional snapshot with current tenure and churn status; it does not include monthly historical snapshots or signup dates.
- Therefore, this is a tenure-band retention matrix, not a true acquisition-month cohort retention curve.
- Segment relationships are descriptive and do not prove causation.
- Monthly charge bands are dataset-specific quartiles.

## Outputs
- Baseline and segment CSV summaries
- Tenure-band cohort retention matrix
- High-risk segment CSVs
- Interactive Plotly HTML charts in `outputs/charts/`