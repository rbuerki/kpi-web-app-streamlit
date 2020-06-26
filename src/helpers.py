import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

import data_dicts


# @st.cache()
def load_data(path: str) -> pd.DataFrame:
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


# DATA PREPROCESSING
# ------------------


def trim_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace from right end of every string in the dataframe."""
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def impute_missing_mandant_values(df: pd.DataFrame) -> pd.DataFrame:
    """Impute the expected missing values for mandant."""
    df["mandant"] = np.where(
        df["agg_level_id"].isin([1, 2]), "Overall", df["mandant"]
    )
    df["mandant"] = np.where(
        (df["agg_level_id"].isin([3, 4])), df["agg_level_value"], df["mandant"]
    )
    df["mandant"] = np.where(
        df["mandant"].str.endswith(" PP"),
        df["mandant"].apply(lambda x: x[:-3]),
        df["mandant"],
    )
    df["mandant"] = np.where(
        df["mandant"].str.endswith(" KK"),
        df["mandant"].apply(lambda x: x[:-3]),
        df["mandant"],
    )
    return df


def impute_missing_profile_values(df: pd.DataFrame) -> pd.DataFrame:
    """Impute the expected missing values for profile.

    On the higher agg_levels 2, 3, 4 the value for `mandant` is
    not provided, so we have to impute the (cleaned) string form
    "agg_level_value".
    """
    df["profile"] = np.where(
        (df["agg_level_id"].isin([2, 3, 4]))
        & (df["agg_level_value"].str.endswith("KK")),
        "CC",
        df["profile"],
    )
    df["profile"] = np.where(
        (df["agg_level_id"].isin([2, 3, 4]))
        & (df["agg_level_value"].str.endswith("PP")),
        "PP",
        df["profile"],
    )
    return df


def replace_kpi_ids_with_kpi_names(
    df: pd.DataFrame, kpi_dict: Dict[int, str]
) -> pd.DataFrame:
    """Map values in column `kpi_id` with kpi_names and change
    the column name to `kpi`.
    """
    kpi_dict = data_dicts.kpi_dict
    df["kpi_id"] = df["kpi_id"].apply(lambda x: kpi_dict.get(x, np.nan))
    df.rename(columns={"kpi_id": "kpi"}, inplace=True)
    return df


def fix_two_periods_for_comparison(
    df: pd.DataFrame,
) -> Tuple[np.datetime64, np.datetime64]:
    """Return the date of the actual period (last available full month,
    called "now"), and the date for the same month one year back ("then")."""
    date_now = df["calculation_date"].max()
    date_then = dt.datetime(date_now.year - 1, date_now.month, date_now.day)
    return date_now, date_then


def create_df_diff(
    df: pd.DataFrame, periods_diff: Tuple[np.datetime64, np.datetime64]
) -> pd.DataFrame:
    """Create a temporary dataframe for calculation of the
    difference from "now" to "then"."""
    df_diff = df.loc[df["calculation_date"].isin(periods_diff)].copy()
    return df_diff


def pivot_df_diff_periods_to_columns(df_diff: pd.DataFrame) -> pd.DataFrame:
    """Create a column each for the `now` and `then` periods."""
    df_diff = df_diff.pivot_table(
        index=[
            "kpi",
            "period_id",
            "agg_level_id",
            "agg_level_value",
            "mandant",
        ],
        columns="calculation_date",
    ).reset_index()
    # TODO - this needs an Assertion that now date is bigger than then date
    cols = list(df_diff.columns.get_level_values(0))[:-2] + ["then", "now"]
    df_diff.columns = cols
    return df_diff


def calculate_diff_now_to_then(df_diff: pd.DataFrame) -> pd.DataFrame:
    """Create a new column `diff_value` containing the difference
    in percentage points of `now` and `then`.
    """
    df_diff["diff_value"] = (df_diff["now"] / df_diff["then"]) - 1
    df_diff.drop(["now", "then"], axis=1, inplace=True)
    return df_diff


def append_diff_value_column_to_original_df(
    df: pd.DataFrame, df_diff: pd.DataFrame
) -> pd.DataFrame:
    """Left join to append the `diff_value` column to the original dataframe.

    Note: As for simplicity's sake we do not merge on `calculation_date`
    column we will have to remove the values from all but the actual period.
    """
    df = pd.merge(
        df,
        df_diff,
        how="left",
        on=["kpi", "period_id", "agg_level_id", "agg_level_value", "mandant"],
    )
    return df


def remove_diff_values_for_non_actual_data(
    df: pd.DataFrame, now: np.datetime64
) -> pd.DataFrame:
    """Remove the values in `diff_value` for all rows which
    are not in the actual period."""
    df["diff_value"] = np.where(
        df["calculation_date"] != now, np.nan, df["diff_value"]
    )
    return df


# SELECT DISPLAY DATA
# -------------------


def create_df_with_actual_period_only(df: pd.DataFrame) -> pd.DataFrame:
    """Create a base dataframe for display that contains
    only data for the actual period (max date value)."""
    max_date = df["calculation_date"].max()
    df_display = df.loc[df["calculation_date"] == max_date]
    return df_display


def select_monthly_vs_ytd(df: pd.DataFrame, result_period: str) -> pd.DataFrame:
    "Filter if monthly or ytd values are to be displayed, return filtered dataframe."
    # TODO: Check the ID values in the final data model, 6 doesn't exist yet
    if result_period.startswith("M"):
        df_display = df.loc[df["period_id"].isin([1, 2])]
    else:
        df_display = df.loc[df["period_id"].isin([5, 6])]
    return df_display


# FILTERING FOR DRILLDOWN (VERSION 1A & 1B, VIEWS KPI AND ENTITY)


def get_filter_dict(df):
    df_filter = df[["agg_level_value", "agg_level_id"]].drop_duplicates()
    filter_dict = {k.strip(): v for k, v in df_filter.itertuples(index=False)}
    return filter_dict


def get_filter_values_1(filter_dict):
    return [k for k, v in filter_dict.items() if v in (1, 4)]


def filter_for_display(
    df: pd.DataFrame,
    mandant: Optional[str] = None,
    agg_level: Optional[List[str]] = None,
    kpi: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Filter df_display according tho the filters set in the front end."""
    # TODO complete filter logics (kpi not implemented yet)
    if mandant is not None and mandant != "Overall":
        df = df.loc[df["mandant"] == mandant]
    if agg_level is not None:
        df = df.loc[df["agg_level_id"].isin(agg_level)]
    if kpi is not None:
        df = df.loc[df["kpi"] == kpi]
    return df


# VERSION 1A: VIEW WITH DFs of ENTITY PER KPI


def create_dict_of_df_per_kpi(
    df: pd.DataFrame, selected_kpi: List
) -> Dict[str, pd.DataFrame]:
    """Title says it."""
    display_dict = {}
    if selected_kpi == ["all"] or selected_kpi == []:
        selected_kpi = df["kpi"].unique()
    else:
        if "all" in selected_kpi:
            selected_kpi.remove("all")
    for kpi in selected_kpi:
        df_kpi = df.loc[df["kpi"] == kpi]
        display_dict[kpi] = df_kpi
    return display_dict


def arrange_for_display_per_kpi(df: pd.DataFrame) -> pd.DataFrame:
    """Rearange and filter columns for display."""
    # df.sort_values(["agg_level_id", "agg_level_value"], inplace=True)
    cols = ["agg_level_value", "value", "diff_value"]
    display_df = df[cols].copy()
    display_df.columns = ["Entität", "Wert", "Abw 12Mte"]
    display_df = display_df.reset_index(drop=True)
    return display_df


def set_bold_font(val: Any) -> str:
    """Take a scalar and return a string with css property `"font-weight: bold"`."""
    return "font-weight: bold"


# VERSION 1B: VIEW WITH DFs of KPI PER ENTITY


def create_dict_of_df_per_entity(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Title says it."""
    display_dict = {}
    for entity in df["agg_level_value"]:
        df_entity = df.loc[df["agg_level_value"] == entity]
        display_dict[entity] = df_entity
    return display_dict


def arrange_for_display_per_entity(df: pd.DataFrame) -> pd.DataFrame:
    """Rearange and filter columns for display."""
    # df.sort_values(["agg_level_id", "agg_level_value"], inplace=True)
    cols = ["kpi", "value", "diff_value"]
    display_df = df[cols].copy()
    display_df.columns = ["KPI", "Wert", "Abw 12Mte"]
    display_df = display_df.reset_index(drop=True)
    return display_df


# VERSION FLEX: FULL-FLEX FILTERING


def get_filter_lists_full_flex(df: pd.DataFrame) -> Tuple[list, list]:
    """Return two list with unique values for kpis and entities from dataframe."""
    kpi_list = list(df["kpi"].unique())
    kpi_list.insert(0, "all")
    entity_list = list(df["agg_level_value"].unique())
    entity_list.insert(0, "all")
    return kpi_list, entity_list


# TODO: Check for non-existing combinations - see how I did for Ver. 1
def filter_for_display_full_flex(
    df: pd.DataFrame, entity_list: List[str], kpi_list: List[str],
) -> pd.DataFrame:
    """Filter df_display according tho the filters set in the front end."""
    # TODO complete filter logics (kpi not implemented yet)
    if entity_list != ["all"]:
        df = df.loc[df["agg_level_value"].isin(entity_list)]
    if kpi_list != ["all"]:
        df = df.loc[df["kpi"].isin(kpi_list)]
    return df
