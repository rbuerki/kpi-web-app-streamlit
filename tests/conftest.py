# Used for specifying Pytest fixtures, hooks or loading external plugins, see here:
# https://towardsdatascience.com/pytest-features-that-you-need-in-your-testing-life-31488dc7d9eb

# import logging
import numpy as np
import pandas as pd
import os
import sys
import pytest

# Append abs path of the module to the sys.path(), solving some import problems
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# LOGGER = logging.getLogger(__name__)


@pytest.fixture
def data():
    df = pd.DataFrame(
        np.array(
            [
                ["31.05.2020", 1, 2, 1, "Overall", 1000.0, np.NaN, np.NaN],
                ["31.05.2020", 1, 2, 2, "KK", 550.0, np.NaN, np.NaN],
            ]
        ),
        columns=[
            "calculation_date",
            "kpi_id",
            "period_id",
            "agg_level_id",
            "agg_level_value",
            "value",
            "mandant",
            "profile",
        ],
    )
    df["calculation_date"] = pd.to_datetime(df["calculation_date"])
    return df


# @pytest.fixture(scope="module")
# def mock_dataframe_1():
#     mock_df = pd.read_csv(
#         "mock_data.csv", sep=";", engine="python", parse_dates=["calculation_date"]
#     )
#     return mock_df.head()


# @pytest.fixture(scope='function')
# def example_fixture():
#     LOGGER.info("Setting Up Example Fixture...")
#     yield
#     LOGGER.info("Tearing Down Example Fixture...")
