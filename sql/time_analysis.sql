SELECT
    hour,
    SUM(CASE WHEN behavior_type = 'pv' THEN count ELSE 0 END) AS pv_count,
    SUM(CASE WHEN behavior_type = 'cart' THEN count ELSE 0 END) AS cart_count,
    SUM(CASE WHEN behavior_type = 'buy' THEN count ELSE 0 END) AS buy_count,
    ROUND(
        1.0 * SUM(CASE WHEN behavior_type = 'buy' THEN count ELSE 0 END)
        / NULLIF(SUM(CASE WHEN behavior_type = 'pv' THEN count ELSE 0 END), 0),
        4
    ) AS pv_to_buy_rate
FROM hourly_behavior_counts
GROUP BY hour
ORDER BY pv_count DESC, pv_to_buy_rate ASC;
