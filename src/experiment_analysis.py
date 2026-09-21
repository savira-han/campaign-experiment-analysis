import duckdb
from scipy.stats import norm


# Connect to the local DuckDB database
con = duckdb.connect("analytics.duckdb")


# Pull the validated experiment data needed for the analysis
query = """
SELECT
    variant,
    eligible_clicks,
    converting_clicks,
    paid_transactions,
    cost,
    booking_value,
    cancelled_transactions
FROM experiment_analysis
ORDER BY variant
"""

result = con.execute(query).fetchdf()


# Split the two experiment groups so the calculations below are easier to read
control = result[result["variant"] == "Control"].iloc[0]
treatment = result[result["variant"] == "Treatment"].iloc[0]


# Primary metric: click-to-paid-transaction conversion rate
control_clicks = int(control["eligible_clicks"])
control_conversions = int(control["converting_clicks"])
control_rate = control_conversions / control_clicks

treatment_clicks = int(treatment["eligible_clicks"])
treatment_conversions = int(treatment["converting_clicks"])
treatment_rate = treatment_conversions / treatment_clicks


# Compare Treatment with Control
absolute_difference = treatment_rate - control_rate
relative_lift = absolute_difference / control_rate


print("=== PRIMARY METRIC ===")
print(
    f"Control conversion rate: {control_rate:.4%}"
)
print(
    f"Treatment conversion rate: {treatment_rate:.4%}"
)
print(
    f"Absolute difference: {absolute_difference * 100:.4f} percentage points"
)
print(
    f"Relative lift: {relative_lift:.2%}"
)


# Two-proportion z-test
# The pooled rate is used for the hypothesis test because the null
# hypothesis assumes that the two conversion rates are equal.
pooled_rate = (
    control_conversions + treatment_conversions
) / (
    control_clicks + treatment_clicks
)

standard_error_test = (
    pooled_rate * (1 - pooled_rate)
    * (
        1 / control_clicks
        + 1 / treatment_clicks
    )
) ** 0.5

z_statistic = absolute_difference / standard_error_test
p_value = 2 * (1 - norm.cdf(abs(z_statistic)))


print()
print("=== STATISTICAL TEST ===")
print(f"Z-statistic: {z_statistic:.4f}")
print(f"P-value: {p_value:.6f}")


# 95% confidence interval for the difference in conversion rates
# Unlike the hypothesis test, the CI uses the individual group rates
# to estimate the uncertainty around the observed difference.
standard_error_ci = (
    (
        control_rate * (1 - control_rate)
        / control_clicks
    )
    +
    (
        treatment_rate * (1 - treatment_rate)
        / treatment_clicks
    )
) ** 0.5

z_critical = norm.ppf(0.975)

ci_lower = absolute_difference - z_critical * standard_error_ci
ci_upper = absolute_difference + z_critical * standard_error_ci


print()
print("=== 95% CONFIDENCE INTERVAL ===")
print(
    f"Lower bound: {ci_lower * 100:.4f} percentage points"
)
print(
    f"Upper bound: {ci_upper * 100:.4f} percentage points"
)


# Secondary business metrics
# These metrics help explain whether the conversion result also
# translates into better campaign economics.
business_query = """
SELECT
    variant,
    eligible_clicks,
    paid_transactions,
    cost,
    booking_value,
    cancelled_transactions,

    paid_transactions * 1.0
        / eligible_clicks AS transactions_per_click,

    cost * 1.0
        / paid_transactions AS cost_per_transaction,

    booking_value * 1.0
        / eligible_clicks AS booking_value_per_click,

    booking_value * 1.0
        / paid_transactions AS average_booking_value,

    cancelled_transactions * 1.0
        / paid_transactions AS cancellation_rate

FROM experiment_analysis
ORDER BY variant
"""

business_metrics = con.execute(business_query).fetchdf()


print()
print("=== SECONDARY BUSINESS METRICS ===")
print(
    business_metrics.to_string(index=False)
)


# Estimate the Treatment impact using the same click volume as Control.
# This avoids attributing the difference in raw totals to performance
# when the two variants received slightly different amounts of traffic.
control_booking_value_per_click = business_metrics.loc[
    business_metrics["variant"] == "Control",
    "booking_value_per_click"
].iloc[0]

treatment_booking_value_per_click = business_metrics.loc[
    business_metrics["variant"] == "Treatment",
    "booking_value_per_click"
].iloc[0]

incremental_converting_clicks = (
    treatment_rate * control_clicks
) - control_conversions

incremental_booking_value = (
    treatment_booking_value_per_click
    - control_booking_value_per_click
) * control_clicks


control_cost_per_transaction = business_metrics.loc[
    business_metrics["variant"] == "Control",
    "cost_per_transaction"
].iloc[0]

treatment_cost_per_transaction = business_metrics.loc[
    business_metrics["variant"] == "Treatment",
    "cost_per_transaction"
].iloc[0]

cost_difference_per_transaction = (
    treatment_cost_per_transaction
    - control_cost_per_transaction
)


print()
print("=== BUSINESS IMPACT ===")
print(
    f"Incremental converting clicks at Control traffic: "
    f"{incremental_converting_clicks:.0f}"
)
print(
    f"Incremental booking value at Control traffic: "
    f"{incremental_booking_value:.2f}"
)
print(
    f"Cost per transaction difference: "
    f"{cost_difference_per_transaction:.2f}"
)


# Save the main analysis output for use in the final case study
experiment_results = business_metrics.copy()

experiment_results["absolute_difference_pp"] = (
    absolute_difference * 100
)
experiment_results["relative_lift_pct"] = (
    relative_lift * 100
)
experiment_results["p_value"] = p_value
experiment_results["ci_lower_pp"] = ci_lower * 100
experiment_results["ci_upper_pp"] = ci_upper * 100

experiment_results[
    "incremental_converting_clicks_at_control_traffic"
] = incremental_converting_clicks

experiment_results[
    "incremental_booking_value_at_control_traffic"
] = incremental_booking_value


# Round the output so the CSV is easier to inspect and use in the portfolio
experiment_results = experiment_results.round({
    "cost": 2,
    "booking_value": 2,
    "transactions_per_click": 6,
    "cost_per_transaction": 2,
    "booking_value_per_click": 2,
    "average_booking_value": 2,
    "cancellation_rate": 6,
    "absolute_difference_pp": 4,
    "relative_lift_pct": 2,
    "p_value": 6,
    "ci_lower_pp": 4,
    "ci_upper_pp": 4,
    "incremental_converting_clicks_at_control_traffic": 0,
    "incremental_booking_value_at_control_traffic": 2
})

experiment_results.to_csv(
    "outputs/experiment_results.csv",
    index=False
)

print()
print("Experiment results saved to outputs/experiment_results.csv")


con.close()