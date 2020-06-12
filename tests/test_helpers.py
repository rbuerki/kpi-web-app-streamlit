from .context import kpi_sheet
import pandas as pd


def test_load_data_1():
    result = kpi_sheet.load_data()
    assert isinstance(result, pd.DataFrame)


def test_load_data_2():
    result = kpi_sheet.load_data()
    assert [
        "calculation_date",
        "kpi_id",
        "period_id",
        "agg_level_id",
        "agg_level_value",
        "value",
        "mandant",
        "profile",
    ] in result.columns
