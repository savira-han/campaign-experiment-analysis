# Campaign Experiment Analysis

An A/B testing analysis of a Google Ads hotel campaign experiment for an online travel platform.

The experiment compares two hotel inventory strategies to understand whether a more curated campaign can improve paid booking conversion.

## 01 - Business Question

**Which campaign strategy is more effective at generating paid hotel bookings?**

* **Control (Campaign A):** promotes the top 100 hotels across the full hotel inventory.
* **Treatment (Campaign B):** promotes the top 100 hotels within the three highest-priority destinations: Jakarta, Bali, and Bandung.

The goal is to measure whether narrowing the promoted inventory changes booking conversion and campaign economics.

## 02 - Experiment Design

The experiment is structured as a Google Ads campaign experiment with approximately 50/50 traffic allocation.

| Component                   | Definition                                |
| --------------------------- | ----------------------------------------- |
| Experiment duration         | 28 days                                   |
| Conversion window           | 7 days after eligible click               |
| Post-experiment observation | 7 days                                    |
| Primary unit                | Campaign click                            |
| Primary metric              | Click-to-Paid-Transaction Conversion Rate |
| Control                     | Top 100 hotels across full inventory      |
| Treatment                   | Top 100 hotels in Jakarta, Bali, Bandung  |

The primary metric is calculated as:

```text
Converting Clicks / Eligible Clicks
```

A click is considered converting when it generates at least one valid paid transaction within the predefined 7-day conversion window.

See [`EXPERIMENT_DESIGN.md`](EXPERIMENT_DESIGN.md) for the full measurement framework and experiment methodology.

## 03 - Analysis Approach

The analysis combines campaign-level advertising data with transaction-level booking data.

The workflow covers:

1. Generate realistic synthetic experiment data
2. Clean and validate the source data
3. Apply the 7-day conversion window
4. Reconcile campaign conversions with backend transactions
5. Compare Control and Treatment conversion rates
6. Quantify statistical uncertainty and business impact
7. Translate the findings into a campaign recommendation

Statistical analysis will focus on the difference in conversion proportions, including confidence intervals and significance testing.

## 04 - Data

This is a synthetic dataset created to simulate a realistic marketing experimentation workflow.

### Campaign performance

`data/raw/campaign_performance.csv`

Daily Google Ads experiment data containing:

* Impressions
* Clicks
* Cost
* Paid transactions
* Experiment variant

### Transactions

`data/raw/transactions.csv`

Transaction-level backend data containing:

* Transaction ID
* Click ID
* Click date
* Transaction date
* Booking value
* Cancellation status

The raw data includes a small amount of realistic source-data inconsistency, such as mixed value formats, missing booking values, and duplicate records. These are handled during the data preparation process.

## 05 - Technical Stack

* Python
* DuckDB
* SQL
* Pandas
* NumPy

The project uses DuckDB for lightweight local analytical processing and SQL-based data preparation.

## 06 - Repository Structure

```text
campaign-experiment-analysis/
│
├── README.md
├── EXPERIMENT_DESIGN.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── campaign_performance.csv
│   │   └── transactions.csv
│   └── processed/
│       └── experiment_analysis.csv
│
├── sql/
│   ├── validation.sql
│   └── experiment_metrics.sql
│
├── src/
│   ├── generate_data.py
│   ├── validate_experiment.py
│   └── experiment_analysis.py
│
└── outputs/
    ├── experiment_results.csv
    └── figures/
        ├── conversion_rate.png
        ├── conversion_lift.png
        └── business_impact.png
```

## 07 - Project Status

The experiment design, synthetic data generation, data preparation, validation, statistical analysis, and business impact analysis are complete.

The final insights, campaign recommendation, and portfolio presentation will be added during the final packaging stage.
