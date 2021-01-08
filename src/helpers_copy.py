import datetime as dt
import functools
import logging
import logging.config
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import streamlit as st

import data_dicts


# LOGGING_CONFIG = (Path(__file__).parent.parent / "logging.conf").absolute()
# logging.config.fileConfig(fname=LOGGING_CONFIG, disable_existing_loggers=False)
# logger = logging.getLogger("appLogger")


# def logging_runtime(func):
#     """Create a decorator that logs time for a function call.
#     Will be applied to the fucntions below for performance testing.
#     """
#     # @functools.wraps(func)
#     def logger_wrapper(*args, **kwargs):
#         """Function that logs time."""
#         start = time.time()
#         result = func(*args, **kwargs)
#         end = time.time()
#         logger.info(
#             f"Calling {func.__name__} - Elapsed time (s): {(end - start):.2f}"
#         )
#         return result

#     return logger_wrapper


# @logging_runtime
# @st.cache()  # TODO reactivate if not active
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


# @logging_runtime
# # @st.cache()
def _return_full_date_list(df: pd.DataFrame) -> List[str]:
    """Return a list of all unique dates in the dataframe, as strings
    in descending order. (This function is called within
    get_filter_options_for_due_date.)
    """
    date_list = sorted(list(df["calculation_date"].unique()), reverse=True)
    date_list = [str(np.datetime_as_string(x, unit="D")) for x in date_list]
    return date_list


# @logging_runtime
# # @st.cache()
def get_filter_options_for_due_date(
    df: pd.DataFrame, n_months_min: int = 12
) -> List[str]:
    """Return a list of available dates for the due date filter after
    removing the oldest n months from the full date list, so that a
    "minimal" period remains for comparison / calculation of the diff
    column. (n_months_min defaults to 12.)
    """
    # Note: at the moment we hide 24 months
    date_list = _return_full_date_list(df)
    if n_months_min >= len(date_list):
        raise ValueError("The observation period is too short for n_months_min.")
    elif n_months_min == 0:
        return date_list
    else:
        del date_list[-n_months_min:]
        return date_list


# @logging_runtime
# # @st.cache()
def return_max_date_string(df: pd.DataFrame) -> str:
    """Return the most recent date available from the loaded data."""
    max_date = df["calculation_date"].max()
    return max_date.strftime(format="%Y-%m-%d")


# @logging_runtime
# # @st.cache()
def return_actual_date_string(filter_now_date: str, max_date: str) -> str:
    """Return the date that will effectively be the "due date" for the
    reporting. Defaults to `max_date`, but the user can choose an earlier
    period if desired.
    """
    if filter_now_date < max_date:
        return filter_now_date
    else:
        return max_date


# @logging_runtime
# # @st.cache()
def truncate_data_to_actual_date(df: pd.DataFrame, actual_date: str) -> pd.DataFrame:
    """Remove all periods "younger" than the selected actual date and
    return the truncated data. (Note: From here on the `calcuation_date`
    column will be in datetime format.)
    """
    df["calculation_date"] = pd.to_datetime(df["calculation_date"], format="%Y-%m-%d")
    actual_date = dt.datetime.strptime(actual_date, "%Y-%m-%d")
    df = df.loc[df["calculation_date"] <= actual_date]
    return df


# @logging_runtime
# # @st.cache()
def calculate_max_n_years_available(df: pd.DataFrame) -> int:
    """Check if the truncated data still has n * 12 + 1 months or more
    in the `calculation_date` column. If yes, return n (years) as input
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
        raise ValueError("Something went wrong. Not enough data periods loaded.")


# @logging_runtime
# # @st.cache()
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
        (df["calculation_date"] <= actual_date) & (df["calculation_date"] > end_date)
    ]
    return df


# @logging_runtime
# # @st.cache()
def get_filter_options_for_result_dim(n_years: int) -> List[str]:
    """Depending on `n_years`, return a list of options for the
    "result dimension" filter (period aggregation). If `n_years`
    is 1, the 12-month option has to be removed (because we do not
    have enough data for calculation of a diff column).
    """
    # Note: For the moment this is not used because we hide the first 24 months
    options = list(data_dicts.RESULT_DIM_DICT.keys())
    if n_years > 1:
        return options
    else:
        options.remove("12 Monate rollierend")
        return options


# @logging_runtime
# # @st.cache()
def prepare_values_according_to_result_dim(
    df: pd.DataFrame, result_dim: str, actual_date: str,
) -> pd.DataFrame:
    """Prepare the `value` column according to the selected result
    dimension. If other than the default "Monat" temporarily set aside
    all kpis that cannot be cumulated, then calculate a sum for a
    rolling window of desired length and re-append the "no_sum_kpi".
    """
    if result_dim == "Monat":
        pass
    else:
        df_sum = df.loc[~df["kpi_name"].isin(data_dicts.NO_SUM_KPI)].copy()
        df_no_sum = df.loc[df["kpi_name"].isin(data_dicts.NO_SUM_KPI)]
        assert (len(df_sum) + len(df_no_sum)) == len(df)

        if result_dim == "Year To Date":
            n_months = dt.datetime.strptime(actual_date, "%Y-%m-%d").month
        else:
            n_months = data_dicts.RESULT_DIM_DICT[result_dim]

        df_sum["value"] = df_sum["value"].rolling(window=n_months).sum()
        df = pd.concat([df_sum, df_no_sum], axis=0)
    return df


# @logging_runtime
# # @st.cache()
def calculate_diff_column(df: pd.DataFrame, n_months_diff: int = 12) -> pd.DataFrame:
    """Calculate the %-difference for the KPI values between two
    periods and write it into a new colum. Return a new dataframe.
    The period lag defaults to 12 months.
    """
    df_diff = df.copy()
    df_diff["temp_index"] = pd.to_datetime(
        df_diff["calculation_date"], format="%Y-%m-%d"
    )
    df_diff.set_index("temp_index", inplace=True)

    df_diff["diff_value"] = df_diff.groupby(
        ["kpi_name", "period_id", "level", "product_name", "mandant", "cardprofile"]
    )["value"].pct_change(n_months_diff, fill_method=None)

    df_diff.reset_index(drop=True, inplace=True)

    # Capp unreasonalbe diff values (new products)
    df_diff["diff_value"] = df_diff["diff_value"].apply(
        lambda x: np.nan if not abs(x) < 10000000 else x
    )

    return df_diff


# @logging_runtime
# # @st.cache()
def create_df_with_actual_period_only(
    df: pd.DataFrame, actual_date: str
) -> pd.DataFrame:
    """Create a base dataframe for display that contains data for the
    actual period only (user choice or max date value (default)).
    """
    df = df.loc[df["calculation_date"] == actual_date]
    return df


# FILTERING FOR MANDANT AND KPI GROUPS (HIGH LEVEL, SIDEBAR)


# @logging_runtime
# # @st.cache()
def get_filter_options_for_mandant_groups(df: pd.DataFrame) -> List:
    """Return a list of the unique `mandant` values. Insert the options
     "[alle]", "BCAG" at the beginning of the list.
    """
    mandant_groups = sorted(list(df["mandant"].unique()))
    try:
        mandant_groups.remove("BCAG")
    except ValueError:
        print("WARNING: Mandant group 'BCAG' not found in the data.")
    mandant_groups.insert(0, "BCAG")
    mandant_groups.insert(0, "[alle]")
    return mandant_groups


# @logging_runtime
# # @st.cache()
def get_filter_options_for_kpi_groups() -> List:
    """Return the `KPI_GROUPS` as defined in the `data_dicts`
    module.
    """
    return list(data_dicts.KPI_GROUPS.keys())


# FILTERING FOR PRODUCT DIMENSION AND DISPLAY VIEW (SIDE BAR)


# @logging_runtime
# # @st.cache()
def filter_for_sidebar_selections_mandant(
    df: pd.DataFrame,
    filter_mandant: str,
) -> pd.DataFrame:
    """Return the dataframe filtered for the necessary `level`
    depending on selected product dim, mandant group and display view.
    """
    mandant = None
    # if filter_product_dim == "Produkt":
    # if filter_display_mode.endswith("KPI"):
    if filter_mandant == "[alle]":
        agg_level = [0, 1, 2, 3]
        sector = ["BCAG", "B2C", "B2B2C"]
    elif filter_mandant == "BCAG":
        agg_level = [0, 1]
        sector = ["BCAG", "B2C", "B2B2C"]
    elif filter_mandant == "B2B2C":
        agg_level = [1, 2, 3]
        sector = ["B2B2C"]
    elif filter_mandant == "B2C":
        agg_level = [1, 2, 3]
        sector = ["B2C"]
    else:
        agg_level = [2, 3]
        mandant = filter_mandant

    if mandant:
        return df.loc[
            (df["level"].isin(agg_level))
            & (df["mandant"] == mandant)
        ]
    else:
        return df.loc[
            (df["level"].isin(agg_level))
            & (df["sector"].isin(sector))
        ]


# @logging_runtime
# # @st.cache()
def filter_for_sidebar_selections_kpi(
    df: pd.DataFrame, filter_kpi_groups: str
) -> pd.DataFrame:
    """Return a dataframe filtered for `kpi_name` belonging to the
    selected kpi group. If not "[alle]" is selected, the filtering
    is done with `str.startswith()` using the KPI_GROUP.values().
    """
    if filter_kpi_groups == "[alle]":
        kpi_options = list(df["kpi_name"].unique())
    elif filter_kpi_groups == "[alle] ohne NCA":
        kpi_options = [
            kpi_name
            for kpi_name in list(df["kpi_name"].unique())
            if not kpi_name.startswith(data_dicts.KPI_GROUPS[filter_kpi_groups])
        ]
    else:
        kpi_options = [
            kpi_name
            for kpi_name in list(df["kpi_name"].unique())
            if kpi_name.startswith(data_dicts.KPI_GROUPS[filter_kpi_groups])
        ]
    return df.loc[df["kpi_name"].isin(kpi_options)]


# @logging_runtime
# # @st.cache()
def get_filter_options_for_entities(df: pd.DataFrame) -> List:
    """Return a list with the available entities depending on selected
    values for mandant group and product dimension in the side panel.
    Add an `[alle]` option at index 0 as default value.
    """
    entity_options = list(df["product_name"].unique())
    entity_options.insert(0, "[alle]")
    return entity_options


# @logging_runtime
# # @st.cache()
def get_filter_options_for_kpi(df: pd.DataFrame) -> List:
    """Return a list with the available kpi depending on selected
    values for kpi group. Add an `[alle]` option at index 0 as default.
    """
    kpi_options = list(df["kpi_name"].unique())
    kpi_options.insert(0, "[alle]")
    return kpi_options


# @logging_runtime
# # @st.cache()
def filter_for_entity_and_kpi(
    df: pd.DataFrame,
    filter_entity: List[str],
    filter_kpi: List[str],
) -> pd.DataFrame:
    """Filter df according to the user choices for entity and kpi.
    Only if "[alle]" is the only value in the multi-select it actually
    selects all entities. For the moment this is the desired behaviour.
    TODO: Check if behaviour of "[alle]" could be improved (low prio).
    """
    if filter_entity != ["[alle]"]:
        df = df.loc[df["product_name"].isin(filter_entity)]
    if filter_kpi != ["[alle]"]:
        df = df.loc[df["kpi_name"].isin(filter_kpi)]
    return df


# @logging_runtime
# # @st.cache()
def create_dict_of_df_for_each_kpi(
    df: pd.DataFrame
) -> Dict[str, pd.DataFrame]:
    """Slice the dataframe by distinct `kpi_name` and return a
    dict with that value as key and the respective df slice as value.
    """
    display_dict = {
        kpi: df_slice for kpi, df_slice in df.groupby("kpi_name", sort=False)
    }
    return display_dict


# @logging_runtime
# # @st.cache()
def create_dict_of_df_for_each_entity(
    df: pd.DataFrame
) -> Dict[str, pd.DataFrame]:
    """Slice the dataframe by distinct `product_name` and return a
    dict with that value as key and the respective df slice as value.
    """
    display_dict = {
        entity: df_slice for entity, df_slice in df.groupby("product_name")
    }
    return display_dict


# @logging_runtime
# # @st.cache()
def prepare_for_display(df: pd.DataFrame, filter_display_mode: str) -> pd.DataFrame:
    """Return a `display_df` with rearanged, renamed and selected
    columns for display depending on the selected display filter mode.
    """
    if filter_display_mode.endswith("KPI"):
        display_df = df[["kpi_name", "product_name", "value", "diff_value"]].copy()
        display_df.set_index("kpi_name", inplace=True)
        display_df.columns = ["Entität", "Wert", "Abw VJ"]

    else:
        display_df = df[["product_name", "kpi_name", "value", "diff_value"]].copy()
        display_df.set_index("product_name", inplace=True)
        display_df.columns = ["KPI", "Wert", "Abw VJ"]

    # display_df = display_df.reset_index(drop=True)
    return display_df


def set_bold_font(val: Any) -> str:
    """Take a scalar and return a string with css property
    `"font-weight: bold"`.
    """
    return "font-weight: bold"
