import datetime as dt
import numpy as np
import pandas as pd
import pytest

from data.create_mock_data import (
    multiply_kpis,
    generate_periods,
    randomize_values,
    multiply_periods,
)


def test_multiply_kpis(data):
    df_out = multiply_kpis(data, 3)
    assert len(df_out) == 6
    assert df_out["kpi_id"].nunique() == 3


def test_randomize_values(data):
    col = randomize_values(data["value"])
    assert isinstance(col, pd.Series)
    assert col[0] >= 800 and col[0] <= 1100
    assert col[1] >= 440 and col[1] <= 605


def test_generate_periods(data):
    periods = generate_periods(data["calculation_date"].min())
    assert len(periods) == 12
    assert periods[-1] == dt.date(2019, 5, 31)
    assert periods[0] == dt.date(2020, 4, 30)


def test_multiply_periods(data):
    periods = generate_periods(data["calculation_date"].min())
    df_out = multiply_periods(data, periods)
    assert len(df_out) == len(data) * 13
    assert df_out["calculation_date"].nunique() == 13
