import streamlit as st

import downloads
import helpers
import plots
import SessionState

DATA_PATH = "./data/preprocessed_results.csv"


def main(data_path):
    """This is basically the full streamlit application code.
    It is run after a small basic set-up and the successfull user
    authentication (see below).
    """
    data_loaded = helpers.load_preprocessed_data(data_path)
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

    if filter_result_dim == "Monat":
        avg_bool = st.sidebar.checkbox("Ø-Werte pro aktive Konten", value=False)
    else:
        st.sidebar.text("[Ø-Werte nicht verfügbar]")
        avg_bool = False

    data_prepared_value = helpers.replace_monthly_values_with_avg(data_prepared, filter_result_dim, avg_bool)
    data_with_diff = helpers.calculate_diff_column(data_prepared_value)
    data_actual = helpers.create_df_with_actual_period_only(data_with_diff, actual_date)

    mandant_groups = helpers.get_filter_options_for_mandant_groups(data_actual)
    kpi_groups = helpers.get_filter_options_for_kpi_groups()

    # SIDEBAR

    filter_mandant = st.sidebar.selectbox(
        "Auswahl Mandanten-Gruppe:", options=mandant_groups
    )
    filter_kpi_groups = st.sidebar.selectbox("Auswahl KPI-Gruppe:", options=kpi_groups)
    filter_display_mode = st.sidebar.radio(
        "Auswahl Gruppierung für Anzeige:", options=["nach Entität", "nach KPI"]
    )

    # TODO: Filter for Product Dim is temporarily (?) disabled (fixed to "Produkt")
    filter_product_dim = "Produkt"
    # filter_product_dim = st.sidebar.radio(
    #     "Auswahl Produktsicht:", options=["Produkt", "Kartenprofil"]
    # )

    st.sidebar.markdown("---")
    st.sidebar.text("")
    st.sidebar.text(f"Datenstand:\n {max_date}")

    # UPPER FILTER OPTIONS MAIN PAGE

    data = helpers.filter_for_sidebar_selections_mandant(data_actual, filter_mandant)
    data = helpers.filter_for_sidebar_selections_kpi(data, filter_kpi_groups)

    # GENERATING OPTION FOR MAIN PAGE FILTERS

    entity_options = helpers.get_filter_options_for_entities(data)
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
    )

    # DISPLAY AND STYLING OF DATAFRAMES

    data_display = helpers.prepare_for_display(data, filter_display_mode)
    helpers.display_dataframes(
        data_display,
        filter_display_mode,
        filter_product_dim,
        filter_mandant,
        filter_entity,
        avg_bool
    )

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
            download_data = downloads.style_for_export_if_no_plot(
                data,
                filter_display_mode
            )

        download_path = downloads.get_download_path()
        b64, href = downloads.export_excel(download_data, download_path)
        st.markdown(href, unsafe_allow_html=True)


st.set_page_config(
    page_title="KPI Sheet BCAG",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("KPI Sheet BCAG")

# The following block adds User Authentication, see here:
# https://discuss.streamlit.io/t/user-authentication/612/8
session_state = SessionState.get(password="")
if session_state.password != "pwd123":
    pwd_placeholder = st.sidebar.empty()
    pwd = pwd_placeholder.text_input("Password:", value="", type="password")
    session_state.password = pwd
    if session_state.password == "pwd123":
        pwd_placeholder.empty()
        main(DATA_PATH)
    elif session_state.password == "":
        st.warning("Please enter a valid password.")
    else:
        st.error("The password you entered is incorrect.")
else:
    main(DATA_PATH)
