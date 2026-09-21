import duckdb
from scipy.stats import norm


con = duckdb.connect("analytics.duckdb")


query = """
SELECT
    variant,
    eligible_clicks,
    converting_clicks,

    converting_clicks * 1.0
        / eligible_clicks AS conversion_rate

FROM experiment_analysis

ORDER BY variant
"""


result = con.execute(query).fetchdf()

control = result[result["variant"] == "Control"].iloc[0]
treatment = result[result["variant"] == "Treatment"].iloc[0]


control_clicks = int(control["eligible_clicks"])
control_conversions = int(control["converting_clicks"])
control_rate = control["conversion_rate"]

treatment_clicks = int(treatment["eligible_clicks"])
treatment_conversions = int(treatment["converting_clicks"])
treatment_rate = treatment["conversion_rate"]


# ------------------------------------------------------------
# Primary metric difference
# ------------------------------------------------------------

absolute_difference = treatment_rate - control_rate

relative_lift = absolute_difference / control_rate


# ------------------------------------------------------------
# Two-proportion z-test
# ------------------------------------------------------------

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


z_statistic = (
    absolute_difference
    / standard_error_test
)


p_value = 2 * (
    1 - norm.cdf(abs(z_statistic))
)


# ------------------------------------------------------------
# 95% confidence interval
# ------------------------------------------------------------

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


ci_lower = (
    absolute_difference
    - z_critical * standard_error_ci
)


ci_upper = (
    absolute_difference
    + z_critical * standard_error_ci
)


# ------------------------------------------------------------
# Output
# ------------------------------------------------------------

print("=== PRIMARY METRIC ===")

print(
    result.to_string(index=False)
)

print()

print(
    f"Absolute difference: "
    f"{absolute_difference * 100:.4f} percentage points"
)

print(
    f"Relative lift: "
    f"{relative_lift * 100:.2f}%"
)

print()

print("=== STATISTICAL TEST ===")

print(
    f"Z-statistic: {z_statistic:.4f}"
)

print(
    f"P-value: {p_value:.6f}"
)

print()

print("=== 95% CONFIDENCE INTERVAL ===")

print(
    f"Lower bound: {ci_lower * 100:.4f} percentage points"
)

print(
    f"Upper bound: {ci_upper * 100:.4f} percentage points"
)


# ------------------------------------------------------------
# Secondary business metrics
# ------------------------------------------------------------

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


business_metrics = con.execute(
    business_query
).fetchdf()


print()
print("=== SECONDARY BUSINESS METRICS ===")

print(
    business_metrics.to_string(index=False)
)

# ------------------------------------------------------------
# Business impact
# ------------------------------------------------------------

control_clicks = int(control["eligible_clicks"])
control_transactions = int(control["converting_clicks"])

treatment_rate = treatment["conversion_rate"]

incremental_transactions = (
    treatment_rate * control_clicks
) - control_transactions


treatment_booking_value_per_click = (
    business_metrics.loc[
        business_metrics["variant"] == "Treatment",
        "booking_value_per_click"
    ].iloc[0]
)

control_booking_value = (
    business_metrics.loc[
        business_metrics["variant"] == "Control",
        "booking_value_per_click"
    ].iloc[0]
)

incremental_booking_value = (
    treatment_booking_value_per_click * control_clicks
) - (
    control_booking_value * control_clicks
)


control_cost_per_transaction = (
    business_metrics.loc[
        business_metrics["variant"] == "Control",
        "cost_per_transaction"
    ].iloc[0]
)

treatment_cost_per_transaction = (
    business_metrics.loc[
        business_metrics["variant"] == "Treatment",
        "cost_per_transaction"
    ].iloc[0]
)

cost_difference_per_transaction = (
    treatment_cost_per_transaction
    - control_cost_per_transaction
)


print()
print("=== BUSINESS IMPACT ===")

print(
    f"Incremental converting clicks at Control traffic: "
    f"{incremental_transactions:.0f}"
)

print(
    f"Incremental booking value at Control traffic: "
    f"{incremental_booking_value:.2f}"
)

print(
    f"Cost per transaction difference: "
    f"{cost_difference_per_transaction:.2f}"
)

# ------------------------------------------------------------
# Save experiment results
# ------------------------------------------------------------

experiment_results = business_metrics.copy()

experiment_results["absolute_difference_pp"] = (
    absolute_difference * 100
)

experiment_results["relative_lift_pct"] = (
    relative_lift * 100
)

experiment_results["p_value"] = p_value

experiment_results["ci_lower_pp"] = (
    ci_lower * 100
)

experiment_results["ci_upper_pp"] = (
    ci_upper * 100
)

experiment_results["incremental_converting_clicks_at_control_traffic"] = (
    incremental_transactions
)

experiment_results["incremental_booking_value_at_control_traffic"] = (
    incremental_booking_value
)

# ------------------------------------------------------------
# Format output
# ------------------------------------------------------------

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
print(
    "Experiment results saved to "
    "outputs/experiment_results.csv"
)

con.close()