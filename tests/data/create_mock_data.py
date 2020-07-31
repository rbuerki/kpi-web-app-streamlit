#! usr/bin/python3

import argparse
from typing import List

import datetime as dt
import numpy as np
import pandas as pd


def load_data(path):
    """Load dataframe with single period / kpi combination from path, parse dates."""
    df = pd.read_csv(path, sep=";", engine="python", parse_dates=["calculation_date"])
    return df


def multiply_kpis(df: pd.DataFrame, n_kpi: int) -> pd.DataFrame:
    """Create rows for a number of new kpi_ids."""
    df_append = df.copy()
    for i in range(2, (n_kpi + 1)):
        try:
            df_append["kpi_id"] = i
        except ValueError as e:
            print(e)
        df = df.append(df_append, ignore_index=True)
    return df


def randomize_values(col: pd.Series) -> pd.Series:
    """Helper function, varies the value with a random multiplication."""
    return col.astype(float).apply(lambda x: x * np.random.uniform(0.9, 1.05))


def generate_periods(ts: dt.datetime, n_years: int) -> List[np.datetime64]:
    """Generate a series of Timestamps with last day of the month for past n years."""
    ts_start = dt.date(year=(ts.year - n_years), month=ts.month, day=ts.day)
    return list(pd.date_range(ts_start, periods=(n_years * 12), freq="M"))[::-1]


def multiply_periods(df: pd.DataFrame, periods: List[np.datetime64]) -> pd.DataFrame:
    """Generate rows for the new periods."""
    df_append = df.copy()
    for i in range(len(periods)):
        try:
            df_append["calculation_date"] = periods[i]
            df_append["value"] = randomize_values(df_append["value"])
        except ValueError as e:
            print(e)
        df = df.append(df_append, ignore_index=True)
    return df


def main(path_to_df: str, n_years: int, n_kpi: int) -> pd.DataFrame:
    df = load_data(path_to_df)
    periods = generate_periods(df["calculation_date"].min(), n_years)
    df = multiply_kpis(df, n_kpi)
    df = multiply_periods(df, periods)
    df.to_csv(f"mock_{str(len(periods))}months_{str(n_kpi)}kpi.csv", index=False)
    print("Success, mock data created!")


arg_parser = argparse.ArgumentParser(
    description="".join(
        [
            "Multiply a set of input data by entering it's path",
            "and the number of years, and the number of kpi you wish.",
        ]
    )
)
arg_parser.add_argument("path", help="Path file with input data", type=str)
arg_parser.add_argument("n_years", help="Number of months to generate", type=str)
arg_parser.add_argument("n_kpi", help="Number of KPI IDs to generate", type=str)

# path_to_df = "./test/mock_input.csv"
# n_kpi = 10

if __name__ == "__main__":
    args = arg_parser.parse_args()
    path_to_df = args.path
    n_years = int(args.n_years)
    n_kpi = int(args.n_kpi)

    main(path_to_df, n_years, n_kpi)
