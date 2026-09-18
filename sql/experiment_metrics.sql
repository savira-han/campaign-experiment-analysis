-- ============================================================
-- 1. Clean campaign performance
-- ============================================================

CREATE OR REPLACE VIEW clean_campaign_performance AS

SELECT
    CAST(date AS DATE) AS date,
    experiment_id,
    variant,
    campaign_id,
    CAST(impressions AS BIGINT) AS impressions,
    CAST(clicks AS BIGINT) AS clicks,
    CAST(cost AS DOUBLE) AS cost,
    CAST(paid_transactions AS BIGINT) AS paid_transactions

FROM read_csv(
    'data/raw/campaign_performance.csv',
    header = true,
    columns = {
        'date': 'VARCHAR',
        'experiment_id': 'VARCHAR',
        'variant': 'VARCHAR',
        'campaign_id': 'VARCHAR',
        'impressions': 'VARCHAR',
        'clicks': 'VARCHAR',
        'cost': 'DOUBLE',
        'paid_transactions': 'BIGINT'
    }
);


-- ============================================================
-- 2. Clean and deduplicate transactions
-- ============================================================

CREATE OR REPLACE VIEW clean_transactions AS

SELECT DISTINCT
    transaction_id,
    experiment_id,
    variant,
    click_id,
    CAST(click_date AS DATE) AS click_date,
    CAST(transaction_date AS DATE) AS transaction_date,

    CASE
        WHEN TRIM(booking_value) = '' THEN NULL
        ELSE CAST(
            REPLACE(booking_value, ',', '')
            AS DOUBLE
        )
    END AS booking_value,

    CASE
        WHEN LOWER(TRIM(cancelled)) IN ('1', 'true')
            THEN TRUE
        WHEN LOWER(TRIM(cancelled)) IN ('0', 'false')
            THEN FALSE
        ELSE NULL
    END AS cancelled

FROM read_csv(
    'data/raw/transactions.csv',
    header = true,
    columns = {
        'transaction_id': 'VARCHAR',
        'experiment_id': 'VARCHAR',
        'variant': 'VARCHAR',
        'click_id': 'VARCHAR',
        'click_date': 'VARCHAR',
        'transaction_date': 'VARCHAR',
        'booking_value': 'VARCHAR',
        'cancelled': 'VARCHAR'
    }
);


-- ============================================================
-- 3. Apply 7-day conversion window
-- ============================================================

CREATE OR REPLACE VIEW eligible_transactions AS

SELECT
    *

FROM clean_transactions

WHERE transaction_date >= click_date
  AND transaction_date <= click_date + INTERVAL 7 DAY
  AND transaction_date <= DATE '2026-09-04';


-- ============================================================
-- 4. Build experiment analysis table
-- ============================================================

CREATE OR REPLACE TABLE experiment_analysis AS

WITH campaign_metrics AS (

    SELECT
        experiment_id,
        variant,

        SUM(impressions) AS impressions,
        SUM(clicks) AS eligible_clicks,
        SUM(cost) AS cost,
        SUM(paid_transactions) AS platform_paid_transactions

    FROM clean_campaign_performance

    GROUP BY
        experiment_id,
        variant
),

transaction_metrics AS (

    SELECT
        experiment_id,
        variant,

        COUNT(*) AS paid_transactions,

        COUNT(DISTINCT click_id) AS converting_clicks,

        SUM(
            CASE
                WHEN cancelled = FALSE
                THEN COALESCE(booking_value, 0)
                ELSE 0
            END
        ) AS booking_value,

        SUM(
            CASE
                WHEN cancelled = TRUE
                THEN 1
                ELSE 0
            END
        ) AS cancelled_transactions

    FROM eligible_transactions

    GROUP BY
        experiment_id,
        variant
)

SELECT
    c.experiment_id,
    c.variant,
    c.impressions,
    c.eligible_clicks,
    c.cost,

    COALESCE(t.converting_clicks, 0)
        AS converting_clicks,

    COALESCE(t.paid_transactions, 0)
        AS paid_transactions,

    COALESCE(t.booking_value, 0)
        AS booking_value,

    COALESCE(t.cancelled_transactions, 0)
        AS cancelled_transactions,

    c.platform_paid_transactions

FROM campaign_metrics c

LEFT JOIN transaction_metrics t
    ON c.experiment_id = t.experiment_id
    AND c.variant = t.variant;