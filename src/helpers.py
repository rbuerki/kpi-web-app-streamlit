import datetime as dt
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import streamlit as st

import data_dicts


@st.cache()
def load_preprocessed_data(path: str) -> pd.DataFrame:
    """Load data and return a dataframe."""
    try:
        df = pd.read_csv(
            path,
            sep=",",
            engine="python",
            parse_dates=["calculation_date"],
            encoding="UTF-8",
        )
    except ValueError:
        df = pd.read_csv(
            path,
            sep=";",
            engine="python",
            parse_dates=["calculation_date"],
            encoding="UTF-8",
        )
    return df


# FILTER DISPLAY DATA


def _return_full_date_list(df: pd.DataFrame) -> List[str]:
    """Return a list of all unique dates in the dataframe, as strings
    in descending order. (This function is called within
    get_filter_values_for_due_date.)
    """
    date_list = sorted(list(df["calculation_date"].unique()), reverse=True)
    date_list = [str(np.datetime_as_string(x, unit="D")) for x in date_list]
    return date_list


def get_filter_options_for_due_date(
    df: pd.DataFrame, n_months_min: int = 12
) -> List[str]:
    """Return a list of available dates for the due date filter. Remove
    the first n months from the full date list, so that a "minimal"
    period remains for comparison / calculation of the diff column.
    (n_months_min defaults to 12.)
    """
    # Note: at the moment we hide 24 months
    date_list = _return_full_date_list(df)
    if n_months_min >= len(date_list):
        raise ValueError(
            "The observation period is too short for n_months_min."
        )
    elif n_months_min == 0:
        return date_list
    else:
        del date_list[-n_months_min:]
        return date_list


def return_max_date_string(df: pd.DataFrame) -> str:
    """Return the most recent date from the loaded data."""
    max_date = df["calculation_date"].max()
    return max_date.strftime(format="%Y-%m-%d")


def return_actual_date_string(filter_now_date: str, max_date: str) -> str:
    """Return the date that will effectively be the "due date" for the
    reporting. Defaults to `max_date`, but the user can choose an earlier
    period if desired.
    """
    if filter_now_date < max_date:
        return filter_now_date
    else:
        return max_date


def truncate_data_to_actual_date(
    df: pd.DataFrame, actual_date: str
) -> pd.DataFrame:
    """Remove all periods after the actual date and return the
    truncated data. (Note: From here on the `calcuation_date`
    column will be in datetime format.)
    """
    df["calculation_date"] = pd.to_datetime(
        df["calculation_date"], format="%Y-%m-%d"
    )
    actual_date = dt.datetime.strptime(actual_date, "%Y-%m-%d")
    df = df.loc[df["calculation_date"] <= actual_date]
    return df


def calculate_max_n_years_available(df: pd.DataFrame) -> int:
    """Check if the truncated data still has n * 12 + 1 months or more in
    the `calculation_date` column. If yes, return n (years) as input
    for further truncation. If it's lower raise an error. Max n is 3.
    """
    n_months_in_df = df["calculation_date"].nunique()

    if n_months_in_df >= 37:
        return 3
    elif n_months_in_df >= 25:
        return 2
    elif n_months_in_df >= 13:
        return 1
    else:
        raise ValueError(
            "Something went wrong. Not enough data periods loaded."
        )


def truncate_data_n_years_back(
    df: pd.DataFrame, actual_date: str, n_years: int
) -> pd.DataFrame:
    """Depending on `n_years`, truncate and return the data to either
    37, 25 or 13 months back from the actual date (including it).
    Note: 25/13 months, not 37/24/12, is necessary for proper resampling!

    Note: If the result_dim "ytd" is chosen, we will have to truncate once
    more in a later step. (Because again: we need n * n_month + 1 periods
    for proper resampling.)
    """
    actual_date = dt.datetime.strptime(actual_date, "%Y-%m-%d")
    assert actual_date == df["calculation_date"].max()
    end_date = dt.datetime(actual_date.year - n_years, actual_date.month, 1)
    df = df.loc[
        (df["calculation_date"] <= actual_date)
        & (df["calculation_date"] > end_date)
    ]
    return df


def get_filter_options_for_result_dim(n_years: int) -> List[str]:
    """Depending on `n_years`, return a list of options for the
    "result dimension" filter (period aggregation). If `n_years`
    is 1, the 12-month option has to be removed (because we do not
    have enough data for calculation of a diff column).
    """
    # Note: at the moment this is not used because we hide 24 months
    options = list(data_dicts.RESULT_DIM_DICT.keys())
    if n_years > 1:
        return options
    else:
        options.remove("12 Monate rollierend")
        return options


def prepare_values_according_to_result_dim(
    df: pd.DataFrame, result_dim: str, actual_date: str,
) -> pd.DataFrame:
    """Prepare the `value` column according to the selected result
    dimension. If other than the default "Monat" drop all kpis that
    cannot be cumulated and then calculate a sum for a rolling window
    of desired length.
    """
    if result_dim == "Monat":
        pass
    else:
        df = df.loc[~df["kpi_name"].isin(data_dicts.NO_SUM_KPI)]
        if result_dim == "Year To Date":
            n_months = dt.datetime.strptime(actual_date, "%Y-%m-%d").month
        else:
            n_months = data_dicts.RESULT_DIM_DICT[result_dim]
        df["value"] = df["value"].rolling(window=n_months).sum()
    return df


def calculate_diff_column(
    df: pd.DataFrame, n_months_diff: int = 12
) -> pd.DataFrame:
    """Calculate the %-difference for the KPI values between two periods
    and append it in a new colum. Return a new dataframe. The period
    lag defaults to 12 months.
    """
    df_diff = df.copy()
    df_diff["temp_index"] = pd.to_datetime(
        df_diff["calculation_date"], format="%Y-%m-%d"
    )
    df_diff.set_index("temp_index", inplace=True)
    df_diff["diff_value"] = df_diff.groupby(
        ["kpi_name", "period_id", "agg_level_id", "agg_level_value", "mandant"]
    )["value"].pct_change(n_months_diff)
    df_diff.reset_index(drop=True, inplace=True)
    return df_diff


def create_df_with_actual_period_only(
    df: pd.DataFrame, actual_date: str
) -> pd.DataFrame:
    """Create a base dataframe for display that contains data for the
    actual period only (user choice or max date value (default)).
    """
    df = df.loc[df["calculation_date"] == actual_date]
    return df


# FILTERING FOR MANDAND GROUPS (HIGH LEVEL, SIDEBAR)


def get_filter_options_for_mandant_groups(df: pd.DataFrame) -> List:
    """Return the `agg_level_values` for `agg_level_id` on the "high"
    agg_levels (Overall and Mandant) only. Insert the options "[alle]",
    "Overall" at the beginning of the list.
    """
    mandant_options = sorted(list(df["mandant"].unique()))
    try:
        mandant_options.remove("Overall")
    except ValueError:
        print("Mandant group 'Overall' not found in the data.")
    mandant_options.insert(0, "Overall")
    mandant_options.insert(0, "[alle]")
    return mandant_options


# FILTERING FOR PRODUCT DIMENSION AND DISPLAY VIEW (SIDE BAR)


def filter_for_sidebar_selections(
    df: pd.DataFrame,
    filter_display_mode: str,
    filter_product_dim: str,
    filter_mandant: str,
) -> pd.DataFrame:
    """Return the dataframe filtered for the necessary `agg_level_id`
    depending on selected product dim, mandant group and display view.
    """
    if filter_product_dim == "Produkt":
        if filter_display_mode.endswith("KPI"):
            if filter_mandant == "Overall":
                agg_level = [1, 4]
            else:
                agg_level = [1, 4, 5]
        elif filter_display_mode.endswith("Entität"):
            if filter_mandant == "Overall":
                agg_level = [1, 4]
            else:
                agg_level = [1, 4, 5]

    elif filter_product_dim == "Kartenprofil":
        if filter_display_mode.endswith("KPI"):
            if filter_mandant == "Overall":
                agg_level = [1, 2]
            elif filter_mandant == "[alle]":
                agg_level = [3]
            else:
                agg_level = [4, 3]
        elif filter_display_mode.endswith("Entität"):
            if filter_mandant == "Overall":
                agg_level = [2]
            else:
                agg_level = [3]

    return df.loc[df["agg_level_id"].isin(agg_level)]


def get_filter_options_for_entities(
    df: pd.DataFrame, filter_mandant: str
) -> List:
    """Return a list with the available entities depending on selected
    values for mandant group and product dimension in the side panel.
    Add an `[alle]` option at index 0 as default.
    """
    if (filter_mandant == "[alle]") or (filter_mandant == "Overall"):
        entity_options = list(df["agg_level_value"].unique())
    else:
        entity_options = list(
            df.loc[df["mandant"] == filter_mandant]["agg_level_value"].unique()
        )
    entity_options.insert(0, "[alle]")
    return entity_options


def get_filter_options_for_kpi(df: pd.DataFrame) -> List:
    """Return a list with the available kpi depending on selected
    values for mandant group and view.
    """
    # TODO: No kpi groups implemented yet, this will come in a next phase
    kpi_options = list(df["kpi_name"].unique())
    kpi_options.insert(0, "[alle]")
    return kpi_options


def filter_for_entity_and_kpi(
    df: pd.DataFrame,
    filter_entity: List[str],
    filter_kpi: List[str],
    filter_mandant: str,
) -> pd.DataFrame:
    """Filter df_display according to the user choices on entity and kpi."""
    # TODO in case we group kpis I have to split the two filters
    if filter_entity != ["[alle]"]:
        df = df.loc[df["agg_level_value"].isin(filter_entity)]
    elif filter_mandant not in ["[alle]", "Overall"]:
        df = df.loc[df["mandant"] == filter_mandant]
    if filter_kpi != ["[alle]"]:
        df = df.loc[df["kpi_name"].isin(filter_kpi)]
    return df


def create_dict_of_df_for_each_kpi(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Iterate through all unique `kpi_names` in dataframe and return a
    dict with that value as key and a dataframe subset for that kpi
    as value.
    """
    display_dict = {}
    filter_kpi = df["kpi_name"].unique()
    for kpi in filter_kpi:
        df_kpi = df.loc[df["kpi_name"] == kpi]
        display_dict[kpi] = df_kpi
    return display_dict


def create_dict_of_df_for_each_entity(
    df: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """Iterate through all `agg_level_values` in dataframe and return a
    dict with that value as key and a dataframe subset for that entity
    as value.
    """
    display_dict = {}
    for entity in df["agg_level_value"]:
        df_entity = df.loc[df["agg_level_value"] == entity]
        display_dict[entity] = df_entity
    return display_dict


def arrange_for_display_per_entity(df: pd.DataFrame) -> pd.DataFrame:
    """Rearange and filter columns for display."""
    cols = ["kpi_name", "value", "diff_value"]
    display_df = df[cols].copy()
    display_df.columns = ["KPI", "Wert", "Abw VJ"]
    display_df = display_df.reset_index(drop=True)
    return display_df


def arrange_for_display_per_kpi(
    df: pd.DataFrame, filter_product_dim: str, filter_mandant: str,
) -> pd.DataFrame:
    """Return a `display_df` with rearanged, renamed and selected
    columns for display. (Note: this function shares logic and code
    with the `style_for_export` function in the `downloads`module.)
    """
    display_df = df.copy()
    if not filter_product_dim.startswith("Prod"):
        # Overall is different from rest (-> higher level has lower id)
        if not filter_mandant == "Overall":
            display_df.sort_values(
                ["agg_level_id", "agg_level_value"],
                ascending=False,
                inplace=True,
            )
    cols = ["agg_level_value", "value", "diff_value"]
    display_df = display_df[cols]
    display_df.columns = ["Entität", "Wert", "Abw VJ"]
    display_df = display_df.reset_index(drop=True)
    return display_df


def set_bold_font(val: Any) -> str:
    """Take a scalar and return a string with css property
    `"font-weight: bold"`.
    """
    return "font-weight: bold"
