# Business brief

## Project
E-commerce Sales and Delivery Analytics on Cloud

## Context
This is an independent portfolio project using the public Olist dataset.
The business scenario is simulated. The project is not commissioned by Olist.

## Stakeholders
A simulated marketplace management team responsible for commercial
performance and delivery experience.

## Central question
What drives changes in merchandise GMV, which product categories and
regions contribute most, and which delivery problems are associated
with lower customer review scores?

## Business questions
1. How does monthly delivered merchandise GMV change?
2. Are changes driven by delivered order volume, AOV, or both?
3. Which categories and customer states contribute most to GMV?
4. Which high-volume categories or states also have high late-delivery rates?
5. How do review scores differ between late and on-time deliveries?
6. How often do customers purchase again within the observed period?

## Decisions supported
- Prioritize categories and regions for commercial investigation.
- Identify delivery performance issues for operational investigation.
- Assess whether the observed data supports further customer
  segmentation and retention analysis.

## Analytical scope
- Historical Olist data, not current market performance.
- Sales, category, customer state, delivery and review analysis.
- Repeat purchase and cohort analysis when data coverage permits.
- SQL as the main analytical tool, with Python for profiling,
  statistical analysis and figures.

## Exclusions
No claims about profit, platform net revenue, marketing ROI,
conversion rate or actual customer lifetime value.
The dataset does not establish causal effects.

## Deliverables
- Tested PostgreSQL analytical models built with dbt Core.
- Reproducible SQL and Python analyses.
- A public Streamlit dashboard.
- At least five evidence-backed findings and three recommendations.
- Documentation, an executive summary and a project demo.

## Success criteria
- KPI totals reconcile with the selected source population.
- Each finding has a reproducible query or analysis.
- Recommendations identify an action, target group and follow-up metric.
- The project remains within free service quotas.
