SELECT
    segment,
    COUNT(*) AS user_count,
    ROUND(AVG(activity_score), 2) AS avg_activity_score,
    ROUND(AVG(buy), 2) AS avg_buy_events,
    ROUND(AVG(conversion_rate), 4) AS avg_conversion_rate,
    ROUND(AVG(recency_days), 2) AS avg_recency_days
FROM user_features
GROUP BY segment
ORDER BY user_count DESC;
