import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

import helpers
import data_dicts

st.title("KPI Sheet")

data_full = helpers.load_data("./tests/data/mock_preprocessed.csv")
data_actual = helpers.create_df_with_actual_period_only(data_full)

kpi_list, entity_list = helpers.get_filter_lists_full_flex(data_actual)

# TODO: Needs refactoring, I need period_id_values for plots -
# unless I return another df_full for plots
filter_result_period = st.sidebar.radio(
    "Choose Result Period:", options=["Single Month", "Year To Date (YTD)"]
)
filter_entity = st.multiselect(
    "Select entities:", options=entity_list, default=["all"]
)
filter_kpi = st.multiselect("Select KPIs:", options=kpi_list, default=["all"])
st.write("")

data = helpers.select_monthly_vs_ytd(data_actual, filter_result_period)
data = helpers.filter_for_display_full_flex(
    data, entity_list=filter_entity, kpi_list=filter_kpi
)

display_dict = helpers.create_dict_of_df_per_kpi(data, filter_kpi)

for k, v in display_dict.items():
    st.write(f"**{k}**")
    v = helpers.arrange_for_display_per_kpi(v)
    st.table(
        v.style.format({"Wert": "{:,.0f}", "Abw 12Mte": "{:0.1%}"}).applymap(
            helpers.set_bold_font,
            subset=pd.IndexSlice[v.index[v.index == 0], :],
        )
    )

# TODO: all of this should be outside of app module (including the imports)
# TODO: Check where and if "all" is removed from the kpi list
# it is not removed from the entity list...  -> throws an error if "all is alone"
print(filter_kpi)  # TODO: Remove
print(filter_entity)  # TODO: Remove
if (
    (len(filter_kpi) == 1)
    & (len(filter_entity) in range(1, 9))
    & (filter_entity != ["all"])
):  # TODO: I set this to 9 because of "all", the last could be removed maybe
    df_plot = data_full.loc[
        (data_full["kpi"].isin(filter_kpi))
        & (data_full["agg_level_value"].isin(filter_entity))
        & (data_full["period_id"].isin([1, 2]))  # TODO: Needs refactoring ...
    ].copy()
    df_plot = df_plot[["calculation_date", "agg_level_value", "value"]]
    df_plot.columns = ["Month", "Entity", "Value"]
    pio.templates.default = "plotly_white"
    fig = px.line(
        df_plot,
        x="Month",
        y="Value",
        color="Entity",
        color_discrete_sequence=list(data_dicts.colors_bcag.values()),
        title=filter_kpi[0],
    )
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x")
    st.plotly_chart(fig)
