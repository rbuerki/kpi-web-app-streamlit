import pandas as pd
import streamlit as st
import helpers


st.title("KPI Sheet")

data_full = helpers.load_data("../data/test/mock_preprocessed.csv")
data_actual = helpers.create_df_with_actual_period_only(data_full)

kpi_list, entity_list = helpers.get_filter_lists_full_flex(data_actual)

filter_result_period = st.sidebar.radio(
    "Choose Result Period:", options=["Month", "Year To Date (YTD)"]
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

display_dict = helpers.create_dict_of_df_per_kpi(data)

for k, v in display_dict.items():
    st.write(f"**{k}**")
    v = helpers.arrange_for_display_per_kpi(v)
    st.table(
        v.style.format({"Wert": "{:,.0f}", "Abw 12Mte": "{:0.1%}"}).applymap(
            helpers.set_bold_font,
            subset=pd.IndexSlice[v.index[v.index == 0], :],
        )
    )
