"""Unit tests for the statistical and reporting helpers in main.py.

Uses only the standard-library ``unittest`` module plus dependencies already
listed in requirements.txt (pandas, numpy). Run with:

    python -m unittest test_main -v
"""

from __future__ import annotations

import asyncio
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

import main

SAMPLE_CSV = Path(__file__).resolve().parent / "sample_sales.csv"


class TestGenerateFutureEstimates(unittest.TestCase):
    def test_sample_data_produces_estimates_for_numeric_columns(self):
        df = pd.read_csv(SAMPLE_CSV)
        estimates = main.generate_future_estimates(df)
        numeric_cols = list(df.select_dtypes(include=np.number).columns)
        self.assertEqual(len(estimates), len(numeric_cols))
        for estimate in estimates:
            self.assertIn(estimate["column"], numeric_cols)
            self.assertEqual(estimate["model_type"], "Linear Regression")
            self.assertIsInstance(estimate["trend_coefficient"], float)
            self.assertEqual(len(estimate["future_estimates_5_steps"]), 5)
            self.assertTrue(all(isinstance(v, float) for v in estimate["future_estimates_5_steps"]))

    def test_known_linear_trend_recovers_coefficient(self):
        # y = 2x -> coefficient should be ~2.0
        df = pd.DataFrame({"y": [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]})
        estimates = main.generate_future_estimates(df)
        self.assertEqual(len(estimates), 1)
        estimate = estimates[0]
        self.assertAlmostEqual(estimate["trend_coefficient"], 2.0, places=6)
        self.assertAlmostEqual(estimate["last_observed_value"], 10.0, places=6)
        # The first forecast step continues the y=2x trend (x=6 -> 12)
        self.assertAlmostEqual(estimate["future_estimates_5_steps"][0], 12.0, places=6)
        self.assertIn("increase", estimate["insight"])

    def test_empty_dataframe_returns_empty(self):
        self.assertEqual(main.generate_future_estimates(pd.DataFrame()), [])

    def test_single_row_returns_empty(self):
        self.assertEqual(main.generate_future_estimates(pd.DataFrame({"a": [1]})), [])

    def test_non_numeric_only_returns_empty(self):
        self.assertEqual(
            main.generate_future_estimates(pd.DataFrame({"a": ["x", "y", "z"]})),
            [],
        )

    def test_nan_gaps_do_not_crash_and_produce_estimate(self):
        df = pd.DataFrame({"a": [1.0, np.nan, 3.0, np.nan, 5.0, 6.0]})
        estimates = main.generate_future_estimates(df)
        self.assertEqual(len(estimates), 1)
        self.assertEqual(estimates[0]["column"], "a")
        self.assertEqual(len(estimates[0]["future_estimates_5_steps"]), 5)


class TestReportGeneration(unittest.TestCase):
    def test_handles_empty_future_estimates_and_returns_bytes(self):
        report = asyncio.run(
            main.generate_complete_report(
                dataset_id="test-dataset-id",
                analysis=None,
                insights=["Insight one."],
                ai_insights=["AI suggestion."],
                future_estimates=[],
                news_articles=None,
                chart_images=None,
                cleaned_csv_bytes=None,
            )
        )
        self.assertIsInstance(report, bytes)
        self.assertIn(b"Sairo Insights", report)
        # With no future estimates, the Future Estimates section should be absent.
        self.assertNotIn(b"Future Estimates", report)

    def test_includes_future_estimates_section_when_present(self):
        future_estimates = [
            {
                "column": "revenue",
                "model_type": "Linear Regression",
                "trend_coefficient": 1.23,
                "last_observed_value": 100.0,
                "future_estimates_5_steps": [101.0, 102.0, 103.0, 104.0, 105.0],
                "insight": "Predicted revenue to increase over the next 5 steps.",
            }
        ]
        report = asyncio.run(
            main.generate_complete_report(
                dataset_id="test-dataset-id",
                analysis=None,
                insights=None,
                ai_insights=None,
                future_estimates=future_estimates,
                news_articles=None,
                chart_images=None,
                cleaned_csv_bytes=None,
            )
        )
        self.assertIsInstance(report, bytes)
        self.assertIn(b"Future Estimates", report)
        self.assertIn(b"revenue", report)


class TestAiInsights(unittest.TestCase):
    def test_returns_list(self):
        df = pd.read_csv(SAMPLE_CSV)
        result = main.generate_ai_insights(df, {}, ["existing insight"])
        self.assertIsInstance(result, list)
        self.assertIn("existing insight", result)
        self.assertLessEqual(len(result), 8)


if __name__ == "__main__":
    unittest.main()
