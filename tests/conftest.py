import numpy as np
import pandas as pd
import pytest

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")


@pytest.fixture
def data_mock():
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


@pytest.fixture(scope="module")
def data_prepared():
    rows = [
        ["2020-05-31", "Umsatz Total", 2, 4, "Liberty CC", 1000, "Liberty", "CC", 1.2,],
        ["2020-05-31", "Umsatz Inland", 2, 4, "Simply", 500, "Simply", np.nan, 0.2,],
        [
            "2019-05-31",
            "Umsatz Total",
            2,
            4,
            "Liberty PP",
            750,
            "Liberty",
            "PP",
            np.nan,
        ],
        ["2019-05-31", "Umsatz Inland", 5, 4, "Simply", 350, "Simply", np.nan, np.nan,],
        [
            "2019-05-31",
            "Umsatz Inland",
            5,
            2,
            "Overall",
            2000,
            "Overall",
            np.nan,
            np.nan,
        ],
    ]

    columns = [
        "calculation_date",
        "kpi_name",
        "period_id",
        "agg_level_id",
        "agg_level_value",
        "value",
        "mandant",
        "profile",
        "diff_value",
    ]

    df = pd.DataFrame(rows, columns=columns)
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
