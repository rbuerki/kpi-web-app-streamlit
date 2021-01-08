import datetime as dt
import logging
import logging.config
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

import data_dicts

LOGGING_CONFIG = (Path(__file__).parent.parent / "logging.conf").absolute()
logging.config.fileConfig(fname=LOGGING_CONFIG, disable_existing_loggers=False)
logger = logging.getLogger("preprocessLogger")

SERVER = "JES2010HA01\\HA01,57226"
DB_NAME = "KF_CORE"


def connect_to_engine(server: str, db_name: str) -> Any:
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
    """Read the data from the db and return a dataframe with
    correct datatpyes (is `decimal` for value column).
    """
    result = connection.execute(query).fetchall()
    df = pd.DataFrame(result, columns=result[0].keys())
    # df["value"] = pd.to_numeric(df["value"], errors="raise", downcast="float")
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


def get_rid_of_invalid_entries(df: pd.DataFrame) -> pd.DataFrame:
    """Some entries are created by IT and do not show actual values or have
    to be (temporarily) removed for other reasons.
    """
    df = df[~df["product_name"].str.startswith("Reserviert IT")]
    # TODO: Temporarily exlcude this KPI, wrong Mandant names, no valid entity level
    df = df[df["kpi_name"] != "NCAs: Anzahl Antraege Completed Total"]
    return df


def prettify_kpi_names(df: pd.DataFrame) -> pd.DataFrame:
    """Cosmetics. Note: Replacing parantheses is a pain ..."""
    df["kpi_name"] = df["kpi_name"].str.replace("gueltig", "gültig")
    df["kpi_name"] = (
        df["kpi_name"]
        .str.replace("(", "")
        .str.replace(")", "")
        .str.replace(" Monatl.", "")
    )
    return df


def add_mandant_sector_level_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Look-up `mandant` and `sector` values from the PRODUCT_LOOK_UP
    dict (in the `data_dicts` module.) and crate new columns. Raise
    when there is a KeyError. Also create a `level` column with all
    values set to '3' (-> 'prodcut level'). Return transformed df.
    """
    try:
        df["mandant"] = df["product_name"].apply(
            lambda x: data_dicts.PRODUCT_LOOK_UP[x]["mandant"]
        )
        df["sector"] = df["product_name"].apply(
            lambda x: data_dicts.PRODUCT_LOOK_UP[x]["sector"]
        )
    except KeyError as e:
        print(f"Loaded product not in PRODUCT_LOOK_UP. LOOK_UP has to be updated!: {e}")
    df["level"] = 3

    # Sanity check
    if df.isna().sum().sum() != 0:
        raise AssertionError(
            "Ups, something went wrong: NaN values in df, please check!"
        )
    return df


def create_max_date_dict(df: pd.DataFrame) -> Dict[str, pd.Timestamp]:
    """Return a dict with each unique `product_name` as key and
    the last month it appeared in as value. (This is necessary for
    correcting the full expansion of the dataframe in a later step.)
    """
    df_max_date = df[["product_name", "calculation_date"]].copy()
    df_max_date.sort_values(["product_name", "calculation_date"], inplace=True)
    df_max_date.drop_duplicates(subset="product_name", keep="last", inplace=True)

    dict_max_date_per_entity = {e: d for e, d in df_max_date.itertuples(index=False)}
    return dict_max_date_per_entity


def expand_dataframe_fully(df: pd.DataFrame) -> pd.DataFrame:
    """Expand the dataframe to have a complete time series of
    `calculation_date` for each possible kpi, agg_level, profile combi.
    Non-existent `value` entries get a NaN entry. (This step is necessary
    to ensure correct difference calculation for the values in later
    stages - because in rare cases it is possible that some entities
    get no value for certain months. See old dev notebook's appendix for
    details on this issue.)
    """
    months = pd.DataFrame(
        {"calculation_date": sorted(df["calculation_date"].unique()), "merge_col": 0}
    )

    # All but `calculation_date` and `value`
    rest = df.drop(["calculation_date", "value"], axis=1).drop_duplicates()
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
            "product_name",
            "cardprofile",
            "mandant",
            "sector",
            "level",
        ],
    ).reset_index(drop=True)

    # Sanity check
    if df.shape[0] / len(df.groupby(["product_name", "kpi_name"]).groups.keys()) != 37:
        raise AssertionError(
            "In case you did not load 3 years, something went wrong, please check!"
        )
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
                (df["product_name"] == entity) & (df["calculation_date"] > date_)
            ].index,
            inplace=True,
        )
    return df


def create_new_mandant_level_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Retrun a dataframe with the aggregated values on MANDANT level.
    Add and fill the necessary columns so that it can be merged with the
    product level values (the original input df) later on.
    """
    df_g = df.groupby(
        ["calculation_date", "kpi_id", "kpi_name", "period_id", "mandant", "sector"]
    )["value"].sum().reset_index()
    df_g["product_name"] = df_g["mandant"] + " - Total"
    df_g["cardprofile"] = "all"
    df_g["level"] = 2
    df_g = df_g.reindex(df.columns, axis=1)

    # Sanity Check
    if df_g["value"].sum() != df["value"].sum():
        raise AssertionError("Ups, something went wrong, please check.")
    return df_g


def create_new_sector_level_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Retrun a dataframe with the aggregated values on SECTOR level.
    Add and fill the necessary columns so that it can be merged with the
    product level values (the original input df) later on.
    """
    df_g = df.groupby(
        ["calculation_date", "kpi_id", "kpi_name", "period_id", "sector"]
    )["value"].sum().reset_index()
    df_g["mandant"] = df_g["sector"]
    df_g["product_name"] = df_g["sector"] + " - Total"
    df_g["cardprofile"] = "all"
    df_g["level"] = 1
    df_g = df_g.reindex(df.columns, axis=1)

    # Sanity Check
    if df_g["value"].sum() != df["value"].sum():
        raise AssertionError("Ups, something went wrong, please check.")
    return df_g


def create_new_overall_level_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Retrun a dataframe with the aggregated values on OVERALL level.
    Add and fill the necessary columns so that it can be merged with the
    product level values (the original input df) later on.
    """
    df_g = df.groupby(
        ["calculation_date", "kpi_id", "kpi_name", "period_id"]
    )["value"].sum().reset_index()
    df_g["mandant"] = "BCAG"
    df_g["sector"] = "BCAG"
    df_g["product_name"] = df_g["sector"] + " - Total"
    df_g["cardprofile"] = "all"
    df_g["level"] = 0
    df_g = df_g.reindex(df.columns, axis=1)

    # Sanity Check
    if df_g["value"].sum() != df["value"].sum():
        raise AssertionError("Ups, something went wrong, please check.")
    return df_g


def concatenate_all_levels(
    df: pd.DataFrame,
    df_mandant: pd.DataFrame,
    df_sector: pd.DataFrame,
    df_overall: pd.DataFrame,
) -> pd.DataFrame:
    """Return a concactenated dataframe with all levels. """
    return pd.concat([df, df_mandant, df_sector, df_overall], ignore_index=True)


def add_avg_value_column(df):
    """Add an 'value_avg' column where the total value is divided
    by the 'Aktive Konten' of the respective product-date combination.
    If 'Aktive Konten' is missing, fill with np.nan.
    """
    df_grouped = df.groupby(["calculation_date", "product_name"], sort=False)
    df_w_avg = df_grouped.apply(_calc_avg_value)
    # Sanity Check
    assert df_w_avg.iloc[:, :-1].equals(df), "Uups, something went wrong."
    return df_w_avg


def _calc_avg_value(df_chunk):
    """Return the respective groupby chunk with a new avg column.
    (This is called within `add_avg_value_column`.)
    """
    try:
        n_active = float(
            df_chunk[df_chunk["kpi_name"] == "Anzahl aktive Konten Total"]
            ["value"].values[0]
        )
        df_chunk["value_avg"] = (
            (pd.to_numeric(df_chunk["value"], errors="raise", downcast="float") + 0.001)
            / n_active
        )
    except IndexError:
        df_chunk["value_avg"] = np.nan
    return df_chunk


def sort_and_drop_kpi_id(df: pd.DataFrame) -> pd.DataFrame:
    """Return a properly sorted df (important for the later aggregation
    of period values!) and then drop the `kpi_id`. It won't be used
    no more.
    """
    df = df.sort_values(
        [
            "kpi_id",
            "level",
            "mandant",
            "product_name",
            "cardprofile",
            "calculation_date",
        ]
    )
    df.drop(columns=["kpi_id"], inplace=True)
    return df


def save_to_csv(df: pd.DataFrame):
    """Save two copies of the dataframe: The 'working' file that is
    overwriting the old data and will be overwritten next month. And
    a copy that will be permanently stored in the "history" folder.
    """
    df.to_csv("./data/preprocessed_results.csv", index=False)
    # History copy with yearmon_str in name
    end_date = df["calculation_date"].max()
    yearmon_str = str(end_date.date().strftime('%Y-%m'))
    df.to_csv(f"./data/history/{yearmon_str}_preprocessed_results.csv", index=False)


def validate_and_log_results(df: pd.DataFrame):
    """Get some dataframe stats and compare some of them to expected
    values in the PREPROCESS_VALIDATION dict. If unexpected values
    are found, log warnings. (It might well be that the expected values
    in the dict have to be updated if the changes are desired.) Logging
    happens to console and the file `preprocessing.log`.
    """
    nunique_list = [f"- {col}: {df[col].nunique()}" for col in list(df.columns)[:-1]]
    nunique_str = "\n".join(nunique_list)
    nan_list = [f"- {col}: {df[col].isnull().sum()}" for col in list(df.columns)]
    nan_str = "\n".join(nan_list)
    cols_exp = data_dicts.PREPROCESS_VALIDATION["cols"]
    cols_act = list(df.columns)
    mandant_exp = sorted(data_dicts.PREPROCESS_VALIDATION["mandant"])
    mandant_act = sorted([val for val in df["mandant"].unique()])
    profile_exp = sorted(data_dicts.PREPROCESS_VALIDATION["cardprofile"])
    profile_act = sorted(
        [val for val in df["cardprofile"].unique() if isinstance(val, str)]
    )
    agg_level_id_exp = sorted(data_dicts.PREPROCESS_VALIDATION["level"])
    agg_level_id_act = sorted([val for val in df["level"].unique()])
    period_id_exp = sorted(data_dicts.PREPROCESS_VALIDATION["period_id"])
    period_id_act = sorted([val for val in df["period_id"].unique()])
    n_period_exp = data_dicts.PREPROCESS_VALIDATION["n_period"]
    n_period_act = df["calculation_date"].nunique()

    # Log infos
    logger.info(f"LOG FOR PERIOD: {df['calculation_date'].max()}")

    logger.info(
        "# of unique values per (relevant) column in processed df:\n"
        f"{nunique_str}"
    )
    logger.info("# of NaN values per column in processed df:\n" f"{nan_str}")
    logger.info(f"Total rows in dataset: {len(df):,.0f}")

    # Log warnings
    if not cols_exp == cols_act:
        logger.warning(
            f"\nData cols not as expected!\n"
            f" Expected columns are:\n {cols_exp}\n"
            f" Actual columns are:\n {cols_act}\n"
        )
    if not n_period_exp == n_period_act:
        logger.warning(
            f"\n# of unique periods not as expected!\n"
            f" Expected: {n_period_exp}, Actual: {n_period_act}\n\n"
        )
    if not mandant_exp == mandant_act:
        logger.warning(
            f"\nMandant values not as expected!\n"
            f" Expected mandants are:\n {mandant_exp}\n"
            f" Actual mandants are:\n {mandant_act}\n"
        )
    if not profile_exp == profile_act:
        logger.warning(
            f"Card profile values not as expected!\n"
            f" Expected profiles are:\n {profile_exp}\n"
            f" Actual profiles are:\n {profile_act}\n"
        )
    if not agg_level_id_exp == agg_level_id_act:
        logger.warning(
            f"Agg_level_id values not as expected!\n"
            f" Expected agg_level_ids are:\n {agg_level_id_exp}\n"
            f" Actual agg_level_ids are:\n {agg_level_id_act}\n"
        )
    if not period_id_exp == period_id_act:
        logger.warning(
            f"Period_id values not as expected!\n"
            f" Expected period_ids are:\n {period_id_exp}\n"
            f" Actual period_ids are:\n {period_id_act}\n"
        )


def main(server, db_name):
    logger.info("Start preprocessing ...")
    connection = connect_to_engine(server, db_name)
    query = read_query("sql_statements/get_results_for_kpi_sheet.sql", n_years_back=3)
    df = create_df(query, connection)
    df = create_calculation_date_column(df)
    df = trim_strings(df)
    df = get_rid_of_invalid_entries(df)
    df = prettify_kpi_names(df)
    df = add_mandant_sector_level_columns(df)
    dict_max_date_per_entity = create_max_date_dict(df)
    df = expand_dataframe_fully(df)
    df = reduce_dataframe_to_max_date_per_entity(df, dict_max_date_per_entity)
    df_mandant = create_new_mandant_level_rows(df)
    df_sector = create_new_sector_level_rows(df)
    df_overall = create_new_overall_level_rows(df)
    df = concatenate_all_levels(df, df_mandant, df_sector, df_overall)
    df = add_avg_value_column(df)
    df = sort_and_drop_kpi_id(df)
    save_to_csv(df)

    validate_and_log_results(df)
    logger.info("Preprocessing complete!\n\n")


if __name__ == "__main__":
    main(SERVER, DB_NAME)
