import datetime as dt
from typing import List, Tuple

import pandas as pd
import plotly.express as px
import plotly.io as pio

import data_dicts

pio.templates.default = "plotly_white"


def get_dimensions_for_plot(data: pd.DataFrame) -> Tuple[List, List]:
    """TODO write docstring"""
    kpi_for_plot = list(data["kpi_name"].unique())
    entities_for_plot = list(data["agg_level_value"].unique())
    agg_level_id_for_plot = list(data["agg_level_id"].unique())
    return kpi_for_plot, entities_for_plot, agg_level_id_for_plot


def check_if_plot(kpi_for_plot: List, entities_for_plot: List) -> bool:
    """TODO write docstring"""
    if (len(kpi_for_plot) in range(1, 2)) & (len(entities_for_plot) in range(1, 9)):
        return True
    else:
        return False


def create_df_plot(
    df: pd.DataFrame,
    kpi_for_plot: List,
    entities_for_plot: List,
    agg_level_id_for_plot: List,
) -> pd.DataFrame:
    """Return a dataframe with friendly named columns for plotting the
    monthly (!) values for the past 12 months from the selected actual
    date for the selected KPI and entities only. For this we have to
    work with the original "truncated" dataframe to have all the necessary
    period values. (Note: The length of the x-Axis could be changed.)
    """
    months_set = set(list(df["calculation_date"].values))
    top_months_13 = sorted(list(months_set), reverse=True)[:13]
    df_plot = df.loc[
        (df["kpi_name"].isin(kpi_for_plot))
        & (df["agg_level_value"].isin(entities_for_plot))
        & (df["agg_level_id"].isin(agg_level_id_for_plot))
        & (df["period_id"].isin([1, 2]))
        & (df["calculation_date"].isin(top_months_13))
    ].copy()
    df_plot = df_plot[["calculation_date", "agg_level_value", "value"]]
    df_plot.columns = ["Monat", "Entität", "Wert"]

    # Add a 'growth' column
    df_plot = _add_growth_col(df_plot)
    return df_plot


def _add_growth_col(df_plot: pd.DataFrame) -> pd.DataFrame:
    """Return df_plot with a new column for pct change from period to
    period. Trick is to calculate this for every entity separately for
    not to have a 'spill over' from one entity's last month to another
    entity's first month. This is called within `create_df_plot`.
    """
    if df_plot["Entität"].nunique() == 1:
        df_plot["Abw VM"] = df_plot["Wert"].pct_change()
    else:
        df_plot_list = []
        for entity in df_plot["Entität"].unique():
            df_temp = df_plot.loc[df_plot["Entität"] == entity].copy()
            df_temp["Abw VM"] = df_temp["Wert"].pct_change()
            df_plot_list.append(df_temp)
        df_plot = pd.concat(df_plot_list)
    return df_plot


def create_plotly_figure(df_plot: pd.DataFrame, kpi_for_plot: List):
    """TODO write docstring"""
    # Set date to first day of month for better alignment of xaxis ticks
    df_plot["Monat"] = df_plot["Monat"].apply(lambda x: dt.date(x.year, x.month, 1))

    fig = px.line(
        df_plot,
        x="Monat",
        y="Wert",
        text="Abw VM",
        color="Entität",
        color_discrete_sequence=list(data_dicts.COLORS_BCAG.values()),
        title=f"{kpi_for_plot[0]} (monatliche Entwicklung)",
    )
    fig.update_traces(
        mode="markers+lines", hovertemplate="<b>%{y:,.3s}</b> <br>%{text:,.1%}"
    )
    fig.update_layout(hovermode="x", xaxis_tickformat="%b %Y")
    return fig


def main(data: pd.DataFrame, data_truncated: pd.DataFrame):
    kpi_for_plot, entities_for_plot, agg_level_id_for_plot = get_dimensions_for_plot(
        data
    )
    if check_if_plot(kpi_for_plot, entities_for_plot):
        df_plot = create_df_plot(
            data_truncated, kpi_for_plot, entities_for_plot, agg_level_id_for_plot
        )
        fig = create_plotly_figure(df_plot, kpi_for_plot)
        return fig, df_plot
    else:
        return None, None
