import pandas as pd
import streamlit as st

import downloads
import helpers
import plots

st.title("KPI Sheet")


data_loaded = helpers.load_preprocessed_data("./data/preprocessed_results.csv")

date_list = helpers.get_filter_options_for_due_date(data_loaded, 24)
max_date = helpers.return_max_date_string(data_loaded)

filter_due_date = st.sidebar.selectbox("Auswahl Stichdatum:", options=date_list)
actual_date = helpers.return_actual_date_string(filter_due_date, max_date)

data_truncated_head = helpers.truncate_data_to_actual_date(data_loaded, actual_date)

n_years = helpers.calculate_max_n_years_available(data_truncated_head)

filter_result_dim = st.sidebar.selectbox(
    "Auswahl Resultatsdimension:",
    options=helpers.get_filter_options_for_result_dim(n_years),
)

data_truncated = helpers.truncate_data_n_years_back(
    data_truncated_head, actual_date, n_years
)

data_prepared = helpers.prepare_values_according_to_result_dim(
    data_truncated, filter_result_dim, actual_date
)

data_with_diff = helpers.calculate_diff_column(data_prepared)
data_actual = helpers.create_df_with_actual_period_only(data_with_diff, actual_date)


# SIDEBAR FILTER OPTIONS

mandant_options = helpers.get_filter_options_for_mandant_groups(data_actual)


# SIDEBAR

filter_mandant = st.sidebar.selectbox(
    "Auswahl Mandanten-Gruppe:", options=mandant_options
)
filter_product_dim = st.sidebar.radio(
    "Auswahl Produktsicht:", options=["Produkt", "Kartenprofil"]
)
filter_display_mode = st.sidebar.radio(
    "Auswahl Gruppierung für Anzeige:", options=["nach KPI", "nach Entität"]
)
st.sidebar.markdown("---")
st.sidebar.text("")
st.sidebar.text(f"Datenstand:\n {max_date}")


# UPPER FILTER OPTIONS MAIN PAGE

# data = helpers.select_monthly_vs_ytd(data_actual, filter_result_dim)
data = helpers.filter_for_sidebar_selections(
    data_actual,
    filter_display_mode=filter_display_mode,
    filter_product_dim=filter_product_dim,
    filter_mandant=filter_mandant,
)


# GENERATING OPTION FOR MAIN PAGE FILTERS

entity_options = helpers.get_filter_options_for_entities(data, filter_mandant)
kpi_options = helpers.get_filter_options_for_kpi(data)


# MAIN PAGE FILTERS

filter_entity = st.multiselect(
    "Select entities:", options=entity_options, default=["[alle]"]
)
filter_kpi = st.multiselect("Select KPIs:", options=kpi_options, default=["[alle]"])

st.write("")


# FILTERING DATA ACCORDING TO CHOICES

data = helpers.filter_for_entity_and_kpi(
    data,
    filter_entity=filter_entity,
    filter_kpi=filter_kpi,
    filter_mandant=filter_mandant,
)

# DISPLAY AND STYLING OF DATAFRAMES

if filter_display_mode.endswith("KPI"):
    display_dict = helpers.create_dict_of_df_for_each_kpi(data)
    for k, v in display_dict.items():
        st.write(f"**{k}**")
        v = helpers.arrange_for_display_per_kpi(v, filter_product_dim, filter_mandant)
        # v.set_index("Entität", inplace=True)  # hack to get rid of the index TODO
        st.table(
            v.style.format({"Wert": "{:,.0f}", "Abw VJ": "{:0.1%}"}).applymap(
                helpers.set_bold_font, subset=pd.IndexSlice[v.index[v.index == 0], :],
            )
        )
else:
    display_dict = helpers.create_dict_of_df_for_each_entity(data)
    for k, v in display_dict.items():
        st.write(f"**{k}**")
        v = helpers.arrange_for_display_per_entity(v)
        # v.set_index("KPI", inplace=True)  # hack to get rid of the index TODO
        st.table(v.style.format({"Wert": "{:,.0f}", "Abw VJ": "{:0.1%}"}))


# DISPLAY STANDARD PLOT IF CONDITIONS ARE MET

fig, df_plot = plots.main(data, data_truncated)
if fig is not None:
    st.plotly_chart(fig)


# EXCEL EXPORT
excel = st.button("Download Excel")

if excel:
    if fig is not None:
        download_data = df_plot
    else:
        download_data = data
    download_path = downloads.get_download_path()
    b64, href = downloads.export_excel(download_data, download_path)
    st.markdown(href, unsafe_allow_html=True)
