import numpy as np

# import pandas as pd

from src import helpers


def test_impute_missing_mandant(data):
    df = helpers.impute_missing_mandant_values(data)
    assert (df["mandant"].values == np.array(["Overall", "Overall"])).all()


def test_impute_missing_profile(data):
    df = helpers.impute_missing_profile_values(data)
    assert (df["profile"].values == np.array(["#NV", "CC"])).all()


# assert df[["mandant", "profile"]].values == np.array(
#     [["Overall", "KK"]["nan", "KK"]]
# )


# def test_load_data_1(mock_dataframe_1):
#     result = load_data(mock_dataframe_1)
#     assert isinstance(result, pd.DataFrame)


# def test_load_data_2():
#     result = kpi_sheet.load_data()
#     assert [
#         "calculation_date",
#         "kpi_id",
#         "period_id",
#         "agg_level_id",
#         "agg_level_value",
#         "value",
#         "mandant",
#         "profile",
#     ] in result.columns
