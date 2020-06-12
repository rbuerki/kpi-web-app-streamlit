import datetime as dt
import pandas as pd
import streamlit as st
from data_dicts import kpi_dict


@st.cache()
def load_data(path):
    """Load dataframe from path."""
    df = pd.read_csv(path, sep=";", engine="python", parse_dates=["calculation_date"])
    return df


def trim_strings(df):
    """Trim whitespace from ends of each string value across all series in dataframe."""
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def get_dates(df):
    """Get relevant dates for filtering the data (last month and 12 months back.)"""
    date_now = df["calculation_date"].max()
    date_12months = dt.datetime(date_now.year - 1, date_now.month, date_now.day)
    return date_now, date_12months


def filter_data(df, dates):
    # We need date_now and date_12months only
    df = df.loc[df["calculation_date"].isin(dates)]
    # We need period_id = 2 only (ASSUMPTION)
    df = df.loc[df["period_id"] == 2]
    df.drop("period_id", axis=1, inplace=True)
    return df


def pivot_dates(df):
    df = df.pivot_table(
        index=["kpi_id", "agg_level_id", "agg_level_value", "mandant"],
        columns="calculation_date",
    ).reset_index()
    # TODO - this needs an assert that I have the right column order!
    cols = list(df.columns.get_level_values(0))[:-2] + ["12months", "value"]
    df.columns = cols
    return df


def calculate_diff_12months(df):
    df["diff_12months"] = (df["value"] / df["12months"]) - 1
    # df.drop("12months", axis=1, inplace=True)
    return df


# def calculate_diff_ytd(df):
#     df["diff_ytd"] = (df["value"] / df["ytd"]) - 1
#     # df.drop("12months", axis=1, inplace=True)
#     return df


def filter_for_display(df, mandant=None, agg_level=None, kpi_id=None):
    """In case specific filters are set - defaults should not be None probably."""
    # TODO complete filter logics
    if mandant is not None and mandant != "Overall":
        # mandant = mandant.rstrip()
        df = df.loc[df["mandant"] == mandant]
    if agg_level is not None:
        df = df.loc[df["agg_level_id"].isin(agg_level)]
    if kpi_id is not None:
        df = df.loc[df["kpi_id"] == kpi_id]
    return df


def iter_through_kpi_ids(df):
    display_dict = {}
    for kpi_id in df["kpi_id"]:
        df_kpi = df.loc[df["kpi_id"] == kpi_id]
        kpi_name = kpi_dict[kpi_id]
        display_dict[kpi_name] = df_kpi
    return display_dict


def style_for_display(df):
    """Rearange and filter columns for display."""
    # df.sort_values(["agg_level_id", "agg_level_value"], inplace=True)
    cols = ["agg_level_value", "value", "diff_12months"]
    display_df = df[cols].copy()
    display_df.columns = ["Entität", "Wert", "Abw 12Mte (%)"]
    return display_df


def get_filter_dict(df):
    df_filter = df[["agg_level_value", "agg_level_id"]].drop_duplicates()
    filter_dict = {k.strip(): v for k, v in df_filter.itertuples(index=False)}
    return filter_dict


def get_filter_values_1(filter_dict):
    return [k for k, v in filter_dict.items() if v in (1, 4)]


# # TESTING AREA
# data = load_data("data/raw/mock_data.csv")
# data = trim_strings(data)
# dates = get_dates(data)
# data = filter_data(data, dates)
# data = pivot_dates(data)
# data = calculate_diff_12months(data)
# style_for_display(data)
# mandant="SWISS"
# agg_level=[1, 4, 3]
# # data = filter_for_display(data, mandant=mandant, agg_level=agg_level, kpi_id=None)

# data = data.loc[(data["agg_level_id"] == 5)]
# # data = data.loc[(data["mandant"] == "SWISS")]

# print(data.info())
# print(data["mandant"].unique())

# now, then = get_dates(data)
# print (dates)
