import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

from data_dicts import kpi_dict  # when running

# from kpi_app.data_dicts import kpi_dict  # for testing


@st.cache()
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


def trim_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace from right end of every string in the dataframe."""
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def impute_missing_mandant_values(df: pd.DataFrame) -> pd.DataFrame:
    """Impute the expected missing values for mandant."""
    df["mandant"] = np.where(df["agg_level_id"].isin([1, 2]), "Overall", df["mandant"])
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
    """Impute the expected missing values for profile."""
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
    """Map values in column kpi_id and change the column name."""
    df["kpi_id"] = df["kpi_id"].apply(lambda x: kpi_dict.get(x, np.nan))
    df.rename(columns={"kpi_id": "kpi"}, inplace=True)
    return df


def fix_two_periods_for_comparison(
    df: pd.DataFrame,
) -> Tuple[np.datetime64, np.datetime64]:
    """Fix the date of the actual period (last full month), and for the same 12 months back."""
    date_now = df["calculation_date"].max()
    date_then = dt.datetime(date_now.year - 1, date_now.month, date_now.day)
    return date_now, date_then


def create_df_diff(
    df: pd.DataFrame, periods_diff: Tuple[np.datetime64, np.datetime64]
) -> pd.DataFrame:
    """Create a dataframe for calculation of the comparision now to then."""
    df_diff = df.loc[df["calculation_date"].isin(periods_diff)].copy()
    # # TODO: Check if I have selected the right period_ids. This will change in the data model!
    # df = df.loc[df["period_id"].isin(1, 2, 6)]
    # df.drop("period_id", axis=1, inplace=True)
    return df_diff


def pivot_df_diff_periods_to_columns(df_diff: pd.DataFrame) -> pd.DataFrame:
    """Create a column each for the now and then periods."""
    df_diff = df_diff.pivot_table(
        index=["kpi", "period_id", "agg_level_id", "agg_level_value", "mandant"],
        columns="calculation_date",
    ).reset_index()
    # TODO - this needs an assert that I have the right column order!
    # print(df_diff.columns)
    cols = list(df_diff.columns.get_level_values(0))[:-2] + ["then", "now"]
    df_diff.columns = cols
    return df_diff


def calculate_diff_now_to_then(df_diff: pd.DataFrame) -> pd.DataFrame:
    """Create a new column containing the difference in values of "now" and "then"."""
    df_diff["diff_value"] = (df_diff["now"] / df_diff["then"]) - 1
    df_diff.drop(["now", "then"], axis=1, inplace=True)
    return df_diff


def append_diff_value_to_original_df(df: pd.DataFrame, df_diff: pd.DataFrame):
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
    """Remove the diff values for all datapoints that are not of actual period. They are wrong."""
    df["diff_value"] = np.where(df["calculation_date"] != now, np.nan, df["diff_value"])
    return df


# df = load_data("../data/test/mock_13months_10kpi.csv")
# # df = df.iloc[:10000, :].copy()
# df = trim_strings(df)
# df = impute_missing_mandant_values(df)
# df = impute_missing_profile_values(df)
# df = replace_kpi_ids_with_kpi_names(df, kpi_dict)
# periods_diff = fix_two_periods_for_comparison(df)
# df_diff = create_df_diff(df, periods_diff)
# df_diff = pivot_df_diff_periods_to_columns(df_diff)
# df_diff = calculate_diff_now_to_then(df_diff)
# df = append_diff_value_to_original_df(df, df_diff)
# df = remove_diff_values_for_non_actual_data(df, periods_diff[0])
# df.to_csv("../data/test/mock_preprocessed.csv", index=False)


def create_df_with_actual_period_only(df: pd.DataFrame) -> pd.DataFrame:
    """Create a base dataframe for display that contains only data for the actual period (max date value)."""
    max_date = df["calculation_date"].max()
    df_display = df.loc[df["calculation_date"] == max_date]
    # TODO: FOR DEMO I ALSO FILTER THE period_id. THIS WILL HAVE TO CHANGE WHEN THE DATAMODEL IS FIX.
    df_display = df_display.loc[df_display["period_id"] == 2]
    return df_display


def filter_for_display(
    df: pd.DataFrame,
    mandant: Optional[str] = None,
    agg_level: Optional[List[str]] = None,
    kpi: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Filter df_display according tho the filters set in the front end."""
    # TODO complete filter logics (kpi not implemented yet)
    if mandant is not None and mandant != "Overall":
        # mandant = mandant.rstrip()
        df = df.loc[df["mandant"] == mandant]
    if agg_level is not None:
        df = df.loc[df["agg_level_id"].isin(agg_level)]
    if kpi is not None:
        df = df.loc[df["kpi"] == kpi]
    return df


def create_dict_of_df_per_kpi(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Title says it."""
    display_dict = {}
    for kpi in df["kpi"]:
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


def get_filter_dict(df):
    df_filter = df[["agg_level_value", "agg_level_id"]].drop_duplicates()
    filter_dict = {k.strip(): v for k, v in df_filter.itertuples(index=False)}
    return filter_dict


def get_filter_values_1(filter_dict):
    return [k for k, v in filter_dict.items() if v in (1, 4)]


def set_bold_font(val: Any) -> str:
    """Take a scalar and return a string with css property `"font-weight: bold"`."""
    return "font-weight: bold"


# ALTERNATIVE VIEW WITH DFs of KPI PER ENTITY


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
