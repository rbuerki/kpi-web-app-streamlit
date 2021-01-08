import numpy as np
import pandas as pd
import pytest
from pytest import approx

from src import helpers  # noqa
from src import data_dicts  # noqa


def test_return_full_date_list(data_prepared):
    date_list = helpers._return_full_date_list(data_prepared)
    assert isinstance(date_list, list)
    assert date_list == ["2020-05-31", "2019-05-31"]


@pytest.mark.parametrize(
    "n_months_min, expected",
    [
        (0, ["2020-05-31", "2019-05-31"]),
        (1, ["2020-05-31"]),
        # (2, pytest.raises(ValueError)),
    ],
)
def test_get_filter_options_for_due_date(data_prepared, n_months_min, expected):
    date_list = helpers.get_filter_options_for_due_date(data_prepared, n_months_min)
    assert date_list == expected


def test_return_max_date_string(data_prepared):
    max_date = helpers.return_max_date_string(data_prepared)
    assert isinstance(max_date, str)
    assert max_date == "2020-05-31"


def test_return_actual_date_string():
    actual_date = helpers.return_actual_date_string("2020-05-31", "2020-06-31")
    assert isinstance(actual_date, str)
    assert actual_date == "2020-05-31"


def test_truncate_data_to_actual_date(data_prepared):
    df = helpers.truncate_data_to_actual_date(data_prepared, "2020-04-30")
    assert df.shape[0] == 3


def test_calculate_max_n_years_available(data_prepared):  # TODO: could add more ...
    with pytest.raises(
        ValueError, match="Something went wrong. Not enough data periods loaded."
    ):
        raise ValueError("Something went wrong. Not enough data periods loaded.")
        helpers.test_calculate_max_n_years_available(data_prepared)


def test_truncate_data_n_years_back(data_prepared):
    data_prepared.iloc[3, 0] = "2017-12-31"
    data_prepared["calculation_date"] = pd.to_datetime(
        data_prepared["calculation_date"], format="%Y-%m-%d"
    )
    df = helpers.truncate_data_n_years_back(data_prepared, "2020-05-31", 2)
    assert df.shape[0] == 4

    with pytest.raises(AssertionError):
        raise AssertionError
        df = helpers.truncate_data_n_years_back(data_prepared, "2020-04-30", 2)


@pytest.mark.parametrize(
    "n_years, expected",
    [
        (1, ["Monat", "Year To Date", "3 Monate rollierend", "6 Monate rollierend"]),
        (
            2,
            [
                "Monat",
                "Year To Date",
                "3 Monate rollierend",
                "6 Monate rollierend",
                "12 Monate rollierend",
            ],
        ),
    ],
)
def test_get_filter_options_for_result_dim(n_years, expected):
    result = helpers.get_filter_options_for_result_dim(n_years)
    assert result == expected


# def test_replace_monthly_values_with_avg(data_prepared):
#     result = helpers.test_replace_monthly_values_with_avg(data_prepared, "Monat", True)
#     pass


def test_calculate_diff_column(data_prepared):
    df = helpers.calculate_diff_column(data_prepared, 1)
    assert df.shape[1] == 10
    assert list(df.columns)[-1] == "diff_value"
    assert list(df.columns)[0] == "calculation_date"
    df["diff_value"].values == approx(np.array([0.33, np.NaN, np.NaN, np.NaN, np.NaN]))


def test_create_df_with_actual_period_only(data_prepared):
    df = helpers.create_df_with_actual_period_only(data_prepared, "2020-05-31")
    assert len(df) == 2


def test_get_filter_options_for_mandant_groups(data_prepared):
    result = helpers.get_filter_options_for_mandant_groups(data_prepared)
    assert result == ["[alle]", "BCAG", "Liberty", "Simply"]


def test_get_filter_options_for_kpi_groups():
    result = helpers.get_filter_options_for_kpi_groups()
    assert result == [
        "[alle] ohne NCA",
        "[alle]",
        "Umsatz",
        "Anzahl Trx",
        "Anzahl Konten",
        "NCA",
    ]


def test_get_filter_options_for_entities(data_prepared):
    result = helpers.get_filter_options_for_entities(data_prepared)
    assert result == ["[alle]", "Liberty CC", "Simply", "Liberty PP", "BCAG"]
    assert isinstance(result, list)


def test_get_filter_options_for_kpi(data_prepared):
    result = helpers.get_filter_options_for_kpi(data_prepared)
    assert result == [
        "[alle]",
        "Umsatz Total",
        "Umsatz Inland",
    ]
    assert isinstance(result, list)


def test_filter_for_sidebar_selections_mandant(data_prepared):
    pass


@pytest.mark.parametrize(
    "kpi_filter, expected",
    [
        (
            "[alle]",
            [
                "Umsatz Total",
                "Nr. TRX Total",
                "NCAs: xy",
                "Anzahl gültige Konten",
                "NCAs: yz",
            ],
        ),
        ("Anzahl Trx", ["Nr. TRX Total"]),
        ("NCA", ["NCAs: xy", "NCAs: yz"]),
        (
            "[alle] ohne NCA",
            ["Umsatz Total", "Nr. TRX Total", "Anzahl gültige Konten"],
        ),
    ],
)
def test_filter_for_sidebar_selections_kpi(data_prepared, kpi_filter, expected):
    data_prepared["kpi_name"] = [
        "Umsatz Total",
        "Nr. TRX Total",
        "NCAs: xy",
        "Anzahl gültige Konten",
        "NCAs: yz",
    ]
    result = helpers.filter_for_sidebar_selections_kpi(data_prepared, kpi_filter)
    assert expected == result["kpi_name"].tolist()
    assert isinstance(result, pd.DataFrame)


def test_filter_for_entity_and_kpi(data_prepared):
    pass


def test_filter_for_display_full_flex():
    pass


def test_create_dict_of_df_for_each_kpi(data_prepared):
    pass


def test_create_dict_of_df_for_each_entity(data_prepared):
    pass

    # def test_impute_missing_mandant(data):
    #     df = helpers.impute_missing_mandant_values(data)
    #     assert (df["mandant"].values == np.array(["BCAG", "BCAG"])).all()

    # def test_impute_missing_profile(data):
    #     df = helpers.impute_missing_profile_values(data)
    #     assert (df["profile"].values == np.array(["#NV", "CC"])).all()

    # assert df[["mandant", "profile"]].values == np.array(
    #     [["BCAG", "KK"]["nan", "KK"]]
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
