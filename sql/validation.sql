-- ============================================================
-- 1. Experiment structure
-- ============================================================

SELECT
    COUNT(DISTINCT experiment_id) AS experiment_count,
    COUNT(DISTINCT variant) AS variant_count,
    MIN(date) AS start_date,
    MAX(date) AS end_date,
    COUNT(DISTINCT date) AS experiment_days
FROM clean_campaign_performance;


-- ============================================================
-- 2. Daily coverage by variant
-- ============================================================

SELECT
    variant,
    COUNT(DISTINCT date) AS experiment_days,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    SUM(cost) AS cost
FROM clean_campaign_performance
GROUP BY variant
ORDER BY variant;


-- ============================================================
-- 3. Traffic allocation
-- ============================================================

SELECT
    variant,
    SUM(clicks) AS eligible_clicks,
    ROUND(
        SUM(clicks) * 100.0
        / SUM(SUM(clicks)) OVER (),
        2
    ) AS click_share_pct
FROM clean_campaign_performance
GROUP BY variant
ORDER BY variant;


-- ============================================================
-- 4. Raw transaction duplicates
-- ============================================================

SELECT
    COUNT(*) AS raw_transaction_rows,
    COUNT(DISTINCT transaction_id) AS unique_transaction_ids,
    COUNT(*) - COUNT(DISTINCT transaction_id) AS duplicate_transaction_rows
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
-- 5. Invalid transaction dates
-- ============================================================

SELECT
    COUNT(*) AS invalid_date_rows
FROM clean_transactions
WHERE transaction_date < click_date
   OR transaction_date > DATE '2026-09-04';


-- ============================================================
-- 6. Conversion window validation
-- ============================================================

SELECT
    COUNT(*) AS invalid_conversion_window_rows
FROM eligible_transactions
WHERE transaction_date < click_date
   OR transaction_date > click_date + INTERVAL 7 DAY;


-- ============================================================
-- 7. Transaction-to-click linkage
-- ============================================================

SELECT
    COUNT(*) AS transactions_without_click_id
FROM clean_transactions
WHERE click_id IS NULL
   OR TRIM(click_id) = '';


-- ============================================================
-- 8. Conversion reconciliation
-- ============================================================

SELECT
    variant,
    converting_clicks,
    platform_paid_transactions,
    converting_clicks - platform_paid_transactions
        AS reconciliation_difference,
    paid_transactions,
    paid_transactions - converting_clicks
        AS additional_transactions
FROM experiment_analysis
ORDER BY variant;


-- ============================================================
-- 9. Business metric sanity
-- ============================================================

SELECT
    variant,
    booking_value,
    cancelled_transactions,
    paid_transactions,
    ROUND(
        cancelled_transactions * 100.0
        / NULLIF(paid_transactions, 0),
        2
    ) AS cancellation_rate_pct
FROM experiment_analysis
ORDER BY variant;