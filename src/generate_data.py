import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# 1. Configuration
# ============================================================

RANDOM_SEED = 42

EXPERIMENT_ID = "EXP001"
START_DATE = "2026-08-01"
EXPERIMENT_DAYS = 28
OBSERVATION_DAYS = 7

CONTROL_CAMPAIGN = "CAMP_A"
TREATMENT_CAMPAIGN = "CAMP_B"

OUTPUT_DIR = Path("data/raw")

rng = np.random.default_rng(RANDOM_SEED)


# ============================================================
# 2. Generate campaign performance
# ============================================================

dates = pd.date_range(
    start=START_DATE,
    periods=EXPERIMENT_DAYS,
    freq="D"
)

campaign_rows = []

for date in dates:
    for variant, campaign_id in [
        ("Control", CONTROL_CAMPAIGN),
        ("Treatment", TREATMENT_CAMPAIGN),
    ]:
        # Daily traffic varies naturally around a base level
        impressions = int(rng.normal(185_000, 15_000))

        ctr = rng.normal(
            0.048 if variant == "Control" else 0.050,
            0.004
        )

        clicks = max(1, int(impressions * ctr))

        # CPC varies by day and variant
        cpc = rng.normal(
            0.88 if variant == "Control" else 0.86,
            0.08
        )

        cost = round(clicks * max(cpc, 0.40), 2)

        campaign_rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "experiment_id": EXPERIMENT_ID,
            "variant": variant,
            "campaign_id": campaign_id,
            "impressions": str(impressions),
            "clicks": str(clicks),
            "cost": cost,
        })

campaign_performance = pd.DataFrame(campaign_rows)


# ============================================================
# 3. Generate transactions
# ============================================================

transaction_rows = []
click_counter = 1
transaction_counter = 1

for _, row in campaign_performance.iterrows():
    date = pd.Timestamp(row["date"])
    variant = row["variant"]
    clicks = int(row["clicks"])

    # Underlying conversion probability
    conversion_rate = (
        rng.normal(0.045, 0.004)
        if variant == "Control"
        else rng.normal(0.048, 0.004)
    )

    conversion_rate = max(
        0.01,
        min(conversion_rate, 0.10)
    )

    # Simulate click-level conversion outcomes
    converting_clicks = rng.random(clicks) < conversion_rate

    campaign_paid_transactions = 0

    for converted in converting_clicks:

        click_id = f"CLK{click_counter:06d}"
        click_counter += 1

        if not converted:
            continue

        # Most converting clicks generate one transaction.
        # A small number generate two transactions.
        transaction_count = (
            2 if rng.random() < 0.02 else 1
        )

        # A click is considered converted only when a
        # valid paid transaction occurs within 7 days.
        valid_transaction_created = False

        for _ in range(transaction_count):

            conversion_delay = int(
                rng.choice(
                    [
                        0, 1, 1, 2, 2, 3,
                        4, 5, 6, 7, 8, 10
                    ]
                )
            )

            observation_end = (
                pd.Timestamp(START_DATE)
                + pd.Timedelta(days=EXPERIMENT_DAYS + OBSERVATION_DAYS - 1)
            )

            transaction_date = (
                date + pd.Timedelta(days=conversion_delay)
            )

            # Transactions after the observation period are not observed
            if transaction_date > observation_end:
                continue           

            booking_value = round(
                rng.lognormal(
                    mean=6.2,
                    sigma=0.65
                ),
                2
            )

            cancelled = rng.random() < 0.10

            # Natural source-data inconsistency:
            # some booking values are empty,
            # some contain thousands separators.
            value_format = rng.random()

            if value_format < 0.03:
                raw_booking_value = ""
            elif value_format < 0.08:
                raw_booking_value = f"{booking_value:,.2f}"
            else:
                raw_booking_value = str(booking_value)

            # Natural source-data inconsistency in cancellation field
            cancellation_format = rng.random()

            if cancellation_format < 0.50:
                raw_cancelled = "1" if cancelled else "0"
            else:
                raw_cancelled = (
                    "true" if cancelled else "false"
                )

            transaction_rows.append({
                "transaction_id": (
                    f"TX{transaction_counter:06d}"
                ),
                "experiment_id": EXPERIMENT_ID,
                "variant": variant,
                "click_id": click_id,
                "click_date": date.strftime("%Y-%m-%d"),
                "transaction_date": (
                    transaction_date.strftime("%Y-%m-%d")
                ),
                "booking_value": raw_booking_value,
                "cancelled": raw_cancelled,
            })

            transaction_counter += 1

            # Count the transaction toward the campaign-level
            # Google Ads conversion total only if it occurs
            # within the 7-day conversion window.
            if conversion_delay <= 7:
                valid_transaction_created = True

        if valid_transaction_created:
            campaign_paid_transactions += 1

    # Store the campaign-level conversion count
    campaign_performance.loc[
        (campaign_performance["date"] == row["date"]) &
        (campaign_performance["variant"] == variant),
        "paid_transactions"
    ] = campaign_paid_transactions


transactions = pd.DataFrame(transaction_rows)

# Add a very small number of exact duplicate transaction rows
duplicate_count = max(
    1,
    int(len(transactions) * 0.002)
)

duplicates = transactions.sample(
    n=duplicate_count,
    random_state=RANDOM_SEED
)

transactions = pd.concat(
    [transactions, duplicates],
    ignore_index=True
)


# ============================================================
# 4. Save raw data
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

campaign_performance.to_csv(
    OUTPUT_DIR / "campaign_performance.csv",
    index=False
)

transactions.to_csv(
    OUTPUT_DIR / "transactions.csv",
    index=False
)

print(
    f"Campaign performance: "
    f"{len(campaign_performance):,} rows"
)

print(
    f"Transactions: "
    f"{len(transactions):,} rows"
)

print(
    f"Raw data saved to: "
    f"{OUTPUT_DIR}"
)