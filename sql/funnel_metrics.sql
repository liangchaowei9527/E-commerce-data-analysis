SELECT
    SUM(CASE WHEN pv > 0 THEN 1 ELSE 0 END) AS pv_users,
    SUM(CASE WHEN fav > 0 THEN 1 ELSE 0 END) AS fav_users,
    SUM(CASE WHEN cart > 0 THEN 1 ELSE 0 END) AS cart_users,
    SUM(CASE WHEN buy > 0 THEN 1 ELSE 0 END) AS buy_users,
    ROUND(
        1.0 * SUM(CASE WHEN pv > 0 AND fav > 0 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN pv > 0 THEN 1 ELSE 0 END), 0),
        4
    ) AS pv_to_fav_rate,
    ROUND(
        1.0 * SUM(CASE WHEN pv > 0 AND cart > 0 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN pv > 0 THEN 1 ELSE 0 END), 0),
        4
    ) AS pv_to_cart_rate,
    ROUND(
        1.0 * SUM(CASE WHEN pv > 0 AND buy > 0 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN pv > 0 THEN 1 ELSE 0 END), 0),
        4
    ) AS pv_to_buy_rate,
    ROUND(
        1.0 * SUM(CASE WHEN cart > 0 AND buy > 0 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN cart > 0 THEN 1 ELSE 0 END), 0),
        4
    ) AS cart_to_buy_rate,
    ROUND(
        1.0 * SUM(CASE WHEN fav > 0 AND buy > 0 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN fav > 0 THEN 1 ELSE 0 END), 0),
        4
    ) AS fav_to_buy_rate
FROM user_features;
