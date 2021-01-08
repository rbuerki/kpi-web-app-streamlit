import datetime as dt
from typing import List, Tuple, Union

import pandas as pd
import plotly.express as px
import plotly.io as pio

import data_dicts
from helpers import logging_runtime


pio.templates.default = "plotly_white"


@logging_runtime
def get_dimensions_for_plot(data: pd.DataFrame) -> Tuple[List, List]:
    """Return the unique values of kpis, entity names and entity ids
    in the actual data selected by the user.
    """
    kpi_for_plot = list(data["kpi_name"].unique())
    entities_for_plot = list(data["product_name"].unique())
    level_for_plot = list(data["level"].unique())
    return kpi_for_plot, entities_for_plot, level_for_plot


@logging_runtime
def check_if_plot(kpi_for_plot: List, entities_for_plot: List) -> Union[int, bool]:
    """Check if the numer of unique kpi and entities in the selected
    data matches the conditions to create a plot and return a flag.
    - Flag 1: 1 kpi for up to 8 entities
    - Flag 2: 2 kpi for one entity
    - Flag False: plot process is aborted"""

    if (len(kpi_for_plot) == 1) & (len(entities_for_plot) in range(1, 9)):
        return 1
    elif (len(kpi_for_plot) == 2) & (len(entities_for_plot) == 1):
        return 2
    else:
        return False


@logging_runtime
def check_if_facet_or_not(kpi_for_plot: List) -> bool:
    """Only if Flag 2 is activated above, we check if the two KPI are
    from the same KPI group (-> their names start with the same word).
    If yes, we plot on the same y-axis, if not we create a facet plot.
    """
    return kpi_for_plot[0].split()[0] == kpi_for_plot[1].split()[0]


@logging_runtime
def create_df_plot(
    df: pd.DataFrame,
    kpi_for_plot: List,
    entities_for_plot: List,
    level_for_plot: List,
) -> pd.DataFrame:
    """Return a dataframe with friendly named columns for plotting the
    monthly (!) values for the past 12 months from the selected actual
    date for the selected KPI and entities only. For this we have to
    work with the original "truncated" dataframe to have all the necessary
    period values. (Note: The length of the x-Axis could be changed.)
    This is the df that can be downloaded by the user.
    """
    months_set = set(list(df["calculation_date"].values))
    top_months_13 = sorted(list(months_set), reverse=True)[:13]
    df_plot = df.loc[
        (df["kpi_name"].isin(kpi_for_plot))
        & (df["product_name"].isin(entities_for_plot))
        & (df["level"].isin(level_for_plot))
        & (df["period_id"].isin([1, 2]))
        & (df["calculation_date"].isin(top_months_13))
    ].copy()
    df_plot = df_plot[["kpi_name", "calculation_date", "product_name", "value"]]
    df_plot.columns = ["KPI", "Monat", "Entität", "Wert"]

    # Add a 'growth' column
    df_plot = _add_growth_col(df_plot)
    return df_plot


@logging_runtime
def _add_growth_col(df_plot: pd.DataFrame) -> pd.DataFrame:
    """Return df_plot with a new column for pct change from period to
    period. Trick is to calculate this for every entity separately for
    not to have a 'spill over' from one entity's last month to another
    entity's first month. This is called within `create_df_plot`.
    """
    df_plot = df_plot.assign(Abw_VM=df_plot.groupby(["KPI", "Entität"])
                             ["Wert"].transform("pct_change")
                             )
    df_plot = df_plot.rename(columns={"Abw_VM": "Abw VM"})
    return df_plot


@logging_runtime
def create_plotly_figure_with_one_kpi(df_plot: pd.DataFrame, kpi_for_plot: List):
    """Return a line plot figure."""
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


@logging_runtime
def create_plotly_figure_with_two_kpis(df_plot: pd.DataFrame, kpi_for_plot: List):
    """Return a line plot figure. Version with 2 kpi from the same
    kpi-family on a shared y-axis.
    """
    # Set date to first day of month for better alignment of xaxis ticks
    df_plot["Monat"] = df_plot["Monat"].apply(lambda x: dt.date(x.year, x.month, 1))
    fig = px.line(
        df_plot,
        x="Monat",
        y="Wert",
        text="Abw VM",
        color="KPI",
        color_discrete_sequence=list(data_dicts.COLORS_BCAG.values()),
        title="KPI-Vergleich (monatliche Entwicklung)",
    )
    fig.update_traces(
        mode="markers+lines", hovertemplate="<b>%{y:,.3s}</b> <br>%{text:,.1%}"
    )
    fig.update_layout(hovermode="x", xaxis_tickformat="%b %Y")
    return fig


@logging_runtime
def create_plotly_figure_with_two_kpis_facet(df_plot: pd.DataFrame, kpi_for_plot: List):
    """Return a line plot figure. Version with 2 kpi from different
    kpi-families in a 2-row facet plot with independent y-axes.
    """
    # Set date to first day of month for better alignment of xaxis ticks
    df_plot["Monat"] = df_plot["Monat"].apply(lambda x: dt.date(x.year, x.month, 1))

    fig = px.line(
        df_plot,
        x="Monat",
        y="Wert",
        text="Abw VM",
        facet_row="KPI",
        facet_row_spacing=0.1,
        color_discrete_sequence=list(data_dicts.COLORS_BCAG.values()),
        title="KPI-Vergleich (monatliche Entwicklung)",
        height=600,
    )
    fig.update_traces(
        mode="markers+lines", hovertemplate="<b>%{y:,.3s}</b> <br>%{text:,.1%}"
    )
    fig.update_layout(hovermode="x", xaxis_tickformat="%b %Y")
    # Make yaxes independent
    fig.update_yaxes(matches=None, )

    return fig


def main(data: pd.DataFrame, data_truncated: pd.DataFrame):
    kpi_for_plot, entities_for_plot, level_for_plot = get_dimensions_for_plot(
        data
    )
    check_result = check_if_plot(kpi_for_plot, entities_for_plot)
    if check_result == 1:
        df_plot = create_df_plot(
            data_truncated, kpi_for_plot, entities_for_plot, level_for_plot
        )
        fig = create_plotly_figure_with_one_kpi(df_plot, kpi_for_plot)
        return fig, df_plot

    elif check_result == 2:
        df_plot = create_df_plot(
            data_truncated, kpi_for_plot, entities_for_plot, level_for_plot
        )
        if check_if_facet_or_not(kpi_for_plot):
            fig = create_plotly_figure_with_two_kpis(df_plot, kpi_for_plot)
        else:
            fig = create_plotly_figure_with_two_kpis_facet(df_plot, kpi_for_plot)
        return fig, df_plot

    else:
        return None, None
