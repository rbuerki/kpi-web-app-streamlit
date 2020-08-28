import datetime as dt
from typing import Any, Dict

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

server = "JES2010HA01\\HA01,57226"
db_name = "KF_CORE"


def connect_to_engine(sever: str, db_name: str) -> Any:
    """Assemble a connection string, connect to the db engine and
    return a connection object.
    """
    con_string = f"mssql+pyodbc://@{server}/{db_name}?driver=SQL Server"
    engine = create_engine(con_string)
    connection = engine.connect()
    return connection


def read_query(file_path: str, n_years_back: int = 3) -> str:
    """Open the sql-query file, parse and return the query while
    replacing the placeholder with the value of the n years
    you want to get the data back for (defaults to 3).
    """
    with open(file_path, "r", encoding="utf-8-sig") as file:
        query = file.read()
    query = query.replace("@n_years_back", str(n_years_back))
    return query


def create_df(query, connection):
    """Read the data from the db and return a dataframe."""
    result = connection.execute(query).fetchall()
    df = pd.DataFrame(result, columns=result[0].keys())
    return df


def create_calculation_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """Replace the `period_value`with a "calculation date" that is
    set to the last day of the same month. (Note: this is not equal
    to the actual calculation date as defined in the DB.)
    """
    df["period_value"] = pd.to_datetime(df["period_value"], format="%Y%m")
    df["period_value"] = df["period_value"].apply(lambda x: _get_last_day_of_month(x))
    return df.rename(columns={"period_value": "calculation_date"},)


def _get_last_day_of_month(some_date):
    """Return date of last day of the same month for a datetime object."""
    next_month = some_date.replace(day=28) + dt.timedelta(
        days=4
    )  # this will never fail
    return next_month - dt.timedelta(days=next_month.day)


def trim_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace from right end of every string in the dataframe."""
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def prettify_kpi_names(df):
    """Replacing parantheses is a pain ..."""
    df["kpi_name"] = df["kpi_name"].str.replace("gueltig", "gültig")
    df["kpi_name"] = (
        df["kpi_name"]
        .str.replace("(", "")
        .str.replace(")", "")
        .str.replace(" Monatl.", "")
    )
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
        df["mandant"].str.endswith(" CC"),
        df["mandant"].apply(lambda x: x[:-3]),
        df["mandant"],
    )
    df["mandant"] = np.where(
        df["mandant"].str.endswith(" CCL"),
        df["mandant"].apply(lambda x: x[:-4]),
        df["mandant"],
    )

    # Just to make sure that no right spaces pollutes my strings ;-)
    df["mandant"] = df["mandant"].apply(lambda x: x.rstrip())
    return df


def impute_missing_cardprofile_values_1(df: pd.DataFrame) -> pd.DataFrame:
    """Impute the expected missing values for cardprofile.

    On the higher agg_levels 2, 3, 4 the value for `cardprofile` is
    not provided, so we have to impute the (cleaned) string form
    "agg_level_value".
    """
    for profile_str in ["CC", "PP", "CCL"]:
        df["cardprofile"] = np.where(
            (df["agg_level_id"].isin([2, 3, 4]))
            & (df["agg_level_value"].str.endswith(profile_str)),
            profile_str,
            df["cardprofile"],
        )
    return df


# def impute_missing_cardprofile_values_2(df: pd.DataFrame) -> pd.DataFrame:
#     """For the NCA kpi family we can impute the `cardprofile`
#     values from the `kpi_name`. - But not sure if this makes sense ...
#     """
#     # TODO replace "CH" with "CCL" as soon as kpi_names in DB are updated
#     for profile_str in ["CC", "PP", "CH"]:
#         df["cardprofile"] = np.where(
#             (df["agg_level_id"].isin([1, 4]))
#             & (df["cardprofile"].isnull())
#             & (df["kpi_name"].str.endswith(profile_str)),
#             profile_str,
#             df["cardprofile"],
#         )
#     return df


def create_max_date_dict(df: pd.DataFrame) -> Dict[str, pd.Timestamp]:
    """Return a dict with each unique `agg_level_value` as key and
    the last month it appeared in as value. (This is necessary for
    correcting the full expansion of the dataframe in a later step.)
    """
    df_max_date = df[["agg_level_value", "calculation_date"]].copy()
    df_max_date.sort_values(["agg_level_value", "calculation_date"], inplace=True)
    df_max_date.drop_duplicates(subset="agg_level_value", keep="last", inplace=True)

    dict_max_date_per_entity = {e: d for e, d in df_max_date.itertuples(index=False)}
    return dict_max_date_per_entity


def expand_dataframe_fully(df: pd.DataFrame) -> pd.DataFrame:
    """Expand the dataframe to have a complete time series of
    `calculation_date` for each possible kpi, agg_level, profile combi.
    Non-existent `value` values get a NaN entry. (This step is necessary
    to ensure correct difference calculation for the values in later
    stages - because in rare cases it is possible that some entities
    get no value for certain months. See dev notebook's appendix for
    details on this issue.)
    """
    months = pd.DataFrame(
        {"calculation_date": sorted(df["calculation_date"].unique()), "merge_col": 0}
    )

    rest = df[
        [
            "kpi_id",
            "kpi_name",
            "period_id",
            "agg_level_id",
            "agg_level_value",
            "mandant",
            "cardprofile",
        ]
    ].drop_duplicates()
    rest["merge_col"] = 0

    temp_tbl = months.merge(rest, how="outer", on="merge_col")
    temp_tbl = temp_tbl.drop(columns={"merge_col"})
    temp_tbl = temp_tbl.sort_values(["kpi_id", "calculation_date"])

    df = temp_tbl.merge(
        df,
        how="left",
        on=[
            "calculation_date",
            "kpi_id",
            "kpi_name",
            "period_id",
            "agg_level_id",
            "agg_level_value",
            "mandant",
            "cardprofile",
        ],
    ).reset_index(drop=True)
    return df


def reduce_dataframe_to_max_date_per_entity(
    df: pd.DataFrame, dict_max_date_per_entity: Dict[str, pd.Timestamp]
) -> pd.DataFrame:
    """For each entity drop all rows for calculation_dates that are
    larger than it's max date before the full expansion. So we make sure
    to display entities only that still exist(ed) at any point in time.
    """
    for entity, date_ in dict_max_date_per_entity.items():
        df.drop(
            df.loc[
                (df["agg_level_value"] == entity) & (df["calculation_date"] > date_)
            ].index,
            inplace=True,
        )
    return df


def sort_and_drop_kpi_id(df: pd.DataFrame) -> pd.DataFrame:
    """Return a properly sorted df (important for the later aggregation
    of period values!) and then drop the `kpi_id`. It won't be used
    no more.
    """
    df = df.sort_values(
        [
            "kpi_id",
            "period_id",
            "agg_level_id",
            "agg_level_value",
            "mandant",
            "cardprofile",
            "calculation_date",
        ]
    )
    df.drop(columns=["kpi_id"], inplace=True)
    return df


def main():
    connection = connect_to_engine(server, db_name)
    query = read_query("sql_statements/get_results_for_kpi_sheet.sql", n_years_back=3)
    df = create_df(query, connection)
    df = create_calculation_date_column(df)
    df = trim_strings(df)
    df = prettify_kpi_names(df)
    df = impute_missing_mandant_values(df)
    df = impute_missing_cardprofile_values_1(df)
    # df = impute_missing_cardprofile_values_2(df)  # TODO remove if not used
    dict_max_date_per_entity = create_max_date_dict(df)
    df = expand_dataframe_fully(df)
    df = reduce_dataframe_to_max_date_per_entity(df, dict_max_date_per_entity)
    df = sort_and_drop_kpi_id(df)
    df.to_csv("./data/preprocessed_results.csv", index=False)


if __name__ == "__main__":
    main()
