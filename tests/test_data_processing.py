import unittest

import pandas as pd

from taobao_analysis.data_processing import clean_behavior_data


class CleanBehaviorDataTests(unittest.TestCase):
    def test_clean_behavior_data_adds_time_columns_and_drops_invalid_rows(self):
        raw = pd.DataFrame(
            [
                [1, 101, 10, "pv", 1511544070],
                [1, 101, 10, "pv", 1511544070],
                [2, 102, 11, "buy", 1511547670],
                [3, 103, 12, "invalid", 1511551270],
            ],
            columns=["user_id", "item_id", "category_id", "behavior_type", "timestamp"],
        )

        cleaned = clean_behavior_data(raw)

        self.assertEqual(len(cleaned), 2)
        self.assertListEqual(
            list(cleaned.columns),
            [
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
        self.assertEqual(cleaned["hour"].iloc[0], 1)
        self.assertEqual(cleaned["is_weekend"].iloc[0], 1)


if __name__ == "__main__":
    unittest.main()
