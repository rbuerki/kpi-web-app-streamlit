import numpy as np
import pandas as pd
import pytest

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")


# @pytest.fixture
# def data_mock():
#     df = pd.DataFrame(
#         np.array(
#             [
#                 ["31.05.2020", 1, 2, 1, "Overall", 1000.0, np.NaN, np.NaN],
#                 ["31.05.2020", 1, 2, 2, "KK", 550.0, np.NaN, np.NaN],
#             ]
#         ),
#         columns=[
#             "calculation_date",
#             "kpi_name",
#             "period_id",
#             "product_name",
#             "cardprofile"
#             "mandant",
#             "sector",
#             "level"
#             "value",
#         ],
#     )
#     df["calculation_date"] = pd.to_datetime(df["calculation_date"])
#     return df


@pytest.fixture(scope="module")
def data_prepared():
    rows = [
        [
            "2020-05-31",
            "Umsatz Total",
            2,
            "Liberty CC",
            "CC",
            "Liberty",
            "B2C",
            3,
            1000,
            1.2,
        ],
        [
            "2020-05-31",
            "Umsatz Inland",
            2,
            "Simply",
            "all",
            "Simply",
            "B2C",
            2,
            500,
            0.2,
        ],
        [
            "2019-05-31",
            "Umsatz Total",
            2,
            "Liberty PP",
            "PP",
            "Liberty",
            "B2C",
            2,
            350,
            np.nan,
        ],
        [
            "2019-05-31",
            "Umsatz Inland",
            2,
            "Simply",
            "all",
            "Simply",
            "B2C",
            2,
            350,
            np.nan,
        ],
        [
            "2019-05-31",
            "Umsatz Inland",
            2,
            "BCAG",
            "all",
            "BCAG",
            "BCAG",
            0,
            2000,
            np.nan,
        ],
    ]

    columns = [
        "calculation_date",
        "kpi_name",
        "period_id",
        "product_name",
        "cardprofile",
        "mandant",
        "sector",
        "level",
        "value",
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
