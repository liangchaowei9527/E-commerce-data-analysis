import unittest

import pandas as pd

from taobao_analysis.metrics import (
    build_user_features,
    compute_behavior_overview,
    compute_funnel_metrics,
)


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.cleaned = pd.DataFrame(
            [
                [1, 100, 10, "pv", 1511544070, pd.Timestamp("2017-11-25 01:47:50"), pd.Timestamp("2017-11-25").date(), 1, 5, 1],
                [1, 100, 10, "cart", 1511547670, pd.Timestamp("2017-11-25 02:47:50"), pd.Timestamp("2017-11-25").date(), 2, 5, 1],
                [1, 100, 10, "buy", 1511551270, pd.Timestamp("2017-11-25 03:47:50"), pd.Timestamp("2017-11-25").date(), 3, 5, 1],
                [2, 200, 20, "pv", 1511554870, pd.Timestamp("2017-11-25 04:47:50"), pd.Timestamp("2017-11-25").date(), 4, 5, 1],
                [2, 200, 20, "fav", 1511558470, pd.Timestamp("2017-11-25 05:47:50"), pd.Timestamp("2017-11-25").date(), 5, 5, 1],
                [3, 300, 30, "pv", 1511562070, pd.Timestamp("2017-11-25 06:47:50"), pd.Timestamp("2017-11-25").date(), 6, 5, 1],
            ],
            columns=[
                "user_id",
                "item_id",
                "category_id",
                "behavior_type",
                "timestamp",
                "event_time",
                "date",
                "hour",
                "weekday",
                "is_weekend",
            ],
        )

    def test_compute_behavior_overview_returns_key_counts(self):
        overview = compute_behavior_overview(self.cleaned)

        self.assertEqual(overview["total_events"], 6)
        self.assertEqual(overview["unique_users"], 3)
        self.assertEqual(overview["buy_users"], 1)
        self.assertAlmostEqual(overview["avg_events_per_user"], 2.0)

    def test_compute_funnel_metrics_uses_user_level_stage_counts(self):
        user_features = build_user_features(self.cleaned)
        funnel = compute_funnel_metrics(user_features)

        self.assertEqual(funnel["pv_users"], 3)
        self.assertEqual(funnel["fav_users"], 1)
        self.assertEqual(funnel["cart_users"], 1)
        self.assertEqual(funnel["buy_users"], 1)
        self.assertAlmostEqual(funnel["pv_to_buy_rate"], 1 / 3, places=4)
        self.assertAlmostEqual(funnel["cart_to_buy_rate"], 1.0, places=4)
        self.assertAlmostEqual(funnel["fav_to_buy_rate"], 0.0, places=4)

    def test_build_user_features_assigns_expected_segments(self):
        user_features = build_user_features(self.cleaned)

        segments = dict(zip(user_features["user_id"], user_features["segment"]))
        self.assertEqual(segments[1], "高活跃高转化")
        self.assertEqual(segments[2], "高活跃低转化")
        self.assertEqual(segments[3], "低活跃低转化")


if __name__ == "__main__":
    unittest.main()
