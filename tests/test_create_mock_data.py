import datetime as dt
import pandas as pd

from .data.create_mock_data import (
    multiply_kpis,
    generate_periods,
    randomize_values,
    multiply_periods,
)


def test_multiply_kpis(data_mock):
    df_out = multiply_kpis(data_mock, 3)
    assert len(df_out) == 6
    assert df_out["kpi_id"].nunique() == 3


def test_randomize_values(data_mock):
    col = randomize_values(data_mock["value"])
    assert isinstance(col, pd.Series)
    assert col[0] >= 900 and col[0] <= 1050
    assert col[1] >= 495 and col[1] <= 577.5


def test_generate_periods(data_mock):
    periods = generate_periods(data_mock["calculation_date"].min(), 2)
    assert len(periods) == 24
    assert periods[-1] == dt.date(2018, 5, 31)
    assert periods[0] == dt.date(2020, 4, 30)


def test_multiply_periods(data_mock):
    periods = generate_periods(data_mock["calculation_date"].min(), 2)
    df_out = multiply_periods(data_mock, periods)
    assert len(df_out) == len(data_mock) * 25
    assert df_out["calculation_date"].nunique() == 25
