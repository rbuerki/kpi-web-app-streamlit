import numpy as np
import pandas as pd
import pytest

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")


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
#         "mock_data.csv",
#         sep=";",
#         engine="python",
#         parse_dates=["calculation_date"],
#     )
#     return mock_df.head()


# @pytest.fixture(scope='function')
# def example_fixture():
#     LOGGER.info("Setting Up Example Fixture...")
#     yield
#     LOGGER.info("Tearing Down Example Fixture...")
